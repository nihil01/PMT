package world.horosho.pcapServer.server_status;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Properties;

public class Status {

    public static void registerServerBootTime() {
        if (Files.exists(Paths.get("src/main/resources/static/boot.properties"))){
            LocalDateTime timestamp = LocalDateTime.now();
            String out = String.format("booted=%s", timestamp);
            try(FileOutputStream fos = new FileOutputStream("src/main/resources/static/boot.properties")){
                fos.write(out.getBytes(StandardCharsets.UTF_8));
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public static Properties getServerBootTime() {
        if (Files.exists(Paths.get("src/main/resources/static/boot.properties"))){
            try(InputStream fis = new FileInputStream("src/main/resources/static/boot.properties")){
                Properties prop = new Properties();
                prop.load(fis);
                return prop;
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        return null;
    }
}
