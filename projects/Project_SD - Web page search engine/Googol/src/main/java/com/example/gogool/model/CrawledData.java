package com.example.gogool.model;

import java.util.List;
import java.util.ArrayList;


/**
 * Representa os dados coletados de uma página da web durante o processo de crawling.
 * Inclui o URL da página, o título, uma citação destacada, palavras da página e uma lista de links encontrados na página.
 */
public class CrawledData{
    private String url; // URL da página.
    private String title;   // Título da página.
    private String quote;   // Uma citação ou texto destacado na página.
    private List<String> words; // Lista de palavras-chave ou termos encontrados na página.
    public List<String> links;  // Lista de palavras-chave ou termos relevantes encontrados na página.

    /**
     * Construtor para criar uma instância de CrawledData com URL e título inicializados.
     * As listas de palavras e links são iniciadas vazias.
     *
     * @param url A URL da página web.
     * @param title O título da página web.
     */
    public CrawledData(String url, String title) {
        this.url = url;
        this.title = title;
        this.quote = "";
        this.words = new ArrayList<>();
        this.links = new ArrayList<>();
    }

    // Métodos Getters e Setters

    /**
     * Retorna o URL da página.
     *
     * @return O URL da página.
     */
    public String getUrl() {
        return url;
    }

    /**
     * Define o URL da página.
     *
     * @param url O novo URL da página.
     */
    public void setUrl(String url) {
        this.url = url;
    }

    /**
     * Retorna o título da página.
     *
     * @return O título da página.
     */
    public String getTitle() {
        return title;
    }

    /**
     * Define o título da página.
     *
     * @param title O novo título da página.
     */
    public void setTitle(String title) {
        this.title = title;
    }

    /**
     * Retorna uma citação ou texto destacado da página.
     *
     * @return A citação ou texto destacado.
     */
    public String getQuote() {return quote; }

    /**
     * Define uma citação ou texto destacado na página.
     *
     * @param text O novo texto destacado ou citação.
     */
    public void setQuote(String text) {
        this.quote = text;
    }

    /**
     * Retorna a lista de palavras coletadas da página.
     *
     * @return A lista de palavras.
     */
    public List<String> getWords() {
        return words;
    }

    /**
     * Define a lista de palavras coletadas da página.
     *
     * @param words A nova lista de palavras.
     */
    public void setWords(List<String> words) {
        this.words = words;
    }

    /**
     * Retorna a lista de links encontrados na página.
     *
     * @return A lista de links.
     */
    public List<String> getLinks() {
        return links;
    }

    /**
     * Define a lista de links encontrados na página.
     *
     * @param Links A nova lista de links.
     */
    public void setLinks(List<String> Links) { this.links = Links; }

}
