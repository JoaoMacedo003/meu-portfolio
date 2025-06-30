#ifndef PROJETOPPP_HEADER_FILE_H
#define PROJETOPPP_HEADER_FILE_H

#include <stdio.h>


typedef struct data{
    int dia;
    int mes;
    int ano;
}data;


typedef struct despesa{
    int numero;
    double valor;
    char descricao[50];
    data data1;
}despesa;


typedef struct noLista_despesa{
    despesa despesaLista;
    struct noLista_despesas * prox;
}   noLista_despesa;

typedef noLista_despesa *pLista_despesas;


typedef struct aluno{
    char nome[50];
    data data_nascimento;
    int ano;
    char turma[10];
    int numero;
    double saldo;
}   aluno;


typedef struct noLista_aluno{
    aluno alunoLista;
    struct noLista_aluno *prox;
}   noLista_aluno;

typedef noLista_aluno *pLista_aluno;



//Lista_alunos:
pLista_aluno cria();
void insere(pLista_aluno lista, aluno a1);
void procura (pLista_aluno lista, int numero, pLista_aluno *ant, pLista_aluno *atual);

// Lista de despesas
pLista_despesas cria_d();
void insere_d (pLista_despesas lista,despesa d1);

//Funcoes:
int str_i(const char *d);
int verifica_existencia(int num, pLista_aluno lista);
aluno inserir_dados_aluno();
void elimina (pLista_aluno lista, int chave);
void listagem_alfabetica(pLista_aluno lista);
void listar_saldo(pLista_aluno lista, double valor);
aluno imprimir_aluno(pLista_aluno lista, pLista_despesas lista1, int num);
aluno efetuar_despesa(pLista_despesas lista, pLista_aluno listaA, int num, double valor);
aluno carregar_saldo(pLista_aluno lista, double valor);
aluno efetuar_transferencia(pLista_despesas lista, pLista_aluno listaA, int num, double valor);
aluno transferir(pLista_aluno lista,int num, double valor);
aluno transferir_saldo(pLista_aluno lista,pLista_despesas listaD,int num1,int num2,double valor);
void guardar(FILE *f, pLista_aluno lista);
void guardar_d(FILE *f,pLista_despesas lista);

#endif //PROJETOPPP_HEADER_FILE_H
