package com.example.gogool.rmi;

import java.rmi.NotBoundException;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;
import java.util.Map;

/**
 * Interface RMIGateway define os métodos disponíveis para interação remota com o gateway,
 * permitindo realizar pesquisas, gerenciar user, obter estatísticas e registar barrels de armazenamento.
 */
public interface RMIGateway extends Remote {

    List<String> search(String term) throws RemoteException;

    String search2(String url) throws RemoteException;

    String registerUser(String username, String password) throws RemoteException, NotBoundException;

    String logIn(String username, String password) throws Exception;

    List<String> getTopSearches() throws RemoteException;
    List<String> getActiveBarrels() throws RemoteException;
    Map<String, Double> getAverageResponseTimes() throws RemoteException;
    void registerBarrel(RMIStorageBarrel barrel) throws RemoteException;

    void updateEstateBarrel(RMIStorageBarrel remoteRef) throws RemoteException;
    String addUrl(String url) throws RemoteException;

}