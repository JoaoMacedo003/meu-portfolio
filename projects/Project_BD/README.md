
## Overview of the Contents
Python - Source code da aplicação web onde corre o server, tem definidos endpoints para o requests HTTP do tipo (POST,GET,PUT) e é onde está definida a lógica de como é feita a interação com a base de dados, neste caso utilizamos uma base de dados PostgresSQL daí a utilização da biblioteca psycopg2
Para dar start no web server basta correr o ficheiro python diretamente do terminal


Postman - O ficheiro dentro da pasta postman contém uma collection que é utilizada para testar os diferentes endpoints do Web Server e as diferentes funcionalidades da base de dados.
Para utilizar a collection importe a mesma dentro do postman.


## Requirements
Para executar este projeto é preciso ter as seguites bibliotecas instaladas:
flask:pip install flask
Psycopg2:pip install psycopg2
Flask JSON:pip install flask-json
JWT:pip install pyjwt
Dateutil:pip install python-dateutil
Flask JWT Extended:pip install flask-jwt-extended
Bcrypt:pip install bcrypt


## Como testar a base de dados e executar a collection fornecida:

1º - Correr o script inicial da base de dados para criar todas as tabelas e relações;
2º - Abir o prompt de comando ou terminal dependendo do seu Sistema Operativo onde possa executar o ficheiro MindStream.py. Uma vez aberto, vá até ao diretório com o ficheiro de código e execute com o comando "python .\MindStream_api.py";
3º - Agora no Postman, supondo que já fez o import da collectio "Stream_demo", pode começar a testar os vários end_points. Em caso de dúvida poderá sempre consultar o manual de utilizador;
4 º - Testar todos os requests dentro das pastas "Admin-1" e "Admin_2" para criar alguns administradores, artistas e gerar alguns dos diferentes tipos de cartões de crédito a utilizar para poder subscrever ao premium;
5º -  Testar todos os requests dentro das pastas "Artist MIGUELLL related" e "Artist BISPO related". Note que no endpoint add album, caso queira adicionar uma música existente ao album terá que inserir um id de música válido para esta poder funcionar;
6º - Testar todos os requests na pasta Registrate Users.
7º - Testar todos os requests dentro das pastas "User Sara_03 Related", "User Mikas Related" e "User Ana related". Os vários endpoints relativos aos consumidores podem ser testados aqui, tenha em atenção que em certos casos precisa de alterar os valores nas variáveis para valores existentes na base de dados para estes poderem funcionar.