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


#linha = [(1, 'SERGIO NOGAI', 2, 0, 1, 1), (2, 'ANA CLAUDIA MOLONHI NUNES', 2, 0, 2, 1), (3, 'RAFAEL GONÇALVES DE MELLO ROSA MENDES', 2, 0, 3, 1), (4, 'MARIANNA DE CARVALHO ROMERO', 1, 0, 4, 1), (5, 'THAIS E SILVA ALBANI', 1, 0, 5, 1)]
#linha = [(1, 'SERGIO NOGAI', 2, 0, 1, 1)]
#lista = []


saldo_max = 4
versao    = 'v3.0'
data      = '18/09/2018'
banco     = 'designacao.db'

# ---------------------------------------------------------------------------------------------------------------------

# Funçao que monta o Cabeçalho
def cabecalho():
    print("\n***************************************************************")
    print("\n*                  DESIGNAÇÃO AUTOMÁTICA      " + data + " " + versao + " *")
    print("\n***************************************************************")

# Funçao que Limpa a Tela do Sistema
def limpa_tela():
    if os.name == 'posix':
        os.system('clear')
    else:  # 'nt'
        os.system('cls')

# Zera os Saldos dos Servidores no Grupo
def zera_saldo(id_grupo):

    # Calcula os Saldos dos Servidores
    con = sqlite3.connect(banco)
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
        elif (saldo > int((saldo_max // 2)) and peso == 1):
            novo_saldo = saldo - int((saldo_max // 2))
        else:
            novo_saldo = 0

        sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
        c_update = con.cursor()
        c_update.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))

    con.commit()
    con.close()

# Atualiza o Saldo do Servidor no Grupo
def atualiza_saldo(novo_saldo, id_servidor_grupo):
    con = sqlite3.connect(banco)
    sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
    c = con.cursor()
    c.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))
    con.commit()
    con.close()

# Exibe Resultado com os Saldos
def exibe_saldo():
    con = sqlite3.connect(banco)
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


# Se tiver somente um, Participa da Distribuicao
def verificaUm(linha):
    if len(linha) == 1:
        return True


# Mantem o Saldo quando somente um Participa
def mantemSaldo(linha):
    mantem_saldo = list(linha[0])
    mantem_saldo[3] = int(mantem_saldo[3] - 1)
    return mantem_saldo


# Verifica se esta dentro dos Limites do Saldo Maximo por peso
def verificaLimites(saldo_atual, peso_atual):
    if (int(saldo_atual) < int(saldo_max // 2) and peso_atual == 1):
        return True
    elif (int(saldo_atual) < int(saldo_max) and peso_atual == 2):
        return True
    else:
        return False


# Se a Diferenca do Saldo for Maior que o Intervalo, Participa
def comparaSaldo(linha, id, saldo_atual, peso_atual):
    for i in linha:
        id_linha    = i[0]
        peso_linha  = i[2]
        saldo_linha = int(i[3])

        # Verifica se a Diferença Entre os Colegas de Mesmo Peso e Menor que o Intervalo
        if (id != id_linha and peso_atual == peso_linha):
            if (int((saldo_atual - saldo_linha)) >= int(saldo_max // 2)):
                return False

        # Nao Participa se o Saldo for Positivo e tiver Alguem com Saldo Negativo
        if (int(saldo_atual) >= 0 and int(saldo_linha) < 0):
            return False

        # Nao Participa se tiver Alguem com Saldo Negativo Maior que a Diferenca
        if (int(saldo_atual) < 0 and int(saldo_linha) < 0):
            if (int(abs(saldo_linha) - abs(saldo_atual)) >= int(saldo_max // 2)):
                return False
    return True


# Compara diferenca em Saldos Negativos
def comparaSaldoNegativo(linha, id, saldo_atual):
    s = 0
    n = 0
    for i in linha:
        id_linha    = i[0]
        saldo_linha = int(i[3])

        if (id != id_linha):

            # Participa de os Dois forem Negativos com Diferença Menor que o Intervalo
            if (int(saldo_atual) < 0 and int(saldo_linha) < 0):

                if(int(saldo_atual) < int(saldo_linha)):
                    if (int(abs(saldo_atual) - abs(saldo_linha)) >= int(saldo_max // 2)):
                        s += 1
                    else:
                        n += 1
                else:
                    n += 1
    if (s > n):
        return True
    else:
        return False



# ---------------------------------------------------------------------------------------------------------------------



def cupons(id_grupo):

    # Busca os Servidores por Grupo para Gerar os Cupons
    con = sqlite3.connect(banco)
    sql = "SELECT id_servidor, nome_servidor, peso_servidor_grupo, saldo_servidor_grupo, id_servidor_grupo, " \
          "id_grupo_servidor_grupo " \
          "FROM servidores, servidores_grupos " \
          "WHERE st_servidor = 'A' AND id_servidor = id_servidor_servidor_grupo AND id_grupo_servidor_grupo == ?"

    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    con.close()
    lista = []

    # Monta a Lista: [0] == ID_SERVIDOR / [1] == NOME / [2] == PESO / [3] == SALDO
    #                [4] == ID_SERVIDOR_GRUPO / [5] == ID_GRUPO_SERVIDOR_GRUPO
    for i in linha:
        id_i = i[0]
        saldo_atual = int(i[3])
        peso_atual = int(i[2])
        participa = 0
        nao_participa = 0

        # Se tiver so 1 Habilitado, Participa do Sorteio e Nao Altera o Saldo
        if verificaUm(linha):
            lista.append(mantemSaldo(linha))
            print(i[1] + " | verificaUm()")
            return lista


        # Verifica a diferenca dos que possuem Saldo Negativo
        if comparaSaldoNegativo(linha, id_i, saldo_atual):
            lista.clear()
            lista.append(list(i))
            print(i[1] + " | comparaSaldoNegativo()")
            return lista


        # Verifica se o Saldo Atual esta abaixo de saldo_max
        if verificaLimites(saldo_atual, peso_atual):
            participa += 1
            print("\n" + i[1] + " | verificaLimites()")
        else:
            nao_participa += 1


        # Verifica se o Diferença entre todos e Menor que o Intervalo
        if comparaSaldo(linha, id_i, saldo_atual, peso_atual):
            participa += 1
            print(i[1] + " | comparaSaldo()")
        else:
            nao_participa += 1


        # Se o Total de Vezes que Participa for Maior entra no Sorteio
        if (participa > nao_participa):
            lista.append(list(i))

    return lista


# ---------------------------------------------------------------------------------------------------------------------


limpa_tela()
cabecalho()
opcao = input("\n[ ENTER ] para Distribuir ou [ S ] para Sair: ")

while opcao.lower() != 's':

    limpa_tela()

    sorteio = list(cupons(1))# id_grupo

    if not sorteio:
        zera_saldo(1) # id_grupo
        sorteio = list(cupons(1)) # id_grupo

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
            if ((id_i != id_y) and (peso_y == 1)):

                qtde_peso1 = 1

                # Participa se a Diferença de Processos for Menor que o Intervalo
                if (diferenca < intervalo):
                    participa += 1
                else:
                    nao_participa += 1

        if (qtde_peso1 == 0):
            participa += 1

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
            if ((id_i != id_x) and (peso_x == 2)):

                qtde_peso2 = 1

                # Participa se a Diferença de Processos for Menor que o Intervalo
                if (diferenca < intervalo):
                    participa += 1
                else:
                    nao_participa += 1

        if (qtde_peso2 == 0):
            participa += 1
"""