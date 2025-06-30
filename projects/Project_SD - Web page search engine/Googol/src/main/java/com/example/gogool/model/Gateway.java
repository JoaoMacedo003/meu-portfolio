package com.example.gogool.model;

import com.example.gogool.rmi.RMIGateway;
import com.example.gogool.rmi.RMIStorageBarrel;

import java.io.*;
import java.net.Socket;
import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Classe Gateway que serve como ponto de entrada para os serviços oferecidos menos a Indexar novo URL.
 * Implementa a interface RMIGateway para comunicação RMI.
 */
public class Gateway extends UnicastRemoteObject implements RMIGateway {

    private final Map<String, Long> searchCounts = new HashMap<>();
    private final List<String> topSearches = new ArrayList<>(11);
    private final Map<String, Long> responseTimes = new HashMap<>();
    private final Map<String, Long> barrelCounts = new HashMap<>();
    private final List<String> activeBarrels = new ArrayList<>();
    private final List<String> BarrelsIds = new ArrayList<>();
    private final List<RMIStorageBarrel> barrels = new CopyOnWriteArrayList<>();
    private final AtomicInteger nextBarrelIndex = new AtomicInteger(0);
    private final AtomicInteger nextId = new AtomicInteger(1);

    private String downloaderHost;
    private int downloaderPort;
    private int gatewayRMIPort;
    private String gatewayRMIHost;

    /**
     * Construtor da classe Gateway.
     * Inicializa a conexão socket e configura o objeto para comunicação RMI.
     *
     * @throws RemoteException Se ocorrer algum problema durante a comunicação RMI.
     */
    public Gateway() throws RemoteException {
        super();
        loadConfig();
    }

    /**
     * Método principal para iniciar o Gateway.
     * Configura o registro RMI e o socket para receber mensagens.
     *
     * @param args Argumentos da linha de comando.
     */
    public static void main(String[] args) {
        try {
            // Create an instance of Gateway
            Gateway gateway = new Gateway();

            // Start the RMI registry
            Registry registry = LocateRegistry.createRegistry(gateway.gatewayRMIPort);
            System.out.println("RMI Registry started on port " + gateway.gatewayRMIPort);

            // Bind the remote object in the registry
            registry.rebind("Gateway", gateway);
            System.out.println("Gateway bound in registry");

            System.out.println("Gateway Started");

            // Manter o processo ativo
            synchronized (Gateway.class) {
                Gateway.class.wait();
            }

        } catch (RemoteException re) {
            System.out.println("Remote Exception in Gateway - main: " + re);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Carrega as propriedades de configuração do arquivo config.txt.
     *
     * Se o arquivo config.txt não for encontrado ou ocorrer um erro durante o carregamento,
     * uma mensagem apropriada é impressa no console e o método retorna.
     *
     * Este método inicializa os seguintes campos com os valores do arquivo de propriedades:
     * - gatewayRMIHost
     * - gatewayRMIPort
     * - downloaderHost
     * - downloaderPort
     *
     * Se algum valor de propriedade estiver ausente ou não puder ser analisado, uma NumberFormatException pode ser lançada.
     *
     * @exception IOException Se ocorrer um erro de E/S durante o carregamento do arquivo de propriedades.
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
            this.downloaderHost = properties.getProperty("downloader.host");
            this.downloaderPort = Integer.parseInt(properties.getProperty("downloader.port"));
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    /**
     * Escolhe um barrel de armazenamento para uso.
     *
     * @return O barrel escolhido.
     * @throws IllegalStateException Se não houver barrels disponíveis.
     */
    private RMIStorageBarrel chooseBarrel() {
        if (activeBarrels.isEmpty()) {
            throw new IllegalStateException("Não há barrels disponíveis.");
        }

        int index = nextBarrelIndex.getAndUpdate(i -> (i + 1) % activeBarrels.size());

        String activeBarrelId = activeBarrels.get(index);

        int index1 = BarrelsIds.indexOf(activeBarrelId);

        return barrels.get(index1);
    }

    /**
     * Registra um barril para armazenamento e atualiza as estruturas de dados correspondentes.
     *
     * @param barrel O barril a ser registrado.
     * @throws RemoteException Se ocorrer algum problema durante a comunicação RMI.
     */
    @Override
    public void registerBarrel(RMIStorageBarrel barrel) throws RemoteException {
        String barrelId = "Barrel" + nextId.getAndIncrement();
        barrels.add(barrel);
        BarrelsIds.add(barrelId);
        activeBarrels.add(barrelId);
        responseTimes.put(barrelId, 0L);

        barrel.setBarrelId(barrelId);
    }

    /**
     * Atualiza o barril da propriedade removendo-o da lista de barris ativos.
     *
     * Este método é chamado remotamente e remove o barril com o ID fornecido da lista de barris ativos.
     *
     * @param remoteRef A referência remota para o objeto RMIStorageBarrel.
     * @throws RemoteException Se ocorrer um erro de comunicação remota.
     */
    @Override
    public void updateEstateBarrel(RMIStorageBarrel remoteRef) throws RemoteException {
        String barrelId = remoteRef.getBarrelId();
        activeBarrels.remove(barrelId);
    }

    /**
     * Realiza uma pesquisa por um termo/s específico/s, selecionando um barrel de armazenamento para a pesquisa.
     * Registra o tempo de resposta e atualiza as estatísticas de pesquisa.
     *
     * @param term O termo de pesquisa.
     * @return A mensagem resultante da pesquisa, podendo ser os resultados ou uma mensagem de erro.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public List<String> search(String term) throws RemoteException {
        long startTime = System.currentTimeMillis();
        String msg;
        RMIStorageBarrel barrel = null;
        try {
            barrel = chooseBarrel();
            if (barrel != null) {
                System.out.println("Barrel connection established");
                updateSearchCount(term);
                msg = barrel.searchWord(term);
            } else {
                throw new IllegalStateException("Barrel não encontrado.");
            }
        } finally {
            if (barrel != null) {
                long endTime = System.currentTimeMillis();
                updateResponseTime(barrel.getBarrelId(), endTime - startTime);
            }
        }

        // Dividir a string em uma lista de resultados
        String[] resultsArray = msg.split("\n\n");
        List<String> resultsList = new ArrayList<>();
        for (String result : resultsArray) {
            resultsList.add(result.trim());
        }

        return resultsList;
    }

    /**
     * Adiciona uma URL ao serviço de download.
     *
     * Este método estabelece uma conexão de socket com o serviço de download e envia a URL.
     * Se a operação for bem-sucedida, retorna uma mensagem de confirmação.
     * Em caso de um erro de E/S, uma RemoteException é lançada.
     *
     * @param url A URL a ser adicionada.
     * @return Uma mensagem de confirmação indicando que a URL foi adicionada com sucesso.
     * @throws RemoteException Se ocorrer um erro de comunicação remota ou um erro de E/S.
     */

    @Override
    public String addUrl(String url) throws RemoteException {
        try (Socket socket = new Socket(downloaderHost, downloaderPort);
             DataOutputStream out = new DataOutputStream(socket.getOutputStream())) {
            out.writeUTF(url);
            return "URL added successfully";
        } catch (IOException e) {
            throw new RemoteException("Failed to add URL", e);
        }
    }

    /**
     * Atualiza a contagem de pesquisas por um determinado termo, de forma sincronizada.
     *
     * @param term O termo para o qual a contagem de pesquisas será incrementada.
     */
    private void updateSearchCount(String term) {
        searchCounts.merge(term, 1L, Long::sum);
    }

    /**
     * Atualiza o tempo de resposta e a contagem de pesquisas para um determinado barrel.
     *
     * @param barrelId O identificador do barrel.
     * @param responseTime O tempo de resposta a ser adicionado.
     */
    private void updateResponseTime(String barrelId, long responseTime) {
        responseTimes.merge(barrelId, responseTime, Long::sum);
        barrelCounts.merge(barrelId, 1L, Long::sum);
    }

    /**
     * Realiza uma pesquisa por um URL específico, selecionando um barrel de armazenamento para a pesquisa.
     *
     * @param url O URL da pesquisa.
     * @return A mensagem resultante da pesquisa.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public String search2(String url) throws RemoteException {
        long startTime = System.currentTimeMillis();
        RMIStorageBarrel barrel = null;
        try {
            barrel = chooseBarrel();
            System.out.println("Barrel connection established");
            System.out.println("Searching for URL: " + url);
            String msg = "";
            msg = msg + barrel.searchUrl(url);
            return msg;
        } catch (RemoteException e) {
            System.out.println("Exception in SearchModule search2");
            return null;
        } finally {
            if (barrel != null) {
                long endTime = System.currentTimeMillis();
                updateResponseTime(barrel.getBarrelId(), endTime - startTime);
            }
        }
    }

    /**
     * Calcula e retorna os tempos médios de resposta para cada barrel baseado no total de respostas e a quantidade de pesquisas realizadas.
     *
     * @return Um mapa onde a chave é o identificador do barrel e o valor é o tempo médio de resposta.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public Map<String, Double> getAverageResponseTimes() throws RemoteException {
        Map<String, Double> averageResponseTimes = new HashMap<>();
        responseTimes.forEach((key, value) -> {
            long count = barrelCounts.getOrDefault(key, 1L);
            averageResponseTimes.put(key, value / (double) count);
        });
        return averageResponseTimes;
    }

    /**
     * Retorna uma lista contendo os identificadores dos barrels atualmente ativos no sistema.
     *
     * @return Uma lista de strings com os identificadores dos barrels ativos.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public List<String> getActiveBarrels() throws RemoteException {
        return new ArrayList<>(activeBarrels);
    }

    /**
     * Regista um novo user no sistema, dando a ação para um barrel específico.
     *
     * @param username Nome de user para registo.
     * @param password Senha do user.
     * @return Uma string indicando o sucesso ou falha do registo.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public String registerUser(String username, String password) throws RemoteException {
        RMIStorageBarrel barrel = chooseBarrel();
        return barrel.registerUser(username, password);
    }

    /**
     * Realiza o login de um user, verificando as suas credenciais através de um barrel específico.
     *
     * @param username Nome de user.
     * @param password Senha do user.
     * @return Uma string indicando o sucesso ou falha do login.
     * @throws Exception Se ocorrer um erro durante a tentativa de login, incluindo problemas de comunicação RMI e barrels não disponíveis.
     */
    @Override
    public String logIn(String username, String password) throws Exception {
        RMIStorageBarrel barrel = chooseBarrel();
        return barrel.logIn(username, password);
    }

    /**
     * Recupera e retorna uma lista das 10 pesquisas mais realizadas no sistema.
     *
     * @return Uma lista imutável contendo os termos das top 10 pesquisas.
     * @throws RemoteException Se ocorrer um erro de comunicação RMI.
     */
    @Override
    public List<String> getTopSearches() throws RemoteException {
        topSearches.clear();

        searchCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(10)
                .forEach(entry -> topSearches.add(entry.getKey()));

        return Collections.unmodifiableList(topSearches);
    }
}
