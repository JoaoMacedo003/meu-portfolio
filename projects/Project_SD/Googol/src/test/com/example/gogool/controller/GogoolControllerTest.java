package com.example.gogool.controller;

import com.example.gogool.rmi.RMIGateway;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;

import java.rmi.RemoteException;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@SpringBootTest
public class GogoolControllerTest {

	@Mock
	private RMIGateway gateway;

	@InjectMocks
	private GogoolController gogoolController;

	@Value("${gateway.rmi.host}")
	private String rmiHost;

	@Value("${gateway.rmi.port}")
	private int rmiPort;

	@BeforeEach
	public void setUp() {
		MockitoAnnotations.openMocks(this);
	}

	@Test
	public void testAddUrl() throws RemoteException {
		when(gateway.addUrl(anyString())).thenReturn("URL added successfully");

		String response = gogoolController.addUrl("http://example.com");
		assertEquals("URL added successfully", response);
	}


	@Test
	public void testGetStats() throws RemoteException {
		when(gateway.getTopSearches()).thenReturn(List.of("example"));
		when(gateway.getAverageResponseTimes()).thenReturn(Map.of("Barrel1", 100.0));
		when(gateway.getActiveBarrels()).thenReturn(List.of("Barrel1"));

		Map<String, Object> stats = gogoolController.getStats();
		assertEquals(1, ((List<?>) stats.get("topSearches")).size());
		assertEquals(1, ((Map<?, ?>) stats.get("averageResponseTimes")).size());
		assertEquals(1, ((List<?>) stats.get("activeBarrels")).size());
	}
}
