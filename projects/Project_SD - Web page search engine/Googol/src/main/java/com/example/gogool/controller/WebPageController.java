package com.example.gogool.controller;

import com.example.gogool.service.HackerNewsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.support.SessionStatus;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Controlador da Web que gerencia as requisições e redirecionamentos das páginas web.
 */
@Controller
@SessionAttributes({"query", "searchResults"})
public class WebPageController {

    private final GogoolController gogoolController;
    private final HackerNewsService hackerNewsService;

    /**
     * Construtor para injeção de dependências.
     *
     * @param gogoolController O controlador do Gogool.
     * @param hackerNewsService O serviço do HackerNews.
     */
    @Autowired
    public WebPageController(GogoolController gogoolController,HackerNewsService hackerNewsService) {
        this.gogoolController = gogoolController;
        this.hackerNewsService = hackerNewsService;
    }

    /**
     * Mapeamento para a página inicial.
     *
     * @return O nome da view da página inicial.
     */
    @GetMapping("/")
    public String index() {
        return "index";
    }

    /**
     * Mapeamento para a página de login.
     *
     * @return O nome da view da página de login.
     */
    @GetMapping("/login")
    public String login() {
        return "login";
    }

    /**
     * Mapeamento para a página de registro.
     *
     * @return O nome da view da página de registro.
     */
    @GetMapping("/register")
    public String register() {
        return "register";
    }

    /**
     * Mapeamento para a página de opções do Gogool.
     *
     * @return O nome da view da página de opções.
     */
    @GetMapping("/googol")
    public String showOptions() { return "googol"; }

    /**
     * Mapeamento para o formulário de adicionar URL.
     *
     * @return O nome da view do formulário de adicionar URL.
     */
    @GetMapping("/googol/addUrl")
    public String addUrlForm() { return "addUrl"; }

    /**
     * Mapeamento para o formulário de pesquisa.
     *
     * @return O nome da view do formulário de pesquisa.
     */
    @GetMapping("/googol/search")
    public String searchForm() { return "search"; }

    /**
     * Mapeamento para o formulário de pesquisa no Gateway.
     *
     * @param model O modelo de atributos da página.
     * @return O nome da view do formulário de pesquisa no Gateway.
     */
    @GetMapping("/googol/search/searchGateway")
    public String searchGatewayForm(Model model) {
        model.addAttribute("query", "");
        model.addAttribute("results", new ArrayList<String>());
        model.addAttribute("currentPage", 0);
        model.addAttribute("totalPages", 0);
        return "searchGateway";
    }

    /**
     * Mapeamento para os resultados de pesquisa no Gateway.
     *
     * @param query A query de pesquisa.
     * @param page O número da página.
     * @param size O tamanho da página.
     * @param model O modelo de atributos da página.
     * @param searchResults A lista de resultados da pesquisa.
     * @return O nome da view dos resultados de pesquisa.
     */
    @GetMapping("/googol/search/searchGateway/results")
    public String searchResults(@RequestParam("query") String query,
                                @RequestParam(value = "page", defaultValue = "0") int page,
                                @RequestParam(value = "size", defaultValue = "10") int size,
                                Model model,
                                @ModelAttribute("searchResults") List<String> searchResults) {
        return gogoolController.paginateResults(query, page, size, model, searchResults);
    }

    /**
     * Mapeamento para limpar os resultados de pesquisa.
     *
     * @param sessionStatus O status da sessão.
     * @param model O modelo de atributos da página.
     * @return Redireciona para o formulário de pesquisa no Gateway.
     */
    @GetMapping("/googol/search/searchGateway/clear")
    public String clearSearch(SessionStatus sessionStatus, Model model) {
        sessionStatus.setComplete();
        model.addAttribute("query", "");
        model.addAttribute("results", new ArrayList<String>());
        model.addAttribute("currentPage", 0);
        model.addAttribute("totalPages", 0);
        return "redirect:/googol/search/searchGateway";
    }

    /**
     * Mapeamento para o formulário de pesquisa no HackerNews.
     *
     * @return O nome da view do formulário de pesquisa no HackerNews.
     */
    @GetMapping("/googol/search/searchHackerNews")
    public String searchHackerNewsForm(){
        return "hackerNewsResults";
    }

    /**
     * Mapeamento para o formulário de pesquisa de projetos no HackerNews.
     *
     * @return O nome da view do formulário de pesquisa de projetos.
     */
    @GetMapping("/googol/search/searchProjects")
    public String searchProjectsForm() {
        return "searchProjects";
    }

    /**
     * Mapeamento para o formulário de pesquisa de URL.
     *
     * @return O nome da view do formulário de pesquisa de URL.
     */
    @GetMapping("/googol/searchUrl")
    public String searchUrlForm() {
        return "searchUrl";
    }


    //------------------------------------------------------------------------------------------------------------------


    /**
     * Mapeamento para a autenticação do usuário.
     *
     * @param username O nome de usuário.
     * @param password A senha do usuário.
     * @param model O modelo de atributos da página.
     * @return O nome da view de redirecionamento após login.
     */
    @PostMapping("/login")
    public String loginUser(@RequestParam("username") String username, @RequestParam("password") String password, Model model) {
        String result = gogoolController.loginUser(username, password);
        if ("Login successful".equals(result)) {
            return "redirect:/googol";
        } else {
            model.addAttribute("result", result);
            return "login";
        }
    }

    /**
     * Mapeamento para o registro do usuário.
     *
     * @param username O nome de usuário.
     * @param password A senha do usuário.
     * @param model O modelo de atributos da página.
     * @return O nome da view de redirecionamento após registro.
     */
    @PostMapping("/register")
    public String registerUser(@RequestParam("username") String username, @RequestParam("password") String password, Model model) {
        String result = gogoolController.registerUser(username, password);
        model.addAttribute("result", result);
        return "register";
    }

    /**
     * Mapeamento para a seleção de opção na página do Gogool.
     *
     * @param option A opção selecionada.
     * @return O redirecionamento para a página correspondente.
     */
    @PostMapping("/googol")
    public String selectOption(@RequestParam("option") String option) {
        switch (option) {
            case "option1":
                return "redirect:/googol/addUrl"; // Redireciona para a página de adicionar URL
            case "option2":
                return "redirect:/googol/search"; // Redireciona para a página de pesquisa
            case "option3":
                return "redirect:/googol/searchUrl"; // Redireciona para a página de consulta de páginas
            case "option4":
                return "redirect:/googol"; // Redireciona para a página de administração de estatísticas
            case "option5":
                return "redirect:/"; // Redireciona para a página de logout
            default:
                return "optionResult"; // Retorna o nome do template Thymeleaf para a página de resultado padrão
        }
    }

    /**
     * Mapeamento para adicionar uma URL.
     *
     * @param url A URL a ser adicionada.
     * @param model O modelo de atributos da página.
     * @return O nome da view do formulário de adicionar URL com o resultado.
     */
    @PostMapping("/googol/addUrl")
    public String addUrl(@RequestParam("url") String url, Model model) {
        String result = gogoolController.addUrl(url);
        model.addAttribute("result", result);
        return "addUrl";
    }

    /**
     * Mapeamento para selecionar uma opção de pesquisa.
     *
     * @param pesquisa A opção de pesquisa selecionada.
     * @return O redirecionamento para a página correspondente.
     */
    @PostMapping("/googol/search")
    public String search(@RequestParam("option") String pesquisa) {
        switch (pesquisa) {
            case "option1":
                return "redirect:/googol/search/searchGateway"; // Redireciona para a página de adicionar URL
            case "option2":
                return "redirect:/googol/search/searchHackerNews"; // Redireciona para a página de pesquisa
            case "option3":
                return "redirect:/googol/search/searchProjects"; // Redireciona para a página de consulta de páginas
            case "option4":
                return "redirect:/googol"; // Redireciona para a página de administração de estatísticas
            default:
                return "optionResult"; // Retorna o nome do template Thymeleaf para a página de resultado padrão
        }
    }

    /**
     * Mapeamento para a pesquisa no Gateway.
     *
     * @param query A query de pesquisa.
     * @param page O número da página.
     * @param size O tamanho da página.
     * @param model O modelo de atributos da página.
     * @param searchResults A lista de resultados da pesquisa.
     * @return O nome da view dos resultados de pesquisa.
     */
    @PostMapping("/googol/search/searchGateway")
    public String searchGateway(@RequestParam("query") String query,
                         @RequestParam(value = "page", defaultValue = "0") int page,
                         @RequestParam(value = "size", defaultValue = "10") int size,
                         Model model,
                         @ModelAttribute("searchResults") List<String> searchResults) {
        model.addAttribute("query", query);
        if (searchResults.isEmpty()) {
            List<String> results = gogoolController.search(query);
            searchResults.addAll(results);
        }

        return gogoolController.paginateResults(query, page, size, model, searchResults);
    }

    /**
     * Mapeamento para a pesquisa no HackerNews.
     *
     * @param term O termo de pesquisa.
     * @return A lista de resultados da pesquisa.
     */
    @PostMapping("/googol/search/searchHackerNews")
    @ResponseBody
    public List<String> searchHackerNews(@RequestParam("term") String term) {
        return hackerNewsService.searchTopStories(term);
    }

    /**
     * Mapeamento para a pesquisa de projetos no HackerNews.
     *
     * @param term O termo de pesquisa.
     * @return A lista de resultados da pesquisa.
     */
    @PostMapping("/googol/search/searchProjects")
    @ResponseBody
    public List<Map<String, Object>> searchProjects(@RequestParam("term") String term) {
        return hackerNewsService.searchProjects(term);
    }

    /**
     * Mapeamento para a pesquisa de uma URL específica.
     *
     * @param url A URL a ser pesquisada.
     * @param model O modelo de atributos da página.
     * @return O nome da view do formulário de pesquisa de URL com o resultado.
     */
    @PostMapping("/googol/searchUrl")
    public String searchUrl(@RequestParam("url") String url, Model model) {
        String result = gogoolController.searchUrl(url);
        model.addAttribute("result", result);
        return "searchUrl";
    }


    //------------------------------------------------------------------------------------------------------------------


    /**
     * Model attribute para inicializar a lista de resultados de pesquisa.
     *
     * @return Uma nova lista vazia de resultados de pesquisa.
     */
    @ModelAttribute("searchResults")
    public List<String> searchResults() {
        return new ArrayList<>();
    }

    /**
     * Model attribute para inicializar a query de pesquisa.
     *
     * @return Uma string vazia como query de pesquisa.
     */
    @ModelAttribute("query")
    public String query() {
        return "";
    }


}
