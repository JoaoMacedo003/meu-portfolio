
## Overview of the Contents
Python - Source code da aplicação web onde corre o server, tem definidos endpoints para o requests HTTP do tipo (POST,GET,PUT) e é onde está definida a lógica de como é feita a interação com a base de dados, neste caso utilizamos uma base de dados PostgresSQL daí a utilização da biblioteca psycopg2
Para dar start no web server basta correr o ficheiro python diretamente do terminal


Postman - O ficheiro dento da pasta postman contém uma collection que é utilizada para testar os diferentes endpoints do Web Server e as diferentes funcionalidades da base de dados
Para utilizar a collection importe a mesma dentro do postman


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

1º - Correr o script inicial da base de dados para criar todas as tabelas e relações
3º - Criar o primeiro administrador dentro da base de dados, este é o unico que precisa ser criado diretamente na base de dados, para tal utilize os seguintes comandos:
INSERT INTO users (username, email, password) VALUES ('admin', 'admin@example.com', 'securepassword');
INSERT INTO administrator (number_cards, users_user_id) VALUES (0, X); sendo o X o valor do user_id criado na tabela 
4 º - Testar todos os requests dentro da pasta Admin-1 e Admin_2 para criar alguns administradores novos, artistas e gerar alguns dos cartões de crédito a utilizar para subscrever ao premium.
5º -  Depois continuar a testar os request mantendo a ordem das pastas