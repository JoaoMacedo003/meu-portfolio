package com.example.gogool.controller;

import com.example.gogool.rmi.RMIGateway;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.ui.Model;

import javax.annotation.PostConstruct;
import java.net.MalformedURLException;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Controlador que lida com operações relacionadas ao gateway RMI.
 */
@Service
public class GogoolController {

    private RMIGateway gateway;

    @Value("${gateway.rmi.host}")
    private String rmiHost;

    @Value("${gateway.rmi.port}")
    private int rmiPort;

    /**
     * Inicializa o controlador após a construção, ligando ao serviço gateway RMI.
     */
    @PostConstruct
    public void init() {
        try {
            this.gateway = (RMIGateway) Naming.lookup("rmi://" + rmiHost + ":" + rmiPort + "/Gateway");
        } catch (RemoteException | NotBoundException | MalformedURLException e) {
            e.printStackTrace();
        }
    }

    /**
     * Registra um novo usuário no sistema.
     *
     * @param username O nome de usuário.
     * @param password A senha do usuário.
     * @return Uma mensagem indicando o sucesso ou falha do registro.
     */
    public String registerUser(String username, String password) {
        try {
            return gateway.registerUser(username, password);
        } catch (RemoteException | NotBoundException e) {
            return "Registration failed: " + e.getMessage();
        }
    }

    /**
     * Autentica um usuário no sistema.
     *
     * @param username O nome de usuário.
     * @param password A senha do usuário.
     * @return Uma mensagem indicando o sucesso ou falha do login.
     */
    public String loginUser(String username, String password) {
        try {
            return gateway.logIn(username, password);
        } catch (Exception e) {
            return "Login failed: " + e.getMessage();
        }
    }

    /**
     * Adiciona uma URL ao sistema.
     *
     * @param url A URL a ser adicionada.
     * @return Uma mensagem indicando o sucesso ou falha da adição.
     */
    public String addUrl(String url) {
        try {
            return gateway.addUrl(url);
        } catch (RemoteException e) {
            return "Failed to add URL: " + e.getMessage();
        }
    }

    /**
     * Pesquisa por uma query no sistema.
     *
     * @param query A query de pesquisa.
     * @return Uma lista de resultados da pesquisa.
     */
    public List<String> search(String query) {
        try {
            return gateway.search(query);
        } catch (RemoteException e) {
            return Collections.singletonList("Failed to search URL: " + e.getMessage());
        }
    }

    /**
     * Pagina os resultados da pesquisa.
     *
     * @param query A query de pesquisa.
     * @param page O número da página.
     * @param size O tamanho da página.
     * @param model O modelo de atributos da página.
     * @param results A lista de resultados da pesquisa.
     * @return O nome da view de resultados da pesquisa.
     */
    public String paginateResults(String query, int page, int size, Model model, List<String> results) {
        int totalResults = results.size();
        int totalPages = (int) Math.ceil((double) totalResults / size);
        int start = Math.min(page * size, totalResults);
        int end = Math.min((page + 1) * size, totalResults);
        List<String> pageResults = results.subList(start, end);

        int maxPages = Math.min(totalPages, 10);
        List<Integer> pageNumbers = new ArrayList<>();
        for (int i = 0; i < maxPages; i++) {
            pageNumbers.add(i);
        }

        model.addAttribute("query", query);
        model.addAttribute("results", pageResults);
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", totalPages);
        model.addAttribute("size", size);
        model.addAttribute("totalResults", totalResults);
        model.addAttribute("pageNumbers", pageNumbers);

        return "searchGateway";
    }

    /**
     * Pesquisa uma URL específica no sistema.
     *
     * @param url A URL a ser pesquisada.
     * @return Uma mensagem indicando o sucesso ou falha da pesquisa.
     */
    public String searchUrl(String url) {
        try {
            return gateway.search2(url);
        } catch (RemoteException e) {
            return "Failed to search URL: " + e.getMessage();
        }
    }
}
