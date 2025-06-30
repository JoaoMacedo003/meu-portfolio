#include <stdio.h>
#include "header_file.h"
#include <stdlib.h>
#include <string.h>

int main() {
    // Ficheiro:
    FILE *f;
    f= fopen("dados.txt","r");
    FILE *fd;
    fd= fopen("despesas.txt","r");
    if (f==NULL){
        printf("Erro: Nao foi possivel read o ficheiro.\n");
        return 0;
    }
    if (fd==NULL){
        printf("Erro: Nao foi possivel read o ficheiro de despesas.\n");
        return 0;
    }

    char *read = (char*)malloc(50 * sizeof(char));
    // Ler ficheiro de dados:
    pLista_aluno lista_alunos=cria();
    int n=1;
    while(fgets(read, 50, f) != NULL){
        aluno auxaluno;
        if(n==1){
            read[(int) strlen(read) - 1] = '\0';
            strcpy(auxaluno.nome, read);
        }
        if(n==2){
            char *ptr;
            ptr = strtok(read, "/");                    //"strtok" --- lê string até um determinado caractér
            auxaluno.data_nascimento.dia = str_i(ptr);       //função que transforma uma string num inteiro
            ptr = strtok(NULL,"/");
            auxaluno.data_nascimento.mes = str_i(ptr);
            ptr = strtok(NULL,"/");
            auxaluno.data_nascimento.ano = str_i(ptr);
        }
        if(n==3){
            auxaluno.ano = str_i(read);
        }
        if(n==4){
            read[(int) strlen(read) - 1] = '\0';
            strcpy(auxaluno.turma, read);
        }
        if(n==5){
            auxaluno.numero = str_i(read);
        }
        if(n==6){
            char *ptr;
            auxaluno.saldo = strtod(read, &ptr);  //Passa de string para double
        }
        if(strcmp("\n", read) == 0){      // compara as duas strings
            n=0;
            insere(lista_alunos,auxaluno);
        }
        n++;
    }

    // Ler ficheiro de despesas:
    pLista_despesas lista_despesas=cria_d();
    n=1;
    while(fgets(read, 50, fd) != NULL) {
        despesa auxdespesa;
        if (n == 1) {
            auxdespesa.numero = str_i(read);
        }
        if (n == 2) {
            char *ptr;
            auxdespesa.valor = strtod(read, &ptr);
        }
        if (n==3){
            read[(int) strlen(read) - 1] = '\0';
            strcpy(auxdespesa.descricao, read);
        }
        if (n == 4){
            char *ptr;
            ptr = strtok(read, "/");                    //"strtok" --- lê string até um determinado caractér
            auxdespesa.data1.dia = str_i(ptr);       //função que transforma uma string num inteiro
            ptr = strtok(NULL,"/");
            auxdespesa.data1.mes = str_i(ptr);
            ptr = strtok(NULL,"/");
            auxdespesa.data1.ano = str_i(ptr);
        }
        if(strcmp("\n", read) == 0){      // compara as duas strings
            n=0;
            insere_d(lista_despesas,auxdespesa);
        }
        n++;
    }
    fclose(f);
    fclose(fd);

    //-------------------------------------------------------------------------//

    int resposta;
    printf("\n---------------------------------------------\nQue operacao deseja realizar?\n1)Introduzir dados de um aluno.\n2)Eliminar um aluno existente.\n3)Listar todos os alunos por ordem alfabetica.\n4)Listar todos os alunos com saldo abaixo de um determinado valor.\n5)Apresentar toda a informacao de um determinado aluno.\n6)Efetuar uma despesa por um determinado aluno.\n7)Carregar a conta de um aluno com um valor.\n8)Transferir saldo de um aluno para outro determinado aluno.\nDigite 0 para sair:\n---------------------------------------------\n");
    scanf("%d",&resposta);
    int num_aluno;

    while(resposta!=0)
    {
        switch (resposta)
        {

            case 1:
                printf("Insira os dados do novo aluno:\n");
                aluno nv_aluno = inserir_dados_aluno();
                insere(lista_alunos,nv_aluno);
                break;

            case 2:
                printf("Qual o numero do aluno que deseja eliminar:");
                scanf("%d", &num_aluno);
                aluno aluno1;
                aluno1.numero = num_aluno;
                elimina(lista_alunos, aluno1.numero);
                break;

            case 3:
                listagem_alfabetica(lista_alunos);
                break;

            case 4:
                printf("Insira o valor do saldo que deseja:\n");
                double valor;
                scanf("%lf",&valor);
                listar_saldo(lista_alunos,valor);
                break;

            case 5:
                printf("Insira o numero do aluno:\n");
                int num;
                scanf("%d",&num);
                imprimir_aluno(lista_alunos,lista_despesas,num);
                break;

            case 6:
                printf("Insira o numero do aluno:\n");
                scanf("%d",&num);
                int v = verifica_existencia(num, lista_alunos);
                if(v == 1) {
                    printf("Insira o valor da despesa:\n");
                    scanf("%lf", &valor);
                    if(valor<=0){break;}
                    efetuar_despesa(lista_despesas, lista_alunos, num, valor);
                }else{
                    printf("O aluno nao existe!");
                }
                break;

            case 7:
                printf("Insira o valor que deseja carregar:\n");
                scanf("%lf",&valor);
                carregar_saldo(lista_alunos,valor);
                break;

            case 8:
                printf("Insira o numero do aluno que ira transferir:\n");
                int num1,num2;
                scanf("%d",&num1);
                int r = verifica_existencia(num1, lista_alunos);
                if(r!=1) {
                    do {
                        printf("Erro: O aluno nao existe.\nInsira novamente:");
                        scanf("%d", &num1);
                        r = verifica_existencia(num1, lista_alunos);
                    }   while (r != 1);
                }
                printf("Digite o numero do aluno destinado:\n");
                scanf("%d", &num2);
                int q = verifica_existencia(num2, lista_alunos);
                if(q!=1) {
                    do {
                        printf("Erro: O aluno nao existe.\nInsira novamente:");
                        scanf("%d", &num2);
                        q = verifica_existencia(num2, lista_alunos);
                    }   while (q != 1);
                }
                printf("Quantia a ser transferida:\n");
                scanf("%lf",&valor);
                transferir_saldo(lista_alunos,lista_despesas,num1,num2,valor);
                break;

        }
        if(resposta==1||resposta==2||resposta==6||resposta==7||resposta==8){
            f = fopen("dados.txt","w");
            fd = fopen("despesas.txt","w");
            guardar(f,lista_alunos);
            guardar_d(fd,lista_despesas);
            printf("\nDados guardados com sucesso.\n");
            fclose(f);
            fclose(fd);
        }
        printf("\n---------------------------------------------\nQue operacao deseja realizar?\n1)Introduzir dados de um aluno.\n2)Eliminar um aluno existente.\n3)Listar todos os alunos por ordem alfabetica.\n4)Listar todos os alunos com saldo abaixo de um determinado valor.\n5)Apresentar toda a informacao de um determinado aluno.\n6)Efetuar uma despesa por um determinado aluno.\n7)Carregar a conta de um aluno com um valor.\n8)Transferir saldo de um aluno para outro determinado aluno.\nDigite 0 para sair:\n---------------------------------------------\n");
        scanf("%d",&resposta);
    }
    f = fopen("dados.txt","w");
    fd = fopen("despesas.txt","w");
    guardar(f,lista_alunos);
    guardar_d(fd,lista_despesas);
    printf("Dados guardados com sucesso.\n");
    fclose(f);
    fclose(fd);
}


