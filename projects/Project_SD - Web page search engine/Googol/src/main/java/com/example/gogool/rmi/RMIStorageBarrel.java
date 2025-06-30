package com.example.gogool.rmi;

import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 * Interface para definir os métodos disponíveis em um barrel de armazenamento acessível via RMI.
 * Os métodos permitem a pesquisa por palavras ou URLs, registo e login de usuários, e a obtenção do identificador do barrel.
 */
public interface RMIStorageBarrel extends Remote {
    String searchWord(String word) throws RemoteException;

    String searchUrl(String url) throws RemoteException;

    String logIn(String username, String password) throws Exception;

    String registerUser(String username, String password) throws RemoteException;

    String getBarrelId() throws  RemoteException;

    void setBarrelId(String id) throws RemoteException;
}