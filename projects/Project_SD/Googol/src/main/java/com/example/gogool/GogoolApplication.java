package com.example.gogool;

import com.example.gogool.service.Downloader;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

import java.io.IOException;

/**
 * Classe principal da aplicação Spring Boot.
 *
 * Esta classe contém o método main que inicia a aplicação Spring Boot.
 */
@SpringBootApplication
public class GogoolApplication {

	/**
	 * Método principal que inicia a aplicação Spring Boot.
	 *
	 * @param args Argumentos da linha de comando
	 */
	public static void main(String[] args) {
		// Start the Spring Boot application
		ConfigurableApplicationContext context = SpringApplication.run(GogoolApplication.class, args);
	}
}