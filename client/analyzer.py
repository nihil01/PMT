from collections import Counter
from scapy.all import *
from scapy.layers import *
import datetime

import sys
import cryptography
import re
import io

import scapy.layers.tls.all

load_layer("tls")

def process_dns(pkt, dnsCollection: Counter):
    try:
        #Query DNS
        if DNSQR in pkt and pkt.dport == 53:
            dnsCollection.update([pkt[DNSQR].qname.decode('utf-8')])
        #Response DNS
        elif DNSRR in pkt and pkt.sport == 53:
            dnsCollection.update([pkt[DNSRR].rrname.decode('utf-8')])

    except IndexError:
        print("Bad packet!")

def process_tls(pkt, tlsCollection: Counter):
    try:
        if TLS in pkt:
            backup = sys.stdout
            stringBuffer = io.StringIO()
            sys.stdout = stringBuffer
            pkt.show()
            sys.stdout = backup
            packets = stringBuffer.getvalue()

            # retrieving hostname from segment (SNI extension TLS 1.2+)
            sni_match = re.search(r"servernames= \[(.*)\]", packets)
            if sni_match and len(sni_match.group(1).strip()) > 0:
                tlsCollection.update([sni_match.group(1)])
    except IndexError:
        print("Bad packet!")

def process_ipv4(pkt, ipv4Collection: Counter):
    try:
       if IP in pkt:
           ip: str = pkt[IP].dst
           #10.0.0.0 - 10.255.255.255
           #172.16.0.0 - 172.31.255.255
           #192.168.0.0 - 192.168.255.255
           if (ip.startswith("10") or re.match("172\.(1[6-9]|2[0-9]|3[0-1])\.", ip)
                   or ip.startswith("192.168")):
               return
           else:
               ipv4Collection.update([ip])
    except IndexError:
        print("Bad packet!")

def main():
    filePath: str = "D:\logs\dump.pcapng"

    packets = rdpcap(filePath)

    #declaring counters
    tlsHostnameCounter = Counter()
    dnsHostnameCounter = Counter()
    ipv4Counter = Counter()

    for packet in packets:
        try:
            if packet.haslayer(TLS):
                process_tls(packet, tlsHostnameCounter)
            elif packet.haslayer(DNS):
                process_dns(packet, dnsHostnameCounter)

            process_ipv4(packet, ipv4Counter)

        except IndexError:
            print("Bad packet!")


    print(ipv4Counter.most_common())
    print(dnsHostnameCounter.most_common())
    print(tlsHostnameCounter.most_common())
    print("WHOIS IP")

    #populating with data from whois databases
    for ip in ipv4Counter.keys():
        print(ip)
        data = str(whois(ip)).strip().split("\\n")
        print(data[11:14])
        print(data[19:20])
        print("\n")

if __name__ == "__main__":
    main()
