-- Servidor

Sintaxe de execução: ./server/server <PORTA_TCP/NEWS> <PORTA_UDP/CONFIG> <LOGINS/FICHEIRO>
Exemplo: ./server/server 9000 9001 credentials

-- Cliente

Sintaxe de execução: ./client/client <IP_SERVER/NEWS> <PORTA_TCP/NEWS>
Exemplo: ./client/client 193.137.100.1 9000

-- Makefile

Sintaxe de execução: make
Limpeza dos ficheiros: make clean