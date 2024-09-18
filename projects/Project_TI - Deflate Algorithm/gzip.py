# Author: Marco Simoes
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

# Modificado por Miguel Leopoldo, João Macedo e Johnny Fernandes, LEI, 2022
# COMENTÁRIOS CRIADOS/MODIFICADOS PELOS ESTUDANTES (CAPS LOCK)

# IMPORTAÇÕES
import sys
from huffmantree import HuffmanTree
import numpy as np


# CLASSE PARA TRATAR O CABEÇALHO DO ARQUIVO GZIP
class GZIPHeader:
    # CLASSE PARA GUARDAR TODOS OS CAMPOS DO CABEÇALHO EM VARIÁVEIS
    ID1 = ID2 = CM = FLG = XFL = OS = 0
    MTIME = []
    lenMTIME = 4
    mTime = 0

    # INICIALIZAÇÃO DAS FLAGS DO CABEÇALHO DO FICHEIRO GZIP
    FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0

    XLEN, extraField = [], []
    lenXLEN = 2

    # SE FLG_FNAME == 1 ENTÃO O NOME É GUARDADO EM fName
    fName = ''  # TERMINA QUANDO É LIDO UM BYTE A 0. NULL-TERMINATOR

    # SE FLG_FCOMMENT == 1 ENTÃO O COMENTÁRIO É GUARDADO EM fComment
    fComment = ''  # TERMINA QUANDO É LIDO UM BYTE A 0. NULL-TERMINATOR

    # SE FLG_HCRC == 1 ENTÃO EXISTE UM CHECKSUM CRC-32 E É GUARDADO EM HCRC
    HCRC = []

    def read(self, f):
        # LÊ E PROCESSA O CABEÇALHO DO GZIP. RETORNA 0 SE NÃO ORIGINAR ERROS, -1 CASO CONTRÁRIO

        # VALORES FIXOS DO GZIP
        self.ID1 = f.read(1)[0]
        if self.ID1 != 0x1f:
            return -1  # ERRO NO HEADER

        # VALORES FIXOS DO GZIP
        self.ID2 = f.read(1)[0]
        if self.ID2 != 0x8b:
            return -1  # ERRO NO HEADER

        # MÉTODO DE COMPRESSÃO. DEFLATE = 0x08
        self.CM = f.read(1)[0]
        if self.CM != 0x08:
            return -1  # ERRO NO HEADER

        # FLAGS
        self.FLG = f.read(1)[0]

        # DATA DE MODIFICAÇÃO DO FICHEIRO ORIGINAL
        self.MTIME = [0] * self.lenMTIME
        self.mTime = 0
        for i in range(self.lenMTIME):
            self.MTIME[i] = f.read(1)[0]
            self.mTime += self.MTIME[i] << (8 * i)

        # NÍVEL DE COMPRESSÃO (GUARDADO MAS NÃO PROCESSADO)
        self.XFL = f.read(1)[0]

        # SISTEMA OPERATIVO (GUARDADO MAS NÃO PROCESSADO)
        self.OS = f.read(1)[0]

        # VERIFICA AS FLAGS
        self.FLG_FTEXT = self.FLG & 0x01
        self.FLG_FHCRC = (self.FLG & 0x02) >> 1
        self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
        self.FLG_FNAME = (self.FLG & 0x08) >> 3
        self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4

        # FLG_EXTRA
        if self.FLG_FEXTRA == 1:
            # 1º BYTE: LSB, 2º BYTE: MSB
            self.XLEN = [0] * self.lenXLEN
            self.XLEN[0] = f.read(1)[0]
            self.XLEN[1] = f.read(1)[0]

            # read extraField and ignore its values
            self.extraField = f.read(self.XLEN[1] << 8 + self.XLEN[0])

        # FUNÇÃO QUE DETECTA NULL-TERMINATOR BYTE (BYTE A ZERO)
        def read_str_until_0(f):
            s = ''
            while True:
                c = f.read(1)[0]
                if c == 0:
                    return s
                s += chr(c)

        # FLG_FNAME - NOME DO FICHEIRO ORIGINAL
        if self.FLG_FNAME == 1:
            self.fName = read_str_until_0(f)

        # FLG_FCOMMENT - COMENTÁRIOS
        if self.FLG_FCOMMENT == 1:
            self.fComment = read_str_until_0(f)

        # FLG_FHCRC (GUARDADO MAS NÃO PROCESSADO)
        if self.FLG_FHCRC == 1:
            self.HCRC = f.read(2)

        return 0


def create_huffman_tree(codes, verbose=False):
    # FUNÇÃO PARA CRIAR UMA ÁRVORE DE HUFFMAN BASEADOS EM CÓDIGOS QUE SÃO PASSADOS À FUNÇÃO
    # USA HUFFMANTREE.PY ATRAVÉS DO IMPORT E DEVOLVE A ÁRVORE A SER USADA PELA FUNÇÃO QUE A CHAMA

    hft = HuffmanTree()
    for i in range(len(codes[0])):
        hft.addNode(codes[0][i], codes[1][i], verbose=verbose)
    return hft


def code_len_to_huffman_code(codes_len, literals):
    # FUNÇÃO PARA DESCODIFICAR OS CÓDIGOS DOS COMPRIMENTOS E OS SEUS VALORES LITERAIS. RETORNA DUAS LISTAS
    # UMA COM OS CÓDIGOS DE HUFFMAN A SEREM USADOS PARA INSERIR NA ÁRVORE DE HUFFMAN
    # OUTRA COM OS SEUS VALORES LITERAIS, A QUE DIZEM RESPEITO OS CÓDIGOS DE HUFFMAN

    # INICIALIZAÇÕES
    temp1 = []
    temp2 = []
    huffman_codes = []
    literal_val = []

    # REMOVE OS ZEROS DESNECESSÁRIOS E ATUALIZA OS PARÂMETROS PASSADOS
    for i in range(len(codes_len)):
        if codes_len[i] != 0:
            temp1 += [codes_len[i]]
            temp2 += [literals[i]]
    codes_len = temp1
    literals = temp2

    # CRIA UM DICIONÁRIO PARA NÃO SEREM PERDIDOS OS DADOS POSICIONAIS
    # A CHAVE DIZ RESPEITO AO VALOR LITERAL E O VALOR DIZ RESPEITO AO VALOR A QUE LHE ESTÁ ASSOCIADO
    codes_len_storedata = {}
    for i in range(len(codes_len)):
        codes_len_storedata[literals[i]] = codes_len[i]
    # REORGANIZAÇÃO DO DICIONÁRIO PARA PODER SER ITERADO POSTERIORMENTE
    sorted_codes_len_storedata = dict(sorted(codes_len_storedata.items(), key=lambda x: (x[1], x[0])))

    # INICIALIZAÇÕES
    # O TAMANHO DO CÓDIGO É GUARDADO COMO SENDO O ÚLTIMO. É POSTERIORMENTE ATUALIZADO
    min_dist = min(codes_len)
    last_dist = min_dist
    # BINÁRIO/CÓDIGO HUFFMAN
    code = 0

    # PARA CADA VALOR GUARDADO EM SORTED_CODES_LEN_STOREDATA
    for key in sorted_codes_len_storedata:
        # ATRIBUI O ATUAL
        current_dist = sorted_codes_len_storedata[key]

        # DEFINE MODO DE FORMATAÇÃO DO CÓDIGO HUFFMAN
        # O CÓDIGO É COMPOSTO PELO TAMANHO DO CÓDIGO EM FORMATO BINÁRIO
        # A CONTAGEM INCREMENTAL É FEITA PELA VARIÁVEL CODE
        format_dist = '{0:0' + str(current_dist) + 'b}'
        if current_dist == last_dist:
            # SE O TAMANHO DO CÓDIGO FOR IGUAL, ENTÃO CONVERTE O CODE EM BINÁRIO COM O TAMANHO RESPETIVO
            huffman_codes.append(format_dist.format(code))
            # GUARDA O VALOR A QUE DIZ RESPEITO NA LISTA DOS VALORES LITERAIS
            literal_val.append(key)
            # INCREMENTA CÓDIGO
            code += 1
            # DEFINE O ÚLTIMO VALOR COMO SENDO O VALOR ATUAL
            # POSTERIORMENTE PARA A PRÓXIMA KEY, O VALOR ATUAL SERÁ O PRÓXIMO VALOR, PODENDO COMPARAR O TAMANHO DE AMBOS
            last_dist = current_dist
        else:
            # CASO O TAMANHO DO CÓDIGO ATUAL FOR DIFERENTE DO CÓDIGO ANTERIOR, ENTÃO DÁ UM SHIFT PARA A ESQUERDA
            # A QUANTIDADE DE VEZES IGUAL À DIFERENÇA DOS TAMANHOS ENTRE UM E OUTRO
            code = code << current_dist - last_dist
            # CONVERTE O CODE EM BINÁRIO COM O TAMANHO RESPETIVO
            huffman_codes.append(format_dist.format(code))
            # GUARDA O VALOR A QUE DIZ RESPEITO NA LISTA DOS VALORES LITERAIS
            literal_val.append(key)
            # INCREMENTA O CÓDIGO
            code += 1
            # DEFINE O ÚLTIMO VALOR COMO SENDO O ATUAL
            last_dist = current_dist

    # RETORNA OS CÓDIGOS DOS HUFFMAN E OS VALORES LITERAIS
    return [huffman_codes] + [literal_val]


class GZIP:
    # CLASSE PARA DESCOMPRESSÃO DOS FICHEIROS GZIP

    # INICIALIZAÇÕES
    gzh = None
    gzFile = ''
    fileSize = origFileSize = -1
    f = None

    bits_buffer = 0
    available_bits = 0

    def __init__(self, filename):
        self.gzFile = filename
        self.f = open(filename, 'rb')
        self.f.seek(0, 2)
        self.fileSize = self.f.tell()
        self.f.seek(0)

    def decompress(self):
        # FUNÇÃO PRINCIPAL PARA A DESCOMPRESSÃO DOS ARQUIVOS COM O ALGORITMO DEFLATE (FICHEIROS GZIP)
        # FEITA A LEITURA DE TODOS OS BLOCOS E DESCODIFICAÇÃO DAS ÁRVORES DE HUFFMAN ASSOCIADAS A CADA BLOCO
        # E POSTERIOR DESCOMPRESSÃO DOS DADOS ATRAVÉS DAS ÁRVORES DE HUFFMAN CORRESPONDENTES

        # INICIALIZAÇÃO DO NÚMERO DE BLOCOS DO ARQUIVO COMPRIMIDO
        numBlocks = 0

        # TAMANHO DO ARQUIVO ANTES DA COMPRESSÃO
        origFileSize = self.getOrigFileSize()
        print("ORIGINAL FILESIZE: ", origFileSize)

        # LÊ O HEADER GZIP
        error = self.getHeader()
        if error != 0:
            print('Formato invalido!')
            return

        # LÊ O NOME DO FICHEIRO QUE ESTÁ DENTRO DO ARQUIVO GZIP
        print("ORIGINAL NAME: ", self.gzh.fName)

        # MAIN LOOP - decode block by block
        BFINAL = 0  # VERIFICA SE O BLOCO É FINAL. SE FOR, TERMINA DE ANALISAR OS BLOCOS APÓS A LEITURA DO ÚLTIMO
        window = []
        while not BFINAL == 1:
            # FAZ A LEITURA E GUARDA EM BFINAL O 0 OU 1, RELATIVO A BLOCO FINAL OU NÃO (1 SE FOR FINAL)
            BFINAL = self.readBits(1)
            print("--------------------------------------- NOVO BLOCO ---------------------------------------")
            BTYPE = self.readBits(2)  # LEITURA DE BLOCOS APENAS CODIFICADOS COM HUFFMAN DYNAMIC CODING
            if BTYPE != 2:
                print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks + 1))
                return

            # LÊ OS PRIMEIROS BITS DO BLOCO PARA ANALISAR DETERMINADOS PARÂMETROS, NOMEADAMENTE
            # HLIT QUE USAMOS PARA CALCULAR O NÚMERO DE DISTÂNCIAS NA ARVORE DE HUFFMAN DOS LITERAIS/COMPRIMENTOS
            # HDIST QUE USAMOS PARA CALCULAR O NÚMERO DE DISTÂNCIAS NA ARVORE DE HUFFMAN DAS DISTÂNCIAS
            # HCLEN QUE USAMOS PARA CALCULAR O NÚMERO DE DISTÂNCIAS NA ARVORE DE HUFFMAN QUE DESCODIFICA OUTRAS ÁRVORES
            HLIT = self.readBits(5)
            print("HLIT bin: ", bin(HLIT), " HLIT dec: ", HLIT)
            HDIST = self.readBits(5)
            print("HDIST bin: ", bin(HDIST), " HDIST dec: ", HDIST)
            HCLEN = self.readBits(4)
            print("HCLEN bin: ", bin(HCLEN), " HCLEN dec: ", HCLEN)

            # DECODE DA PRIMEIRA ÁRVORE DE HUFFMAN (QUE CODIFICA AS OUTRAS DUAS)
            alphabet_codes_len = self.get_alphabet_code_len(HCLEN)
            print("ALPHABET CODES LENGTHS: ", alphabet_codes_len)
            alphabet_huffman_codes = code_len_to_huffman_code(alphabet_codes_len,
                                                              [16, 17, 18, 0, 8, 7, 9, 6, 10, 5,
                                                               11, 4, 12, 3, 13, 2, 14, 1, 15])
            print("ALPHABET HUFFMAN CODES: ", alphabet_huffman_codes)
            HCLEN_tree = create_huffman_tree(alphabet_huffman_codes)

            # ÁRVORE DE HUFFMAN DOS LITERAIS/COMPRIMENTOS
            HLIT_codes_len = self.get_code_len(HLIT + 257, HCLEN_tree)
            print("HLIT CODES LENGTHS: ", HLIT_codes_len)
            HLIT_huffman_codes = code_len_to_huffman_code(HLIT_codes_len, list(range(HLIT + 257)))
            print("HLIT HUFFMAN CODES: ", HLIT_huffman_codes)
            HLIT_tree = create_huffman_tree(HLIT_huffman_codes)

            # ÁRVORE DE HUFFMAN DAS DISTÂNCIAS
            HDIST_codes_len = self.get_code_len(HDIST + 1, HCLEN_tree)
            print("HDIST CODES LENGTHS: ", HDIST_codes_len)
            HDIST_huffman_codes = code_len_to_huffman_code(HDIST_codes_len, list(range(HDIST + 1)))
            print("HDIST HUFFMAN CODES: ", HDIST_huffman_codes)
            HDIST_tree = create_huffman_tree(HDIST_huffman_codes)

            # LÊ OS DADOS DOS BLOCOS
            data = self.decode(HLIT_tree, HDIST_tree, window)

            # ESCREVE OS DADOS OBTIDOS DO BLOCO ANALISADO, NO FICHEIRO
            self.write_data(data)

            # ADICIONA À WINDOW OS VALORES DA data DO BLOCO ATUAL
            # É USADO PARA CASO O FICHEIRO TENHA MAIS DO QUE UM BLOCO E PRECISE DE LER VALORES DO BLOCO ANTERIOR
            # A WINDOW SÓ PRECISA DE TER TAMANHO 32768 POIS É O MÁXIMO DE DISTÂNCIA QUE O LZ77 PODE RECUAR
            window += data
            if len(window) >= 32768:
                # CASO A WINDOW TENHA MAIS DO QUE 32768 ELEMENTOS, DAMOS UM SLICE PARA FICAR APENAS COM OS 32768 ÚLTIMOS
                window = window[-32768:]

            # CONTA O NÚMERO DE BLOCOS COMPRIMIDOS
            numBlocks += 1
            print("BLOCK NUM:" + str(numBlocks))
            print("--------------------------------------- FIM DO BLOCO ---------------------------------------")

        # FECHA O FICHEIRO (GZIP)
        self.f.close()
        print("End: %d block(s) analyzed." % numBlocks)

    def getOrigFileSize(self):
        # FUNÇÃO PARA FAZER A LEITURA DO TAMANHO DO FICHEIRO ORIGINAL (ANTES DA SUA COMPRESSÃO)

        # GUARDA A POSIÇÃO ATUAL DO PONTEIRO
        fp = self.f.tell()

        # SALTA PARA O FIM-4
        self.f.seek(self.fileSize - 4)

        # LÊ OS ÚLTIMOS 4 BYTES (LITTLE ENDIAN)
        sz = 0
        for i in range(4):
            sz += self.f.read(1)[0] << (8 * i)

        # DEVOLVE O PONTEIRO À SUA POSIÇÃO INICIAL
        self.f.seek(fp)

        return sz

    def getHeader(self):
        # FUNÇÃO PARA LER O HEADER DO FICHEIRO

        self.gzh = GZIPHeader()
        header_error = self.gzh.read(self.f)
        return header_error

    def readBits(self, n, keep=False):
        # FUNÇÃO PARA LER BITS. SE keep = True, ENTÃO OS BITS SÃO DEIXADOS PARA ESTAREM ACESSÍVEIS POSTERIORMENTE

        while n > self.available_bits:
            self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
            self.available_bits += 8

        mask = (2 ** n) - 1
        value = self.bits_buffer & mask

        if not keep:
            self.bits_buffer >>= n
            self.available_bits -= n

        return value

    def get_alphabet_code_len(self, HCLEN):
        # FUNÇÃO QUE RECEBE O HCLEN E USA A FÓRMULA DO HCLEN+4 PARA LER 3 BITS RELATIVOS A CADA UM DOS CÓDIGOS
        # QUE SERÁ DEPOIS USADO PARA A PRIMEIRA ÁRVORE DE HUFFMAN QUE IRÁ POSTERIORMENTE DAR ORIGEM ÀS OUTRAS DUAS

        # INICIA UM ARRAY A ZEROS
        alphabet_code_len = np.zeros(19, dtype=np.uint8)

        # PARA CADA VALOR DO HCLEN+4, LÊ 3 BITS E GUARDA NO ARRAY DE ZEROS
        for i in range(HCLEN + 4):
            alphabet_code_len[i] = self.readBits(3)

        # DEVOLVE O ARRAY
        return alphabet_code_len

    def get_code_len(self, iterations, huffmantree):
        # FUNÇÃO QUE LÊ OS BITS E COM BASE NA ÁRVORE DE HUFFMAN DO alphabet_huffman_codes VERIFICA O CÓDIGO BINÁRIO
        # DA ÁRVORE QUE DIZ RESPEITO A UM DOS CÓDIGOS HARDCODED DO ARRAY
        # [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]

        codes_len = []
        i = 0
        while i < iterations:
            node = self.search_bit_by_bit(huffmantree)

            # FAZEMOS UMA VERIFICAÇÃO PARA SABER SE O COMPRIMENTO É LITERAL OU SE É UMA SEQUÊNCIA DE ZEROS
            # OU DE UM VALOR ANTERIOR
            if node == 16:
                skip = self.readBits(2) + 3
                x = codes_len[i - 1]
            elif node == 17:
                skip = self.readBits(3) + 3
                x = 0
            elif node == 18:
                skip = self.readBits(7) + 11
                x = 0
                # CASO NÃO SEJA NENHUM DOS ACIMA, É LITERAL
            else:
                skip = 1
                x = node

            # ADICIONA AO codes_len O(S) VALOR(ES) BUSCADOS ANTERIORMENTE
            for j in range(skip):
                codes_len.append(x)

            i += skip

        return codes_len

    def decode(self, HLIT_tree, HDIST_tree, window):
        # FUNÇÃO QUE DESCODIFICA OS DADOS DO BLOCO COM BASE NAS ÁRVORES DE HUFFMAN

        # DICIONARIO DOS COMPRIMENTOS, PARA EXISTIR UMA CORRELAÇÃO ENTRE O COMPRIMENTO E O VALOR LIDO
        lenghts = {265: 11, 266: 13, 267: 15, 268: 17,
                   269: 19, 270: 23, 271: 27, 272: 31, 273: 35, 274: 43, 275: 51,
                   276: 59, 277: 67, 278: 83, 279: 99, 280: 115, 281: 131, 282: 163, 283: 195, 284: 227, 285: 258}

        # DICIONARIO DAS DISTÂNCIAS, PARA EXISTIR UMA CORRELAÇÃO ENTRE A DISTÂNCIA E O VALOR LIDO
        distances = {4: 5, 5: 7, 6: 9, 7: 13, 8: 17, 9: 25, 10: 33, 11: 49, 12: 65, 13: 97, 14: 129, 15: 193, 16: 257,
                     17: 385, 18: 513, 19: 769, 20: 1025, 21: 1537, 22: 2049, 23: 3073, 24: 4097, 25: 6145, 26: 8193,
                     27: 12289, 28: 16385, 29: 24577}

        first_len = len(window)
        end_of_block = False
        position = len(window)
        while not end_of_block:
            lit_len_node = self.search_bit_by_bit(HLIT_tree)

            # VERIFICAMOS SE O VALOR LIDO NA ARVORE DOS LITERAIS/COMPRIMENTOS É UM LITERAL OU UM COMPRIMENTO
            # OU O FIM DO BLOCO
            if lit_len_node < 256:
                # SE FOR LITERAL ADICIONAMOS À WINDOW DE INFORMAÇÃO E REPETIMOS
                window.append(lit_len_node)
                position += 1
            elif lit_len_node == 256:
                end_of_block = True

            else:
                # SE FOR COMPRIMENTO, CALCULAMOS O VALOR DO COMPRIMENTO USANDO O DICIONARIO DOS COMPRIMENTOS,
                # LENDO OS BITS NECESSÁRIOS PARA CHEGAR A ESSE VALOR
                if 257 <= lit_len_node <= 264:
                    length = lit_len_node - 257 + 3
                elif lit_len_node == 285:
                    length = 258
                else:
                    bits = (lit_len_node - 261) // 4
                    length = lenghts[lit_len_node] + self.readBits(bits)

                # COMO É UM COMPRIMENTO, TAMBÉM TEMOS DE TER UMA DISTÂNCIA
                # VAMOS LER OS PRÓXIMOS BITS PARA ENTRAR NA ÁRVORE DE HUFFMAN DAS DISTÂNCIAS E OBTER UM VALOR
                dist_node = self.search_bit_by_bit(HDIST_tree)

                # A PARTIR DESSE VALOR E DO DICIONÁRIO DAS DISTÂNCIAS CALCULAMOS O VALOR DA DISTÂNCIAS A RECUAR
                if 0 <= dist_node <= 3:
                    distance = 1 + dist_node
                else:
                    bits = (dist_node // 2) - 1
                    if dist_node > 27:
                        bits = 13
                    distance = distances[dist_node] + self.readBits(bits)

                # COPIAMOS OS VALORES QUE ESTÃO À DISTÂNCIA CALCULADA DO FIM DA DATA PARA A WINDOW DE INFORMAÇÃO
                for i in range(length):
                    window.append(window[position - distance + i])
                position += length
                # ----------------------------

        # COMO USAMOS UMA WINDOW PARA CASO HAJA MAIS DO QUE UM BLOCO PODERMOS LER OS VALORES ANTERIORES,
        # TEMOS DE RETIRAR ESSES VALORES ANTERIORES PARA NÃO REPETIRMOS INFORMAÇÃO
        window = window[-len(window) + first_len:]
        return window

    def search_bit_by_bit(self, huffman_tree):
        # FUNÇÃO QUE, DADA UMA ÁRVORE DE HUFFMAN, RECEBIDA COMO PARÂMETRO, ANALISA BIT POR BIT
        # ATRAVÉS DA LEITURA DE BITS COM readBits A EXISTÊNCIA DE UM MATCH COM UM CÓDIGO DE HUFFMAN
        # É DEPOIS DEVOLVIDO O NODE DA ÁRVORE DE HUFFMAN

        # INICIALIZAÇÕES
        found = False
        node = -1

        # PESQUISA ATÉ ENCONTRAR UM MATCH. EXISTE SEMPRE UM MATCH
        while not found:
            # FAZ A LEITURA DE BITS CONSECUTIVOS ATÉ FORMAR UM CÓDIGO DE HUFFMAN PRESENTE NA ÁRVORE
            code = str(self.readBits(1))
            node = huffman_tree.nextNode(code)

            # QUEBRA O CICLO QUANDO ENCONTRA O MATCH
            if node != -1 and node != -2:
                found = True

        huffman_tree.resetCurNode()
        # RETORNA NODE
        return node

    def write_data(self, data):
        # FUNÇÃO QUE ESCREVE A PORÇÃO DE DADOS PASSADAS POR ARGUMENTO NO FICHEIRO DE DESTINO
        # O FICHEIRO DE DESTINO DIZ RESPEITO AO fName OBSERVADO PELA LEITURA DO CABEÇALHO DO GZIP
        fName = self.gzh.fName
        with open(fName, 'a') as f:
            for i in data:
                f.write(chr(i))


if __name__ == '__main__':
    # MAIN

    # NA LINHA DE COMANDOS PODERÁ SER PASSADO O NOME DO FICHEIRO
    # FORMATO: PYTHON GZIP.PY <NOME_DO_FICHEIRO.TXT.GZ>
    filename = "FAQ.txt.gz"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    # DESCOMPRESSÃO DO FICHEIRO
    gz = GZIP(filename)
    gz.decompress()

    # ABERTO NO MODO DE LEITURA BINÁRIA
    f = open(filename, 'rb')
