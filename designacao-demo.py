#!usr/bin/python3
# -*- mode python; coding: utf-8 -*-
#
# Sistema para Designação Automática de Autos Judiciais e Extrajudiciais
# Entrada: Número do Processo
# Distribuição Automática e Aleatória com Diferença Máxima de 2
# Distribuição Equilibrada por Grupos
# Manipulação de Arquivos para Relatórios
#

"""
@autor:         Fernando Cesar Nunes
@contato:       fcesar@mpf.mp.br
@organização:   Ministerio Publico Federal
@data:          04/09/2018
"""

# Importação dos Módulos Necessários
import os
import random
import sqlite3

# Variaveis Globais
versao    = 'v2.1'
data      = '13/09/2018'

# Funçao que monta o Cabeçalho
def cabecalho():
    print("\n***************************************************************")
    print("\n*                  DESIGNAÇÃO AUTOMÁTICA      " + data + " " + versao + " *")
    print("\n***************************************************************")

# ---------------------------------------------------------------------------------------------------------------------

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
          "WHERE st_servidor = 'A' AND id_servidor = id_servidor_servidor_grupo AND id_grupo_servidor_grupo == ?"

    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    lista = []
    con.close()

    print(linha)


    # Diferença Maxima de Processos entre os Servidores e Saldo Maximo antes de Zerar Contadores
    intervalo = 2
    saldo_max = 4

    # Monta a Lista: [0] == ID_SERVIDOR / [1] == NOME / [2] == PESO / [3] == SALDO
    #                [4] == ID_SERVIDOR_GRUPO / [5] == ID_GRUPO_SERVIDOR_GRUPO
    for i in linha:
        id_i = i[0]
        saldo_atual = int(i[3])
        peso_atual  = int(i[2])
        participa = 0
        nao_participa = 0

        # Se tiver so um Habilitado, Participa do Sorteio e Nao Altera o Saldo
        if (len(linha) == 1):
            mantem_saldo = list(i)
            mantem_saldo[3] = int(mantem_saldo[3] - 1)
            lista.append(mantem_saldo)
            return lista

        # Monta a Lista por Peso para Estagiarios
        if (saldo_atual < intervalo and peso_atual == 1 and len(linha) > 1):

            # Contador de Número de Servidores Peso 1
            qtde_peso1 = 0

            # Compara os Saldos dos Servidores de Peso 1
            for y in linha:
                id_y = y[0]
                peso_y = int(y[2])
                saldo_y = int(y[3])
                diferenca = int(saldo_atual - saldo_y)

                # Compara o Saldo com os Demais Servidores com o mesmo Peso
                if((id_i != id_y) and (peso_y == 1)):

                    qtde_peso1 = 1

                    # Participa se a Diferença de Processos for Menor que o Intervalo
                    if(diferenca < intervalo):
                        participa += 1
                    else:
                        nao_participa += 1

            if (qtde_peso1 == 0):
                participa +=1


        # Lista por Peso para Servidores (Recebe 2x mais que Estagiários)
        elif (saldo_atual < saldo_max and peso_atual == 2 and len(linha) > 1):

            # Contador de Número de Servidores Peso 2
            qtde_peso2 = 0

            # Compara os Saldos dos Servidores de Peso 2
            for x in linha:
                id_x = x[0]
                peso_x = int(x[2])
                saldo_x = int(x[3])
                diferenca = int(saldo_atual - saldo_x)

                # Compara o Saldo com os Demais Servidores com o mesmo Peso
                if((id_i != id_x) and (peso_x == 2)):

                    qtde_peso2 = 1

                    # Participa se a Diferença de Processos for Menor que o Intervalo
                    if(diferenca < intervalo):
                        participa += 1
                    else:
                        nao_participa += 1

            if (qtde_peso2 == 0):
                participa +=1

        # Se o Total de Vezes que Participa for Maior entra no Sorteio
        if (participa > nao_participa):
            lista.append(list(i))

    # print("\n>>>: " + str(lista))
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

    # Saldo Máximo por Servidor
    saldo_max = 4

    # Calcula os Saldos dos Servidores
    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_servidor_grupo, saldo_servidor_grupo, peso_servidor_grupo FROM servidores_grupos " \
          "WHERE id_grupo_servidor_grupo == ? "
    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()

    # Se o Saldo Atual for Maior que o Maximo por conta de Distribuiçao Manual
    # Subtrai a Diferença para Equilibrar o Sorteio
    for i in linha:
        id_servidor_grupo = i[0]
        saldo = int(i[1])
        peso = int(i[2])

        if (saldo > saldo_max and peso == 2):
            novo_saldo = saldo - saldo_max
        elif (saldo > (saldo_max // 2) and peso == 1):
            novo_saldo = saldo - (saldo_max // 2)
        else:
            novo_saldo = 0

        sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
        c_update = con.cursor()
        c_update.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))

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
    con.close()

    for i in linha:
        print(i[0] + " : "+ str(i[1]))



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
    # print("\nQuantidade de Cupons: " + str(len(sorteio)))

    sorteado = random.choice(sorteio)
    sorteado[3] = int(sorteado[3]) + 1
    atualiza_saldo(sorteado[3], sorteado[4]) # Parametros: NOVO_SALDO, ID_SERVIDOR_GRUPO

    cabecalho()
    print("\n" + str(sorteio))
    print("\n>>> *** Sorteado *** <<<: " + sorteado[1] + "\n")

    exibe_saldo()
    opcao = input("\n[ ENTER ] para Distribuir ou [ S ] para Sair: ")


# ---------------------------------------------------------------------------------------------------------------------


"""
# TERMCOLOR SAMPLES

import sys
from termcolor import colored, cprint

text = colored('Hello, World!', 'red', attrs=['reverse', 'blink'])
print(text)
cprint('Hello, World!', 'green', 'on_red')

print_red_on_cyan = lambda x: cprint(x, 'red', 'on_cyan')
print_red_on_cyan('Hello, World!')
print_red_on_cyan('Hello, Universe!')

for i in range(10):
    cprint(i, 'magenta', end=' ')

cprint("Attention!", 'red', attrs=['bold'], file=sys.stderr)


# GERA GRAFICO
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

"""
