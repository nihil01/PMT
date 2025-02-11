package world.horosho.pcapServer.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import world.horosho.pcapServer.server_status.Status;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Objects;
import java.util.Properties;

@RestController
public class CommonController {
    @Value("${spring.file_dump.path}")
    private String FILE_STORAGE_PATH;

    @GetMapping("/status")
    public ResponseEntity<String> status() {
        Properties props = Status.getServerBootTime();

        if (props != null){
            return ResponseEntity.ok(props.getProperty("booted"));
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
    }

    @GetMapping("/shutdown")
    public void shutdownServer() {
        new ResponseEntity<>(HttpStatus.OK);
        System.exit(0);
    }

    @PostMapping("/file")
    public ResponseEntity<String> receiveFile(
            @RequestParam("file") MultipartFile[] files,
            @RequestParam("hostname") String hostname)
    {
        try {

            for (MultipartFile file : files) {


                if (file == null || hostname == null || file.isEmpty() || hostname.isEmpty()) {
                    return new ResponseEntity<>("One of files is empty or hostname not specified. Aborting request.",
                            HttpStatus.BAD_REQUEST);
                }

                System.out.println(file.getOriginalFilename());
                System.out.println(file.getContentType());

                if (Objects.requireNonNull(file.getContentType())
                        .equalsIgnoreCase("application/octet-stream")) {

                    String fileName = file.getOriginalFilename();
                    Path dirPath = Paths.get(FILE_STORAGE_PATH, hostname);
                    System.out.println(dirPath.toAbsolutePath());

                    if (!Files.exists(dirPath)) {
                        Files.createDirectory(dirPath);
                    }

                    System.out.println(Paths.get(FILE_STORAGE_PATH, hostname, fileName));
                    Files.write(Paths.get(FILE_STORAGE_PATH, hostname, fileName), file.getBytes());

                }
            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
            throw new RuntimeException(e);
        }
        return new ResponseEntity<>("Files have been saved", HttpStatus.OK);
    }

}
