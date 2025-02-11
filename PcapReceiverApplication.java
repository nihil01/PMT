package world.horosho.pcapServer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import world.horosho.pcapServer.server_status.Status;

@SpringBootApplication
public class PcapReceiverApplication {

	public static void main(String[] args) {
		SpringApplication.run(PcapReceiverApplication.class, args);
		Status.registerServerBootTime();
	}

}
