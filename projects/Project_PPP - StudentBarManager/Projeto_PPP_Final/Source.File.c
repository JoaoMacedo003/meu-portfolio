#include <stdio.h>
#include "header_file.h"
#include <stdlib.h>
#include <string.h>

//------------------------------------------------------------------------//

// Passa strings para inteiros:
int str_i(const char *d){
    int i=0, numero=0;
    while (d[i] != '\0'){
        if(('0'<=d[i] && d[i]<='9')) numero = numero*10 + (d[i]-'0');
        i++;
    } if(d[0] == '-') numero *= -1;
    return numero;
}

//Verifica se o aluno existe pelo numero:
int verifica_existencia(int num, pLista_aluno lista){
    pLista_aluno auxlista = lista;
    do {
        if (num == (auxlista->alunoLista.numero)) {
            return 1;
        }
        auxlista = auxlista->prox;
    } while (auxlista != NULL);
}

// Lista De Alunos:
pLista_aluno cria(){
    pLista_aluno aluno;
    struct aluno a1 = {"",{0,0,0},0,"",0,0.0,0};
    aluno = (pLista_aluno) malloc(sizeof(noLista_aluno));
    if(aluno != NULL){
        aluno->alunoLista = a1;
        aluno->prox = NULL;
    }
}

//Insere o aluno na Lista de alunos:
void insere (pLista_aluno lista, struct aluno a1){
    pLista_aluno aux,ant,inutil;
    aux = (pLista_aluno) malloc(sizeof (noLista_aluno));
    if(aux != NULL){
        aux->alunoLista = a1;
        procura(lista,a1.numero,&ant,&inutil);
        aux->prox = ant->prox;
        ant->prox = aux;
    }
}

//Procura o numero do aluno e o anterior a ele:
void procura (pLista_aluno lista, int numero, pLista_aluno *ant, pLista_aluno *atual){
    *ant = lista;
    *atual = lista->prox;
    while((*atual)!=NULL && (*atual)->alunoLista.numero < numero){
        *ant=*atual;
        *atual=(*atual)->prox;
    }
    if((*atual)!=NULL && (*atual)->alunoLista.numero != numero){
        *atual=NULL;
    }
}

// Lista de Despesas para cada Aluno
pLista_despesas cria_d(){
    pLista_despesas aux;
    struct despesa d1 ={0,0,"",{0,0,0}};
    aux= (pLista_despesas)malloc(sizeof(noLista_despesa));
    if(aux!=NULL){
        aux->despesaLista=d1;
        aux->prox=NULL;
    }
}

//Procura a Despesa:
void procura_d(pLista_despesas lista,double chave,pLista_despesas *ant,pLista_despesas *atual){
    *ant=lista;
    *atual=lista->prox;
    while((*atual)!=NULL && (*atual)->despesaLista.numero<chave){
        *ant=*atual;
        *atual=(*atual)->prox;
    }
    if((*atual)!=NULL && (*atual)->despesaLista.numero!=chave){
        *atual=NULL;
    }
}

//Insere a Despesa na Lista de despesas:
void insere_d (pLista_despesas lista,despesa d1){
    pLista_despesas no,ant,inutil;
    no=(pLista_despesas) malloc (sizeof (noLista_despesa));
    if(no!=NULL){
        no->despesaLista=d1;
        procura_d(lista,d1.numero,&ant,&inutil);
        no->prox=ant->prox;
        ant->prox=no;
    }
}

//------------------------------------------------------------------------//

// 1) Introduzir dados de um novo aluno:
aluno inserir_dados_aluno(){
    aluno a;
    printf("Insira o nome do aluno:\n");
    scanf("%c",(char*) stdin);
    fgets(a.nome,50,stdin);
    a.nome[strlen(a.nome)-1]='\0';
    printf("Introduza a data de nascimento do aluno: (DD/MM/AA)\n");
    scanf("%d/%d/%d",&a.data_nascimento.dia,&a.data_nascimento.mes,&a.data_nascimento.ano);
    printf("Insira o ano do aluno:\n");                                                               //Falta adicionar depois ao documento de texto
    scanf("%d",&a.ano);
    printf("Insira a turma do mesmo:\n");
    scanf("%s",a.turma);
    printf("Introduza o numero do aluno:\n");
    scanf("%d",&a.numero);
    printf("Insira o saldo do aluno:\n");
    scanf("%lf",&a.saldo);
    //Erros:
    if(a.data_nascimento.mes<0||a.data_nascimento.mes>12){
        printf("\nErro: Mes inserido invalido\nDigite novamente:");
        scanf("%d",&a.data_nascimento.mes);
    }
    if(a.data_nascimento.mes==1||a.data_nascimento.mes==3||a.data_nascimento.mes==5||a.data_nascimento.mes==7||a.data_nascimento.mes==8||a.data_nascimento.mes==10||a.data_nascimento.mes==12){
        if(a.data_nascimento.dia>31){
            printf("\nErro: Dia inserido invalido (Mes inserido: %d).\nDigite novamente:",a.data_nascimento.mes);
            scanf("%d",&a.data_nascimento.dia);
        }
    }
    if(a.data_nascimento.mes==4||a.data_nascimento.mes==6||a.data_nascimento.mes==9||a.data_nascimento.mes==11){
        if(a.data_nascimento.dia>30){
            printf("\nErro: Dia inserido invalido (Mes inserido: %d).\nDigite novamente:",a.data_nascimento.mes);
            scanf("%d",&a.data_nascimento.dia);
        }
    }
    if(a.data_nascimento.mes==2){
        if(a.data_nascimento.dia>29){
            printf("Erro: Dia inserido invalido (Mes inserido: %d).\nDigite novamente:",a.data_nascimento.mes);
            scanf("%d",&a.data_nascimento.dia);
        }
    }
    if(a.saldo<0.0){
        printf("\nErro: Saldo invalido (Saldo inserido: %lf).\nDigite novamente:",a.saldo);
        scanf("%lf",&a.saldo);
    }
    return  a;
}

//------------------------------------------------------------------------//

// 2) Eliminar um aluno existente:
void elimina (pLista_aluno lista, int chave){
    pLista_aluno anterior,atual;
    procura(lista,chave,&anterior,&atual);   /*Procura-se o número que se pretende eliminar e do anterior a ele*/
    if(atual != NULL){
        anterior->prox = atual->prox;
        free(atual);
    }
}

//------------------------------------------------------------------------//

//3)Listar todos os alunos por ordem alfabética.
void listagem_alfabetica(pLista_aluno lista) {
    pLista_aluno auxlista = lista, auxlista1 = lista; int contador = 0;
    do {
        contador = contador + 1;
        auxlista1 = auxlista1->prox;
    } while (auxlista1 != NULL);
    contador = contador - 1;
    char nomes[contador][50];
    for (int i = 0; i < contador; ++i) {
        auxlista = auxlista->prox;
        strcpy(nomes[i],auxlista->alunoLista.nome);
    }
    char aux[50];
    for (int i = 0; i < contador-1; ++i) {
        for (int j = i+1; j < contador; ++j) {
            if(strcmp(nomes[i],nomes[j]) > 0){
                strcpy(aux,nomes[i]);
                strcpy(nomes[i],nomes[j]);
                strcpy(nomes[j],aux);
            }
        }
    }
    for (int i = 0; i <= contador; ++i) {
        printf("--%s--",nomes[i]);
    }
}

//------------------------------------------------------------------------//
// 4) Listar todos os alunos com saldo inferior a um determinado valor:
void listar_saldo(pLista_aluno lista, double valor){
    pLista_aluno auxlista1 = lista; pLista_aluno auxlista2 = lista; pLista_aluno auxlista3 = lista ;
    double aux = valor, aux1 = 0;
    int contador = 0;                               //Conta o número de alunos com valor de saldo inferior ao selecionado
    do {
        if (aux > (auxlista1->alunoLista.saldo)) {
            contador = contador + 1;
        }
        auxlista1 = auxlista1->prox;
    } while (auxlista1 != NULL);
    contador = contador-1;             //É retirado o primeiro aluno pois esse não conta (aluno a1 na função que cria a lista)
    if(auxlista2 != NULL) {
        do {
            if (valor != auxlista2->alunoLista.saldo && aux > auxlista2->alunoLista.saldo && aux1 < auxlista2->alunoLista.saldo) {
                aux1 = auxlista2->alunoLista.saldo;
                auxlista3 = auxlista2;
            }
            auxlista2 = auxlista2->prox;
            if (contador != 0 && auxlista2 == NULL) {
                aux = aux1;
                printf("-- %s --", auxlista3->alunoLista.nome);
                aux1 = 0;
                auxlista2 = lista->prox;
                contador = contador - 1;
            }
        } while (contador != 0);     // o ciclo vai ser repetido o número de vezes guardado na variável "contador", onde em cada imprime o nome da pessoa com o maior saldo inferior ao valor selecionado
    }else{
        printf("A lista está vazia!");
    }
}

//------------------------------------------------------------------------

// 5)Apresentar toda a informacao de um determinado aluno.
aluno imprimir_aluno(pLista_aluno lista,pLista_despesas lista1, int num) {
    aluno a;
    pLista_aluno ant, atual;
    procura(lista, num, &ant, &atual);
    a = atual->alunoLista;
    printf("Nome: %s\nData de nascimento: %d/%d/%d\nAno: %d\nTurma: %s\nNumero: %d\nSaldo: %.2lf\n", a.nome,
           a.data_nascimento.dia, a.data_nascimento.mes, a.data_nascimento.ano, a.ano, a.turma, a.numero, a.saldo);
    pLista_despesas auxlista_d = lista1;
    do {
        if(auxlista_d->despesaLista.numero == num) {
            printf("Despesa: ---- Valor:%lf ---- Descricao:%s ---- Data: %d/%d/%d\n", auxlista_d->despesaLista.valor, auxlista_d->despesaLista.descricao, auxlista_d->despesaLista.data1.dia,
                   auxlista_d->despesaLista.data1.mes, auxlista_d->despesaLista.data1.ano);
        }
        auxlista_d = auxlista_d->prox;
    }while(auxlista_d!=NULL);
}

//------------------------------------------------------------------------

// 6)Efetuar uma despesa por um determinado aluno.
aluno efetuar_despesa(pLista_despesas lista, pLista_aluno listaA, int num, double valor){
    pLista_aluno ant,atual;
    procura(listaA,num,&ant,&atual);
    (atual)->alunoLista.saldo=(atual)->alunoLista.saldo-valor;
    despesa d1;
    d1.valor=valor;
    d1.numero=num;
    printf("Descricao:\n");
    scanf("%c",(char*) stdin);
    fgets(d1.descricao,50,stdin);
    d1.descricao[strlen(d1.descricao)-1]='\0';
    printf("Data: (DD/MM/AA)\n");
    scanf("%d/%d/%d",&d1.data1.dia,&d1.data1.mes,&d1.data1.ano);
    insere_d(lista,d1);
}


//------------------------------------------------------------------------

// 7) Carregar  a conta de um aluno com um valor:
aluno carregar_saldo(pLista_aluno lista, double valor){
    int num;
    printf("Insira o numero do aluno:\n");
    scanf("%d",&num);
    int v = verifica_existencia(num, lista);
    if(v == 1) {
        pLista_aluno ant,atual;
        procura(lista,num,&ant,&atual);
        if (valor>0){
            (atual)->alunoLista.saldo+=valor;
        }
        else{
            do {
                printf("Erro: Inseriu um valor invalido.\nInsira o valor para carregar:\n");
                scanf("%lf", &valor);
                (atual)->alunoLista.saldo+=valor;
            }   while(valor<=0);
        }
    }else{
        printf("O aluno nao existe!");
    }
}
//------------------------------------------------------------------------
// 8)Transferir Saldo:
aluno efetuar_transferencia(pLista_despesas lista, pLista_aluno listaA, int num, double valor){
    pLista_aluno ant,atual;
    procura(listaA,num,&ant,&atual);
    (atual)->alunoLista.saldo=(atual)->alunoLista.saldo-valor;
    despesa d1;
    d1.valor=valor;
    d1.numero=num;
    strcpy(d1.descricao,"Transferencia");
    printf("Data: (DD/MM/AA)\n");
    scanf("%d/%d/%d",&d1.data1.dia,&d1.data1.mes,&d1.data1.ano);
    insere_d(lista,d1);
}
aluno transferir(pLista_aluno lista,int num, double valor){
    pLista_aluno ant,atual;
    procura(lista,num,&ant,&atual);
    if (valor>0){
        (atual)->alunoLista.saldo+=valor;
    }
    else{
        do {
            printf("Erro: Inseriu um valor invalido.\nInsira o valor para carregar:\n");
            scanf("%lf", &valor);
            (atual)->alunoLista.saldo+=valor;
        }   while(valor<=0);
    }
}
aluno transferir_saldo(pLista_aluno lista,pLista_despesas listaD,int num1,int num2,double valor){
    pLista_aluno ant,atual;
    procura(lista,num1,&ant,&atual);
    aluno a1;
    a1=atual->alunoLista;
    efetuar_transferencia(listaD,lista,num1,valor);
    procura(lista,num2,&ant,&atual);
    aluno a2;
    a2=atual->alunoLista;
    transferir(lista,num2,valor);
    printf("Foi transferido %0.2lf de %s para %s\n",valor,a1.nome,a2.nome);
}

//------------------------------------------------------------------------
// 8)Guardar dados:
void guardar(FILE *f, pLista_aluno lista){
    pLista_aluno auxlista = lista->prox;
    while(auxlista != NULL){
        fprintf(f,"%s\n%d/%d/%d\n%d\n%s\n%d\n%lf\n\n",auxlista->alunoLista.nome,auxlista->alunoLista.data_nascimento.dia,auxlista->alunoLista.data_nascimento.mes,auxlista->alunoLista.data_nascimento.ano,auxlista->alunoLista.ano,
                auxlista->alunoLista.turma,auxlista->alunoLista.numero,auxlista->alunoLista.saldo);
        auxlista = auxlista->prox;
    }
}
void guardar_d(FILE *f,pLista_despesas lista){
    pLista_despesas aux=lista->prox;
    while(aux != NULL) {
        fprintf(f, "%d\n%lf\n%s\n%d/%d/%d\n\n", aux->despesaLista.numero, aux->despesaLista.valor,
                aux->despesaLista.descricao, aux->despesaLista.data1.dia, aux->despesaLista.data1.mes,
                aux->despesaLista.data1.ano);
        aux = aux->prox;
    }
}

//------------------------------------------------------------------------