#!usr/bin/python
# -*- mode python; -*-
#
# Sistema para Designação Automática de Autos Judiciais e Extrajudiciais
# Entrada: Número do Processo
# Distribuição Automática e Aleatória com Diferença Máxima de 3
# Distribuição Equilibrada por Grupos
# Manipulação de Arquivos para Relatórios
#

"""
@autor:         Fernando Cesar Nunes
@contato:       fcesar@mpf.mp.br
@organização:   Ministerio Publico Federal
@data:          01/09/2018
"""

# Importação dos Módulos Necessários
import os
import random
import sqlite3


# Funçao que Limpa a Tela do Sistema
def limpa_tela():
    if os.name == 'posix':
        os.system('clear')
    else:  # 'nt'
        os.system('cls')


# Funçao que gera os cupons
def cupons(id_grupo):

    # Busca os Servidores por Grupo para Gerar os Cupons
    con = sqlite3.connect('designacao.db')

    sql = "SELECT id_servidor, nome_servidor, peso_servidor_grupo, saldo_servidor_grupo, id_servidor_grupo, " \
          "id_grupo_servidor_grupo " \
          "FROM servidores, servidores_grupos " \
          "WHERE st_servidor = 'A' AND id_servidor = id_servidor_grupo AND id_grupo_servidor_grupo == ?"

    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    linha_original = linha
    lista = []

    # Monta a Lista: [0] == ID_SERVIDOR / [1] == NOME / [2] == PESO / [3] == SALDO
    #                [4] == ID_SERVIDOR_GRUPO / [5] == ID_GRUPO_SERVIDOR_GRUPO
    for i in linha:

        saldo_atual = int(i[3])
        peso_atual  = int(i[2])
        participa   = False

        # Monta a Lista por Peso para Estagiarios
        if (saldo_atual < 3 and peso_atual == 1):
            lista.append(list(i))
        # Lista por Peso para Servidores (Recebe 2x mais que Estagiários)
        elif (saldo_atual < 6 and peso_atual == 2):
            for x in linha_original:
                peso_x = x[2]
                id_i = i[0]
                id_x = x[0]
                saldo_x = int(x[3])
                if(peso_x == 2 and id_x != id_i):
                    #print(i[1] + ' ' + str(saldo_atual) + ' | ' + x[1] + ' ' + str(saldo_x))
                    if (saldo_atual <= (saldo_x)): # Deixa 2 Processos de Intervalo
                        participa = True
                        break
            if participa:
                lista.append(list(i))

    con.close()
    #print("\nParticipantes: " + str(lista))
    return lista


# Atualiza o Saldo do Servidor no Grupo
def atualiza_saldo(novo_saldo, id_servidor_grupo):
    con = sqlite3.connect('designacao.db')
    sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
    c = con.cursor()
    c.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))
    con.commit()
    con.close()


# Zera os Saldos dos Servidores no Grupo
def zera_saldo(id_grupo):
    con = sqlite3.connect('designacao.db')
    sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == 0 WHERE id_grupo_servidor_grupo == ?"
    c = con.cursor()
    c.execute(sql, str(id_grupo))
    con.commit()
    con.close()


def exibe_saldo():
    con = sqlite3.connect('designacao.db')
    sql = "SELECT nome_servidor as NOME, saldo_servidor_grupo as SALDO " \
          "FROM servidores, servidores_grupos " \
          "WHERE id_servidor == id_servidor_servidor_grupo " \
          "AND id_grupo_servidor_grupo == 1"
    c = con.cursor()
    c.execute(sql)
    linha = c.fetchall()

    for i in linha:
        print(i[0] + " : "+ str(i[1]))

    con.close()



# ---------------------------------------------------------------------------------------------------------------------


# Funçao que monta o Cabeçalho
def cabecalho():
    print("\n***************************************************************")
    print("\n*                    DESIGNAÇÃO AUTOMÁTICA    01/09/2018 v1.0 *")
    print("\n***************************************************************")

# ---------------------------------------------------------------------------------------------------------------------


limpa_tela()
cabecalho()
opcao = input("\n[ ENTER ] para Distribuir ou [ S ] para Sair: ")

while opcao.lower() != 's':

    limpa_tela()
    # Chama as Funçao de Geraçao dos Cupons
    sorteio = cupons(1) # Parametro: ID_GRUPO

    if len(sorteio) == 0:
        zera_saldo(1) # Parâmetro: ID_GRUPO
        sorteio = cupons(1) # Parametro: ID_GRUPO


    # Realiza o Sorteio
    # sorteado: [0] == ID_SERVIDOR / [1] == NOME / [2] == PESO / [3] == SALDO
    #           [4] == ID_SERVIDOR_GRUPO / [5] == ID_GRUPO_SERVIDOR_GRUPO
    sorteado = random.choice(sorteio)
    #print("\nQuantidade de Cupons: " + str(len(sorteio)))
    sorteado[3] = int(sorteado[3]) + 1
    atualiza_saldo(sorteado[3], sorteado[4]) # Parametros: NOVO_SALDO, ID_SERVIDOR_GRUPO

    cabecalho()

    print("\nSorteado: " + str(sorteado[1]) + "\n")
    exibe_saldo()
    opcao = input("\n[ ENTER ] para Distribuir ou [ S ] para Sair: ")

# ---------------------------------------------------------------------------------------------------------------------











"""


def gera_grafico():

    import matplotlib.pyplot as plt
    con = sqlite3.connect('designacao.db')
    sql = "SELECT nome_servidor as NOME, saldo_servidor_grupo as SALDO " \
          "FROM servidores, servidores_grupos " \
          "WHERE id_servidor == id_servidor_servidor_grupo " \
          "AND id_grupo_servidor_grupo == 1"
    c = con.cursor()
    c.execute(sql)
    nomes = []
    saldos = []
    dados = c.fetchall()

    for linha in dados:
        nomes.append(linha[0])
        saldos.append(linha[1])

    plt.bar(nomes, saldos)
    plt.show()


# Executável (Terminal)
# pip install PyInstaller
# pip install pypiwin32
# pyinstaller --onefile rffps.py


# Random com Dicionario
servidores = {1: 'ANA CLAUDIA MOLONHI', 2: 'RAFAEL MELLO DE ROSA MENDES', 3: 'SERGIO NOGAI'}
designado = dict([random.choice(list(servidores.items()))])
print(designado)



    for i in lista:
        saldo = i.split(':')
        print(saldo[2])




        criterio1 = 0
        for k, v in saldo.items():
            if (k == d[0] and v < 3):
                criterio1 = 1
                #print('Participa: ' + str(d[1]))

        criterio2 = 0
        for k, v in saldo.items():
            if (k != d[0]):
                criterio2 = 1
                print('Participa: ' + str(d[1]))


# Calcula o Saldo de Cada Servidor por Grupo e retorna um Dicionario
def calcula_saldo():
    con = sqlite3.connect('designacao.db')
    sql_saldo = "SELECT id_servidor_relatorio, count(id_relatorio) " \
                "FROM relatorios, servidores " \
                "WHERE id_servidor_relatorio == id_servidor AND st_servidor = 'A' " \
                "GROUP BY id_servidor_relatorio"

    cur = con.cursor()
    cur.execute(sql_saldo)
    total = cur.fetchall()
    dic_saldo = {}
    for s in total:
       dic_saldo.update({s[0]:s[1]})
    con.close()
    return dic_saldo

# Verifica se o Servidor vai Participar do Sorteio
def participa_sorteio():
    return true




    #
    saldo = calcula_saldo()
    print(saldo)


    # Percorre o Dicionario Calculando a Diferença do Saldo
    # Caso seja menor que 3 participa do Sorteio (sorteio = true)
    # Caso nao possua nenhum, participa, também











        # Monta a Lista por Peso
        if saldo_atual < 3 and peso_atual == 1:
            count=0
            if peso_atual > 1:
                while count < i[2]:
                   count+= 1
                   lista.append(list(i))
            else:
                lista.append(list(i))


"""
