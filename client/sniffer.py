#Executable python script that sniffs a network interface and saves data in .pcapng file,
# then data is send to local server for analyzing
import random

import queue
import subprocess
import datetime
import tempfile
import os
from scapy.all import *
import platform
import glob
import requests

###########################
#IP ADDRESS OF LOCAL SERVER
local_server_ip: str = "localhost"
###########################

#hostname
host_name: str = platform.node() or f"unknown_host_{random.seed(213).random()}"

#tempdir
tempdirectory: str = os.path.join(tempfile.gettempdir(), "packet_sniffer_dumps")

#queue for awaiting files
files: list[tuple[str, tuple[str, bytes], str]] = []

#returns active interfaces
def initialize_active_network_interfaces() -> list[str]:
    try:
        out = subprocess.Popen(["netsh", "interface", "show", "interface"], shell=True, stdout=subprocess.PIPE)
        interfaces = out.stdout.read().decode().split("\n")

        interfaces_list = list()
        for interface in interfaces[3:len(interfaces) - 2]:
            intermediate_data = interface.split()

            if intermediate_data[0].lower() == "enabled" and intermediate_data[1].lower() == "connected":
                interfaces_list.append(" ".join(intermediate_data[3:]))

        return interfaces_list
    except subprocess.SubprocessError:
        print("Could not run netsh interface show interface")


#sniffs until counter reached
def sniff_network_interface(interfaces: list[str], output: str) -> None:
    if len(interfaces) > 0 and output is not None:
        packets = sniff(iface=interfaces, count=500)
        wrpcapng(output, packets)
        #appending to resulting list
        files.append(('file', (output.replace("\\", "/").split("/").pop(),
                               open(output, 'rb'), "application/octet-stream")))
        return

#generates output file
def get_output_destination():

    if not os.path.exists(tempdirectory):
        os.makedirs(tempdirectory)

    fileName: str = f"dump_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcapng"
    filePath: str = os.path.join(tempdirectory, fileName)
    return filePath


#clear temp tempdirectory: as script has been initialized
def clear_temp_directory():
    if os.path.exists(tempdirectory):
        try:
            files = glob.glob(os.path.join(tempdirectory, "*"))
            for file in files:
                os.remove(file)
        except Exception as e:
            print(e)

#sends multiple files via form data
def send_files_to_server():
    try:
        payload = {"hostname": host_name}
        request = requests.post(url=f"http://{local_server_ip}:8080/file", files=files, data=payload)
        print(request.text)
    except requests.exceptions.ConnectionError as e:
        print(e)



if __name__ == "__main__":
    try:
        clear_temp_directory()

        while True:
            dump_path: str = get_output_destination()
            interfaces: list[str] = initialize_active_network_interfaces()
            print("### Started sniffing packets ###" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            sniff_network_interface(interfaces, dump_path)
            print("### Finished sniffing packets ###" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

            if len(files) == 5:
                send_files_to_server()
                files.clear()
                clear_temp_directory()

    except KeyboardInterrupt:
        print("\nClosing script")
        sys.exit(0)
