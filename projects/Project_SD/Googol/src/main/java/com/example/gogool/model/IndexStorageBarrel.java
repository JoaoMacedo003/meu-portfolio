package com.example.gogool.model;

import com.example.gogool.rmi.RMIStorageBarrel;
import com.example.gogool.model.CrawledData;
import com.example.gogool.rmi.RMIGateway;


import com.example.gogool.rmi.RMIStorageBarrel;

import java.io.*;
import java.net.DatagramPacket;
import java.nio.charset.StandardCharsets;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.rmi.server.UnicastRemoteObject;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;


/**
 * Classe que implementa a interface RMIStorageBarrel para armazenamento e gerenciamento de dados coletados por web crawlers.
 * Permite o registro e a pesquisa de informações sobre URLs, como título, citações, palavras-chave e conexões.
 */
public class IndexStorageBarrel implements RMIStorageBarrel {

    private final HashMap<String, HashMap<String, String>> urlsTitleQuote = new HashMap<>();
    private final HashMap<String, HashSet<String>> urlsWords = new HashMap<>();
    private final HashMap<String, HashSet<String>> urlsConnections = new HashMap<>();
    private final String USER_CREDENTIALS_FILE = "userCredentials.obj";
    private HashMap<String, String> userCredentials;
    private String barrelId;
    private RMIStorageBarrel remoteRef = null;
    private int gatewayRMIPort;
    private String gatewayRMIHost;  // IP address of the Gateway
    private String downloaderMulticastGroup;
    private int downloaderMulticastPort;
    private MulticastSocket socket;

    private String indexStorageBarrelHost;

    /**
     * Construtor que inicializa um novo barrel com um identificador, ficheiros para os users e configurações de rede.
     */
    public IndexStorageBarrel() {
        loadConfig();
        initUserCredentials();
        remoteRef = registerSelf();

    }

    /**
     * Método principal que configura o barrel para recepção de dados via multicast e registro RMI.
     *
     * @param args Argumentos da linha de comando.
     */
    public static void main(String[] args) {
        IndexStorageBarrel barrelInstance = new IndexStorageBarrel(); // Criar uma instância da classe

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutdown hook is running...");
            try {
                if (barrelInstance.socket != null) {
                    System.out.println("Leaving multicast group and closing socket...");
                    barrelInstance.updateBarrelEstate();
                    barrelInstance.socket.leaveGroup(InetAddress.getByName(barrelInstance.downloaderMulticastGroup));
                    barrelInstance.socket.close();
                }
            } catch (IOException e) {
                System.err.println("Error closing multicast socket: " + e.getMessage());
            }
        }));

        try {
            InetAddress group = InetAddress.getByName(barrelInstance.downloaderMulticastGroup);
            barrelInstance.socket = new MulticastSocket(barrelInstance.downloaderMulticastPort);
            barrelInstance.socket.joinGroup(group);

            ExecutorService executor = Executors.newFixedThreadPool(1);
            executor.execute(barrelInstance.new CentralBarrel()); // Usar a instância criada para a thread
            executor.shutdown();

            try {
                if (!executor.awaitTermination(1, TimeUnit.DAYS)) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException e) {
                System.err.println("A espera pela conclusão das tarefas foi interrompida: " + e.getMessage());
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        } catch (IOException e) {
            System.err.println("Exception found in Barrel (Main): " + e.getMessage());
        }


    }

    /**
     * Carrega as propriedades de configuração a partir do arquivo config.txt.
     *
     * Este método lê um arquivo de propriedades localizado no caminho do classpath e
     * carrega suas propriedades. As propriedades carregadas incluem:
     * - gateway.rmi.host
     * - gateway.rmi.port
     * - downloader.multicast.group
     * - downloader.multicast.port
     * - indexStorageBarrel.host
     *
     * Se o arquivo config.txt não for encontrado ou ocorrer um erro durante o carregamento,
     * uma mensagem apropriada é impressa no console e o método retorna.
     *
     * Este método inicializa os seguintes campos com os valores das propriedades:
     * - gatewayRMIHost
     * - gatewayRMIPort
     * - downloaderMulticastGroup
     * - downloaderMulticastPort
     * - indexStorageBarrelHost
     *
     * @throws IOException Se ocorrer um erro de E/S durante o carregamento do arquivo de propriedades.
     */
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
            this.gatewayRMIHost = properties.getProperty("gateway.rmi.host");
            this.gatewayRMIPort = Integer.parseInt(properties.getProperty("gateway.rmi.port"));
            this.downloaderMulticastGroup = properties.getProperty("downloader.multicast.group");
            this.downloaderMulticastPort = Integer.parseInt(properties.getProperty("downloader.multicast.port"));
            this.indexStorageBarrelHost = properties.getProperty("indexStorageBarrel.host");
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    /**
     * Obtém o identificador do barrel.
     *
     * @return O identificador do barrel.
     * @throws RemoteException Se ocorrer um erro na comunicação remota.
     */
    public String getBarrelId() throws RemoteException {
        return barrelId;
    }

    public void setBarrelId(String id) throws RemoteException {
        this.barrelId = id;
    }

    /**
     * Registra este barrel no gateway RMI para torná-lo acessível para buscas e outras operações.
     */
    private RMIStorageBarrel registerSelf() {
        RMIStorageBarrel remoteRef = null;
        try {
            System.setProperty("java.rmi.server.hostname", indexStorageBarrelHost);// IP do host do Barrel
            LocateRegistry.createRegistry(5100); // Ensure the RMI registry is created on the specific IP and port
            RMIGateway gateway = (RMIGateway) LocateRegistry.getRegistry(gatewayRMIHost, gatewayRMIPort).lookup("Gateway");
            remoteRef = (RMIStorageBarrel) UnicastRemoteObject.exportObject(this, 0);  // Registro RMI na porta  para object( servidor central) com o nome de IndexStorageBarrel
            gateway.registerBarrel(remoteRef);
        } catch (Exception e) {
            System.err.println("Erro ao registrar o barrel no gateway: " + e.getMessage());
        }
        return remoteRef;
    }

    /**
     * Atualiza o estado do barrel comunicando-se com o serviço gateway.
     *
     * Este método obtém a referência remota para o serviço gateway e chama o método
     * updateEstateBarrel para atualizar o estado do barrel. Se ocorrer alguma exceção,
     * uma mensagem de erro é impressa no fluxo de erro padrão.
     *
     * O serviço gateway é procurado usando o registro RMI no host e porta especificados.
     *
     * @throws Exception Se ocorrer um erro durante a procura no registro RMI ou a chamada do método remoto.
     */
    private void updateBarrelEstate() {
        try {
            RMIGateway gateway = (RMIGateway) LocateRegistry.getRegistry(gatewayRMIHost, gatewayRMIPort).lookup("Gateway");
            gateway.updateEstateBarrel(remoteRef);
        } catch(Exception e) {
            System.err.println("Erro ao atualizar o estado do barrel no gateway: " + e.getMessage());
        }
    }


    /**
     * Salva os dados coletados em arquivos de objetos.
     */
    public void saveData() {

        File fileUTQ = new File("UTQ.obj"); // Guarda os titulos e citacoes associadas a cada url
        File fileUW = new File("UW.obj");   // Para cada url guarda as palavras associadas a ele
        File fileUC = new File("UC.obj");   // Para cada url guarda todos os links associados a essa página.

        saveObjectToFile(fileUTQ, urlsTitleQuote);
        saveObjectToFile(fileUW, urlsWords);
        saveObjectToFile(fileUC, urlsConnections);
    }


    /**
     * Auxiliar para salvar um objeto em um arquivo específico.
     *
     * @param filename O nome do arquivo no qual o objeto será salvo.
     * @param object   O objeto a ser salvo.
     */
    public synchronized void saveObjectToFile(File filename, Object object) {
        try (RandomAccessFile raf = new RandomAccessFile(filename, "rw");
             FileChannel channel = raf.getChannel();
             FileLock lock = channel.lock()) {  // Bloqueio exclusivo

            ObjectOutputStream oos = new ObjectOutputStream(new BufferedOutputStream(new FileOutputStream(raf.getFD())));
            oos.writeObject(object);
            oos.flush();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    /**
     * Atualiza os HashMaps com os dados coletados de uma página web.
     *
     * @param crawledData Os dados coletados da página.
     */
    public void updateHashMaps(CrawledData crawledData) {

        urlsTitleQuote.put(crawledData.getUrl(), new HashMap<>());
        urlsTitleQuote.get(crawledData.getUrl()).put("title", crawledData.getTitle());
        urlsTitleQuote.get(crawledData.getUrl()).put("quote", crawledData.getQuote());

        List<String> words = crawledData.getWords();

        for (String word : words) {
            if (word.isEmpty())
                continue;
            if (urlsWords.containsKey(word)) {
                urlsWords.get(word).add(crawledData.getUrl());
            } else {
                HashSet<String> urls = new HashSet<>();
                urls.add(crawledData.getUrl());
                urlsWords.put(word, urls);
            }
        }

        if (!crawledData.getLinks().isEmpty()) {
            if (!crawledData.getWords().isEmpty()) {
                List<String> links = crawledData.getLinks();

                for (String link : links) {
                    if (urlsConnections.containsKey(link)) {
                        urlsConnections.get(link).add(crawledData.getUrl());
                    } else {
                        HashSet<String> urls = new HashSet<>();
                        urls.add(crawledData.getUrl());
                        urlsConnections.put(link, urls);
                    }

                }
            }
        }

    }

    /**
     * Classe interna que implementa Runnable para tratar a recepção de dados via multicast.
     */
    public class CentralBarrel implements Runnable {

        /**
         * Executa a tarefa de ouvir mensagens multicast. Para cada mensagem recebida, extrai os dados relevantes
         * e atualiza as estruturas de dados correspondentes.
         */
        @Override
        public void run() {

            while (true) {
                byte[] buffer = new byte[999999999];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);


                try {

                    socket.receive(packet); // Recebe algo pelo canal multicast

                    String packetString = new String(packet.getData(), 0, packet.getLength());


                    /*
                     * Exemplo de packetString:
                     *
                     * type | login ; username | t i n t i n ; password | unicorn
                     * type | s t a t u s ; logged | on ; msg | Welcome to the app
                     * type | u r l _ l i s t ; item_count | 2; item_0_name | www. uc . pt ; item_1_name | www. dei . uc . pt
                     *
                     */

                    String[] data = packetString.split(" ; "); // Separa a string por " ; " ou " | "

                    CrawledData crawledData = new CrawledData("", "");
                    String[] keyValue;

                    for (int i = 1; i < data.length; i++) {
                        if (data[i].length() > 1) { // Garante que os conjuntos de dados sejam válidos, tenham mais que um dado
                            keyValue = data[i].split(" \\| ");  // Separa a string por " | "

                            switch (keyValue[0]) {
                                case "url":
                                    crawledData.setUrl(keyValue[1]);
                                    break;
                                case "title":
                                    crawledData.setTitle(keyValue[1]);
                                    break;
                                case "quote":
                                    StringBuilder quoteBuilder = new StringBuilder();
                                    String[] quote = keyValue[1].split(" ");
                                    for (int j = 2; j < quote.length; j++) {
                                        quoteBuilder.append(quote[j]);
                                        if (j < quote.length - 1) {
                                            quoteBuilder.append(" ");
                                        }
                                    }
                                    crawledData.setQuote(quoteBuilder.toString());
                                    break;
                                case "words":
                                    if (keyValue[1].equals(" ")) {
                                        break;
                                    }
                                    // palavra1,palavra2,palavra3
                                    String[] words = keyValue[1].split(",");
                                    ArrayList<String> Words = new ArrayList<>(Arrays.asList(words).subList(1, words.length));
                                    crawledData.setWords(Words);
                                    break;
                                case "links":
                                    if (keyValue[1].equals(" ")) {
                                        break;
                                    }
                                    String[] links = keyValue[1].split(",");
                                    ArrayList<String> Links = new ArrayList<>();
                                    for (int j = 1; j < links.length; j++) {
                                        String link = links[j];
                                        if (!(crawledData.getLinks().contains(link))) {
                                            Links.add(link);
                                        }
                                    }
                                    crawledData.setLinks(Links);
                                    break;
                            }
                        }
                    }


                    updateHashMaps(crawledData);
                    saveData();

                } catch (IllegalArgumentException e) {
                    System.err.println("Exception occurred. Invalid argument: " + e.getMessage());

                } catch (IOException e) {
                    System.err.println("Exception occurred: " + e.getMessage());

                }
            }
        }

    }

    /**
     * Pesquisa por palavras-chave em URLs armazenadas, retornando informações sobre elas.
     *
     * @param term O termo de pesquisa.
     * @return Uma string contendo informações sobre as URLs que contêm o termo de pesquisa, ordenadas por relevância.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    public String searchWord(String term) throws RemoteException {
        StringBuilder msg = new StringBuilder();
        try {
            term += " ";
            String[] word = term.split(" ");

            List<ArrayList<Object>> notOrder = new ArrayList<>();

            HashMap<String, HashSet<String>> words;
            HashMap<String, HashMap<String, String>> info_search;
            HashMap<String, HashSet<String>> u;

            words = (HashMap<String, HashSet<String>>) readObject("UW.obj");
            info_search = (HashMap<String, HashMap<String, String>>) readObject("UTQ.obj");
            u = (HashMap<String, HashSet<String>>) readObject("UC.obj");

            for (String s : word) {
                if (words.containsKey(s)) {
                    HashSet<String> urls = words.get(s);
                    for (String url : urls) {
                        HashMap<String, String> infoUrl = info_search.get(url);
                        HashSet<String> urlsPoint = u.get(url);
                        int count = 0;
                        if (urlsPoint != null)
                            count += urlsPoint.size();
                        String title = infoUrl.get("title");
                        String quote = infoUrl.get("quote");
                        String aux = title + "\n" + url + "\n" + quote + "\n\n";
                        notOrder.add(new ArrayList<>(List.of(aux, count)));
                    }

                    List<ArrayList<Object>> inOrder = notOrder.stream()
                            .sorted((lista1, lista2) -> ((Integer) lista2.get(1)).compareTo((Integer) lista1.get(1)))
                            .toList();
                    for (ArrayList<Object> list : inOrder) {
                        msg.append(list.getFirst());
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("Exception in Barrel (searchWord): " + e);
        }
        return msg.toString();
    }

    /**
     * Pesquisa por URLs específicas armazenadas e retorna informações sobre elas.
     *
     * @param url A URL a ser pesquisada.
     * @return Uma string contendo informações sobre a URL pesquisada.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    public String searchUrl(String url) throws RemoteException {
        StringBuilder msg = new StringBuilder();
        try {

            if (!(url.startsWith("http://") || url.startsWith("https://"))) {
                url = "https://".concat(url);
            }
            if (!url.endsWith("/")) {
                url = url.concat("/");
            }

            HashMap<String, HashSet<String>> u;

            u = (HashMap<String, HashSet<String>>) readObject("UC.obj");

            HashSet<String> point = u.get(url);
            if (point != null) {
                for (String a : point) {
                    msg.append(a).append("\n");
                }
                msg.append("\n");
            } else {
                msg.append("Sem URLS associados.\n\n");
            }
        } catch (Exception e) {
            System.out.println("Exception in Barrel (searchUrl): " + e);
        }
        return msg.toString();
    }

    /**
     * Lê um objeto a partir de um arquivo especificado pelo nome do arquivo.
     *
     * @param filename O nome do arquivo do qual ler o objeto.
     * @return O obj lido do arquivo, ou null se algum erro ocorrer.
     */
    public synchronized Object readObject(String filename) {
        Object obj = null;
        try (RandomAccessFile raf = new RandomAccessFile(filename, "r");
             FileChannel channel = raf.getChannel();
             FileLock lock = channel.lock(0, Long.MAX_VALUE, true)) {  // Bloqueio compartilhado

            ObjectInputStream ois = new ObjectInputStream(new BufferedInputStream(new FileInputStream(raf.getFD())));
            obj = ois.readObject();

        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
        return obj;
    }


    /**
     * Inicializa as credenciais dos users a partir de um arquivo, ou cria um novo mapa de credenciais se o arquivo não existir.
     */
    private void initUserCredentials() {
        File credentialsFile = new File(USER_CREDENTIALS_FILE);
        if (credentialsFile.exists()) {
            userCredentials = (HashMap<String, String>) readObject(USER_CREDENTIALS_FILE);
        } else {
            userCredentials = new HashMap<>();
        }
    }

    /**
     * Registra um novo user com um nome de user e senha. A senha é armazenada como um hash SHA-256.
     *
     * @param username O nome de user a ser registado.
     * @param password A senha do user.
     * @return Uma string indicando se o registo foi bem-sucedido ou não.
     * @throws RemoteException Se ocorrer um erro na comunicação RMI.
     */
    @Override
    public synchronized String registerUser(String username, String password) throws RemoteException {
        if (userCredentials.containsKey(username)) {
            return "User already exists";
        }
        try {
            String hashedPassword = hashPassword(password);
            userCredentials.put(username, hashedPassword);
            saveObjectToFile(new File(USER_CREDENTIALS_FILE), userCredentials);
            return "User registered successfully";
        } catch (Exception e) {
            return "Error registering user";
        }
    }

    /**
     * Autentica um user com um nome de user e senha fornecidos.
     *
     * @param username O nome de user.
     * @param password A senha do user.
     * @return Uma string indicando se o login foi bem-sucedido ou não.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     * @throws Exception       Se ocorrer um erro ao gerar o hash da senha.
     */
    public String logIn(String username, String password) throws RemoteException, Exception {
        if (userCredentials.containsKey(username) &&
                userCredentials.get(username).equals(hashPassword(password))) {
            return "Login successful";
        } else {
            return "Login failed";
        }
    }

    /**
     * Gera um hash SHA-256 de uma senha fornecida.
     *
     * @param password A senha a ser hashada.
     * @return A representação em string do hash SHA-256 da senha.
     * @throws Exception Se ocorrer um erro ao criar o hash.
     */
    private String hashPassword(String password) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashedBytes = digest.digest(password.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(hashedBytes);
    }

}
