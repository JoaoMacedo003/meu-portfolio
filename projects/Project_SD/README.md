# Gogool Project

Este projeto é um aplicativo Spring Boot chamado Gogool. O projeto inclui dependências do Spring Boot, Jsoup, JSON Web Token e outras.

## Pré-requisitos

Antes de iniciar, você precisará ter os seguintes softwares instalados:

- **Java Development Kit (JDK) 21**: Certifique-se de que o JDK 21 está instalado e configurado corretamente no seu sistema.
- **Apache Maven 3.8.1 ou superior**: Siga as instruções abaixo para instalar o Maven.

## Instalação do Maven

### Windows

1. Baixe a última versão do Maven em: [Maven Downloads](https://maven.apache.org/download.cgi)
2. Extraia o arquivo baixado para um diretório de sua escolha, por exemplo: `C:\Program Files\Apache\Maven`.
3. Configure a variável de ambiente `MAVEN_HOME` apontando para o diretório de instalação do Maven.
4. Adicione o diretório `bin` do Maven à variável de ambiente `PATH`. Por exemplo: `C:\Program Files\Apache\Maven\bin`.
5. Abra um novo terminal ou prompt de comando e verifique a instalação com o comando:
   ```sh
   mvn -version

## Executando o Projeto Gogool

Para executar o projeto Gogool, siga estes passos detalhados abaixo.

### Preparação

1. **Abrir o Terminal**: Abra o terminal ou prompt de comando no seu computador.

2. **Navegar até a pasta do projeto**:
   Utilize o comando para navegar até o diretório do projeto Gogool:
   cd caminho_para_pasta_Gogool

3. Para limpar, instalar e empacotar o projeto, execute os seguintes comandos Maven:
   mvn clean install
   mvn clean package

4. Para correr os diferenttes componentes do projeto:
   mvn exec:java@run-gateway
   mvn exec:java@run-downloader -> Podem existir vários
   mvn exec:java@run-indexstoragebarrel -> Podem existir vários
   mvn spring-boot:run

### Correr o projeto em diferentes máquinas

É possível correr o projeto em diferentes máquinas.

Primeiro é necessário estar na mesma rede local e ter a firewall desativada.

Para isso é preciso definir nos ficheiros config.txt e application.properties os ips respetivos das máquinas onde os compomnentes estão a correr.

Exemplo:
-Gateway e WebServer -> 1ºmáquina
-Downloader e IndexStorageBarrel -> 2ºmáquina

Para aceder ao WebServer basta chegar no seu browser e colocar "https://<"ip da maquina que corre o WebServer">:8443"
É possivél aceder ao WebServer a partir de um telémovel também.
