package com.example.gogool.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestOperations;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import java.util.logging.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Serviço para interagir com a API do Hacker News.
 */
@Service
public class HackerNewsService {

    private static final Logger logger = Logger.getLogger(HackerNewsService.class.getName());
    private static final String TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json";
    private static final String ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json";
    private static final String PROJECTS_URL = "https://hacker-news.firebaseio.com/v0/showstories.json";

    /**
     * Pesquisa projetos no Hacker News que contenham o termo especificado no título.
     *
     * @param term O termo de pesquisa.
     * @return Uma lista de mapas representando os projetos que correspondem ao termo de pesquisa.
     */
    public List<Map<String, Object>> searchProjects(String term) {
        List<Map<String, Object>> projects = new ArrayList<>();
        RestTemplate restTemplate = new RestTemplate();

        // Get the top show stories IDs
        List<Integer> showStoryIds = restTemplate.getForObject(PROJECTS_URL, List.class);

        if (showStoryIds != null) {
            for (int i = 0; i < Math.min(showStoryIds.size(), 200); i++) {  // Limit to the top 50 project stories
                Integer id = showStoryIds.get(i);
                Map<String, Object> story = restTemplate.getForObject(ITEM_URL, Map.class, id);

                if (story != null) {
                    String title = (String) story.get("title");
                    if (title != null && title.toLowerCase().contains(term.toLowerCase())) {
                        projects.add(story);
                    }
                }
            }
        }
        return projects;
    }

    /**
     * Pesquisa as principais histórias no Hacker News que contenham o termo especificado no título.
     *
     * @param term O termo de pesquisa.
     * @return Uma lista de URLs das histórias que correspondem ao termo de pesquisa.
     */
    public List<String> searchTopStories(String term) {
        List<String> urls = new ArrayList<>();
        RestTemplate restTemplate = new RestTemplate();

        try {
            List<Integer> topStoryIds = restTemplate.getForObject(TOP_STORIES_URL, List.class);

            if (topStoryIds != null) {
                for (int i = 0; i < Math.min(topStoryIds.size(), 100); i++) {
                    Integer id = topStoryIds.get(i);
                    Map<String, Object> story = restTemplate.getForObject(ITEM_URL, Map.class, id);
                    if (story != null) {
                        String title = (String) story.get("title");
                        String url = (String) story.get("url");

                        if (title != null && title.contains(term)) {
                            urls.add(url);
                        }
                    }
                }
            }
        } catch (Exception e) {
            logger.severe("Error fetching top stories: " + e.getMessage());
        }

        return urls;
    }

}