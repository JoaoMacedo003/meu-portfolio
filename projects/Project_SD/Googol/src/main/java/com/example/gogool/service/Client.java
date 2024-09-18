package com.example.gogool.service;

import com.example.gogool.rmi.RMIGateway;

import java.io.IOException;
import java.net.Socket;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.util.Map;
import java.util.Scanner;
import java.util.List;
import java.util.stream.IntStream;

/**
 * A classe Client implementa um cliente que se conecta a um servidor via socket e RMI para realizar operações
 * como adicionar URLs, buscar, visualizar estatísticas, entre outras. Esta classe gere a interação do user
 * com o sistema, permitindo que ele realize login ou registro antes de prosseguir com as operações disponíveis.
 */
public class Client {

    private RMIGateway gateway;  // Representa o gateway para comunicação RMI.
    private final Scanner scanner = new Scanner(System.in);    // Scanner para leitura dos comandos do user.

    /**
     * Construtor da classe Client que inicia a conexão com o servidor via socket e RMI.
     */
    public Client(RMIGateway gateway) {
        this.gateway = gateway;
    }

    /**
     * Classe responsável por inicializar o cliente e gerenciar a interação do usuário.
     */
    public static void main(String[] args) {
        try {
            String rmiHost = "192.168.1.6"; // Substitua "IP_DO_GATEWAY_RMI" pelo endereço IP real
            RMIGateway gateway = (RMIGateway) LocateRegistry.getRegistry(rmiHost, 5000).lookup("Gateway");
            System.out.println("Connected to Gateway at " + rmiHost);

            Client client = new Client(gateway);
            client.run();
        } catch (NotBoundException | IOException e) {
            System.out.println("Failed to connect to the server at the specified address.");
            e.printStackTrace();
        }
    }

    /**
     * Executa o menu principal para interação do user com o sistema.
     */
    public void run() {
        try {
            boolean isLoggedIn = loginOrRegister();

            while (!isLoggedIn) {
                System.out.println("You must log in or register to use the application.");
                isLoggedIn = loginOrRegister();
            }

            boolean exit = false;
            while (!exit) {
                System.out.println("\n>==================== Googol ====================<\n");
                System.out.println("Escolha uma operação:");
                System.out.println("1. Introduzir um URL");
                System.out.println("2. Pesquisar");
                System.out.println("3. Consultar lista de páginas com ligação para uma página introduzida");
                System.out.println("4. Stats | Página de administração");
                System.out.println("5. Sair");
                System.out.print("Opção: ");

                String choice = scanner.nextLine();

                switch (choice) {
                    case "1":
                        addUrl();
                        break;
                    case "2":
                        search();
                        break;
                    case "3":
                        searchUrl();
                        break;
                    case "4":
                        showStats();
                        break;
                    case "5":
                        System.out.println("Programa terminado\n");
                        exit = true;
                        break;
                    default:
                        System.out.println("Opção inválida. Tente novamente.");
                        break;
                }
            }
        } catch (Exception e) {
            System.out.println("Ocorreu um erro. A terminar...");
        }
    }

    /**
     * Solicita ao user que insira um URL e envia esse URL ao Downloader através do Gateway.
     *
     * @throws IOException Se ocorrer um erro de entrada/saída ao enviar o URL.
     */
    private void addUrl() throws RemoteException {
        System.out.print("Insira o URL: ");
        String url = scanner.nextLine();
        String response = gateway.addUrl(url);
        System.out.println(response);
    }

    /**
     * Permite que o user realize uma pesquisa por um termo ou conjunto de termos de pesquisa e mostre os resultados.
     *
     * @throws Exception Se ocorrer um erro durante a pesquisa.
     */
    private void search() throws Exception {
        System.out.print("Pesquisa: ");
        String searchTerm = scanner.nextLine();
        List<String> result = gateway.search(searchTerm);
        int count = 0;
        int countPaginas = 0;
        for (String res : result) {
            if (count % 10 == 0 && count != 0) {
                countPaginas++;
                System.out.println("Pressione qualquer tecla para continuar ou digite 'back' para sair");
                String input = scanner.nextLine();
                // Verifica se o usuário deseja sair digitando 'back'
                if (input.trim().equalsIgnoreCase("back")) {
                    System.out.println("Saindo da pesquisa...");
                    break; // Sai do loop se o usuário digitar 'back'
                }
            }
            if (countPaginas == 10){
                break;
            }
            System.out.println(res + "\n");
            count++;
        }
    }

    /**
     * Solicita ao user que introduza um URL e realiza uma pesquisa por páginas com ligação a esse URL.
     *
     * @throws Exception Se ocorrer um erro durante a pesquisa.
     */
    private void searchUrl() throws Exception {
        System.out.print("Introduza o URL: ");
        String url = scanner.nextLine();
        String result = gateway.search2(url);
        System.out.println(result);
    }

    /**
     * Gere o processo de login ou registo do user, solicitando as suas credenciais e validando-as
     * ou registando um novo user no sistema.
     *
     * @return {@code true} se o login for bem sucedido, {@code false} caso contrário.
     * @throws Exception Se ocorrer um erro durante o processo de login ou registo.
     */
    private boolean loginOrRegister() throws Exception {
        System.out.println("1. Login");
        System.out.println("2. Register");
        String choice = scanner.nextLine();

        System.out.print("Username: ");
        String username = scanner.nextLine();
        System.out.print("Password: ");
        String password = scanner.nextLine();

        if ("1".equals(choice)) {
            String response = gateway.logIn(username, password);
            System.out.println(response);
            return "Login successful".equals(response);
        } else if ("2".equals(choice)) {
            String response = gateway.registerUser(username, password);
            System.out.println(response);
            return false;
        } else {
            System.out.println("Invalid choice.");
            return false;
        }
    }

    /**
     * Mostra as estatísticas relacionadas às pesquisas e aos tempos de resposta do sistema, além de listar os "barrels"
     * ativos.
     *
     * @throws RemoteException Se ocorrer um erro na comunicação RMI ao obter as estatísticas.
     */
    private void showStats() throws RemoteException {
        System.out.println("Stats | Página de administração");
        System.out.println("Top Searches:");

        List<String> topSearches = gateway.getTopSearches(); // Obtenha a lista de top pesquisas
        if (!topSearches.isEmpty()) { // Verifica se há mais de um elemento na lista
            IntStream.range(0, topSearches.size()) // Gera um stream de inteiros do 1 até o tamanho da lista - 1
                    .forEach(i -> System.out.println((i + 1) + " -> " + topSearches.get(i))); // Imprime o índice e o elemento correspondente
        }

        Map<String, Double> averageTimes = gateway.getAverageResponseTimes();
        System.out.println("Average Response Times:");
        averageTimes.forEach((barrelId, time) -> System.out.println("Barrel ID: " + barrelId + ", Time: " + time));

        List<String> barrels = gateway.getActiveBarrels();
        System.out.println("Active Barrels:");
        barrels.forEach(barrelId -> System.out.println("Barrel ID: " + barrelId));
    }

}
