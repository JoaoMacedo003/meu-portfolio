package com.example.gogool.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import com.example.gogool.model.CrawledData;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;
import java.io.EOFException;

/**
 * A classe Downloader é responsável por retirar conteúdo da web,
 * analisar documentos HTML e gerenciar uma fila de URLs para download.
 * Utiliza a biblioteca Jsoup para a análise dos documentos HTML.
 */
public class Downloader {

    public InetAddress downloaderMulticastGroup;    // Endereço IP do grupo para comunicação de rede.
    public int downloaderMulticastPort; // Define a porta de comunicação do servidor.
    public String downloaderHost;
    private int downloaderPort;   // Define a porta de comunicação do cliente.
    public LinkedBlockingDeque<String> urlQueue; // Fila bloqueante para armazenar URLs que precisam ser baixadas.


    /**
     * Construtor para Downloader.
     */
    public Downloader(LinkedBlockingDeque<String> urlQueue) {
        this.urlQueue = urlQueue;
        loadConfig();
    }

    /**
     * O ponto de entrada do programa. Cria uma instância do Downloader e inicia o processo de download.
     *
     * @param args Argumentos da linha de comando. Não são utilizados neste método.
     */
    public static void main(String[] args) {
        try {
            LinkedBlockingDeque<String> urlQueue = new LinkedBlockingDeque<>();
            Downloader downloader = new Downloader(urlQueue);
            downloader.start();
        } catch (UnknownHostException e) {
            System.out.println("Erro: Endereço de host desconhecido.");
        }
    }

    private void loadConfig() {
        Properties properties = new Properties();
        try (InputStream input = getClass().getClassLoader().getResourceAsStream("config.txt")) {
            if (input == null) {
                System.out.println("Sorry, unable to find config.txt");
                return;
            }
            // load a properties file from class path, inside static method
            properties.load(input);

            // get the property value and assign it to the fields
            this.downloaderHost = properties.getProperty("downloader.host");
            this.downloaderPort = Integer.parseInt(properties.getProperty("downloader.port"));
            String downloaderMulticastGroup = properties.getProperty("downloader.multicast.group");
            this.downloaderMulticastGroup = InetAddress.getByName(downloaderMulticastGroup);
            this.downloaderMulticastPort = Integer.parseInt(properties.getProperty("downloader.multicast.port"));



        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    /**
     * Inicia o servidor para aceitar conexões de clientes e processar URLs para download.
     * Utiliza um ExecutorService com um pool fixo de threads para executar tarefas de download e crawling.
     */
    public void start() throws UnknownHostException {
        // Cria um pool de threads para execução dos downloaders.
        ExecutorService executorDownloaders = Executors.newFixedThreadPool(2);

        InetAddress specificAddress = InetAddress.getByName(downloaderHost); // Substitua pelo endereço IP do gateway
        try (ServerSocket listenSocket = new ServerSocket(downloaderPort, 50, specificAddress)) {
            System.out.println("SOCKET = " + listenSocket + " IP = " + specificAddress.getHostAddress() + " PORT = " + downloaderPort);
            while (true) {
                Socket clientSocket = listenSocket.accept();    // Aguarda e aceita uma conexão de cliente.
                new TCP(clientSocket, urlQueue).start(); // Inicia uma nova thread para tratar a conexão TCP.

                for (int i = 0; i < 2; i++) {
                    executorDownloaders.execute(new WebCrawlerer(urlQueue, downloaderMulticastGroup, downloaderMulticastPort));
                    System.out.println("Downloader " + i + " initialized");
                }
            }
        } catch (IOException e) {
            System.out.println("Listen: " + e.getMessage());
        } finally {
            // Tenta encerrar corretamente o ExecutorService ao final da execução.
            executorDownloaders.shutdown();
            try {
                if (!executorDownloaders.awaitTermination(60, TimeUnit.SECONDS)) {
                    executorDownloaders.shutdownNow();
                }
            } catch (InterruptedException ie) {
                executorDownloaders.shutdownNow();
            }
        }
    }

    /**
     * Classe TCP estende Thread, responsável por gerir a comunicação via socket TCP.
     * Recebe URLs como strings através do socket e as adiciona em uma fila de bloqueio para processamento futuro.
     */
    public static class TCP extends Thread {

        private final DataInputStream in; // Stream de entrada para ler dados do socket.
        private final BlockingQueue<String> urlQueue; // Fila de bloqueio para armazenar URLs recebidas.
        private final Socket socket;  // Socket para comunicação com o cliente.

        /**
         * Constrói uma instância da classe TCP.
         *
         * @param clientSocket O socket do cliente para comunicação.
         * @param list_url Uma fila de bloqueio para armazenar URLs recebidas através do socket.
         * @throws IOException Se ocorrer um erro ao obter o stream de entrada do socket.
         */
        public TCP(Socket clientSocket, BlockingQueue<String> list_url) throws IOException {
            this.socket = clientSocket;
            this.in = new DataInputStream(clientSocket.getInputStream());
            this.urlQueue = list_url;
        }

        /**
         * Executa a thread, lendo strings (URLs) do stream de entrada e adicionando-as à fila de bloqueio.
         * Continua a ler e adicionando URLs até que a thread seja interrompida ou o socket seja fechado.
         */
        @Override
        public void run() {
            try {
                while (!Thread.currentThread().isInterrupted() && !socket.isClosed()) {
                    String received = in.readUTF();
                    if (!received.isEmpty()) {
                        // Oferece a URL recebida ao início da fila.
                        ((LinkedBlockingDeque<String>) urlQueue).offerFirst(received);
                        System.out.println("TCP Receive = " + received);
                    }
                }
            } catch (EOFException e) {
                System.out.println("Client disconnected: " + e.getMessage());
            } catch (IOException e) {
                if (!Thread.interrupted()) {
                    System.out.println("IOException: " + e.getMessage());
                }
            } finally {
                try {
                    in.close();
                    socket.close();
                } catch (IOException e) {
                    System.out.println("Error closing TCP resources: " + e.getMessage());
                }
            }
        }
    }

    /**
     * Classe WebCrawlerer implementa a interface Runnable para permitir a execução de operações de crawling em threads separadas.
     * Responsável por retirar URLs da fila de bloqueio fornecida e processá-las para extrair dados relevantes.
     */
    private class WebCrawlerer implements Runnable {
        private final BlockingQueue<String> urlQueue;  // Use BlockingQueue instead of Vector
        private final InetAddress downloaderMulticastGroup; // Endereço IP do grupo para comunicação de rede
        private final int downloaderMulticastPort; // Porta para comunicação de rede

        /**
         * Constrói uma instância de WebCrawlerer com uma fila de bloqueio para URLs.
         *
         * @param list_url A fila de bloqueio de URLs para processamento.
         * @param downloaderMulticastGroup Endereço IP do grupo para comunicação de rede.
         * @param downloaderMulticastPort Porta para comunicação de rede.
         */
        public WebCrawlerer(BlockingQueue<String> list_url, InetAddress downloaderMulticastGroup, int downloaderMulticastPort) {
            this.urlQueue = list_url;
            this.downloaderMulticastGroup = downloaderMulticastGroup;
            this.downloaderMulticastPort = downloaderMulticastPort;
        }

        /**
         * Executa a tarefa de crawling: retira URLs da fila de bloqueio e processa cada um deles.
         */
        @Override
        public void run() {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    String url = urlQueue.take(); // Espera e retira uma URL da fila.
                    WebCrawler(url);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    System.out.println("Erro...");
                }
            }
        }

        /**
         * Realiza o crawling de uma URL específica, extraindo informações como título, palavras-chave e links.
         *
         * @param strUrl A URL a ser processada.
         */
        public void WebCrawler(String strUrl) {
            try {
                ArrayList<String> words = new ArrayList<>();

                if (!strUrl.startsWith("https://")) {
                    strUrl = "https://".concat(strUrl);
                }

                Document doc = Jsoup.connect(strUrl).get();

                String title = doc.title();
                StringTokenizer tokens = new StringTokenizer(doc.text());

                CrawledData crawledData = new CrawledData(strUrl, title);

                int countTokens = 0;
                StringBuilder quote = new StringBuilder();
                while (tokens.hasMoreElements()) {
                    String token = tokens.nextToken().toLowerCase();
                    words.add(token);
                    if (countTokens < 10) {
                        quote.append(token).append(" ");
                        countTokens++;
                    }
                }

                crawledData.setQuote(quote.toString());
                crawledData.setWords(words);

                Elements links = doc.select("a[href]");
                ArrayList<String> Links = new ArrayList<>();
                for (Element link : links) {
                    String absUrl = link.attr("abs:href"); // Obtem o URL absoluto
                    if (!absUrl.isEmpty()) { // Verifica se o URL absoluto não está vazio
                        Links.add(absUrl); // Adiciona o URL absoluto à lista de Links
                    }
                    urlQueue.add(link.attr("abs:href"));
                }
                crawledData.setLinks(Links);

                System.out.println(strUrl);

                sendMulticast(crawledData);
            } catch (IOException e) {
                // Trata exceções de IO, incluindo problemas de conexão ou formato de URL inválido.
            } catch (IllegalArgumentException | NullPointerException | IndexOutOfBoundsException ignored) {
            }
        }

        /**
         * Envia os dados extraídos de uma página web via multicast para um grupo de endereços IP.
         * Os dados incluem a URL da página, o título, uma citação destacada, uma lista de palavras-chave e uma lista de links encontrados.
         *
         * @param crawledData Os dados extraídos da página web, incluindo URL, título, citação, palavras-chave e links.
         */
        public void sendMulticast(CrawledData crawledData) {
            //  A estrutura try-with-resources chama o método close() do socket automaticamente.
            try (MulticastSocket socket = new MulticastSocket(downloaderMulticastPort)) {
                socket.setTimeToLive(64); // Ajusta o TTL conforme necessário

                // Prepara os dados a serem enviados via multicast
                Map<String, String> message = new HashMap<>();
                message.put("type", "crawledData");
                message.put("url", crawledData.getUrl());
                message.put("title", crawledData.getTitle());
                message.put("quote", crawledData.getQuote());

                // Para 'words'
                if (crawledData.getWords() == null || crawledData.getWords().isEmpty()) {
                    message.put("words", " ");
                } else {
                    message.put("words", crawledData.getWords().toString().replaceAll("[\\[\\]\\s]", ""));
                }

                // Para 'links'
                if (crawledData.getLinks() == null || crawledData.getLinks().isEmpty()) {
                    message.put("links", " ");
                } else {
                    message.put("links", crawledData.getLinks().toString().replaceAll("[\\[\\]\\s]", ""));
                }

                StringBuilder msg = new StringBuilder();
                // Adiciona o elemento 'type' primeiro
                msg.append("type").append(" | ").append(message.get("type")).append(" ; ");

                // Itera sobre o mapa para adicionar os outros elementos, exceto 'type'
                for (String key : message.keySet()) {
                    if (!"type".equals(key)) { // Pula 'type', já que ele já foi adicionado
                        msg.append(key).append(" | ").append(message.get(key)).append(" ; ");
                    }
                }
                msg.append("\n");

                // Converte a mensagem para bytes e empacota para envio
                byte[] buffer = msg.toString().getBytes();
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length, downloaderMulticastGroup, downloaderMulticastPort);

                // Envia o pacote
                socket.send(packet);
            } catch (IOException e) {
                System.out.println("Erro no multicast sender.");
            }
        }
    }
}
