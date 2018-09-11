#!usr/bin/python
# -*- mode python; -*-
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
@data:          05/09/2018
"""

# Importação dos Módulos Necessários
import os
import random
import sqlite3
import datetime


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
          "WHERE st_servidor == 'A' AND id_servidor == id_servidor_servidor_grupo AND id_grupo_servidor_grupo == ?"

    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    con.close()

    lista = []

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

        # Monta a Lista por Peso para Estagiarios
        if (saldo_atual < intervalo and peso_atual == 1):
            lista.append(list(i))
        # Lista por Peso para Servidores (Recebe 2x mais que Estagiários)
        elif (saldo_atual < saldo_max and peso_atual == 2):

            # Compara os Saldos dos Servidores de Peso 2
            for x in linha:
                id_x = x[0]
                peso_x = int(x[2])
                saldo_x = int(x[3])
                diferenca = int(saldo_atual - saldo_x)

                # Compara o Saldo com os Demais Servidores com o mesmo Peso
                if((id_i != id_x) and (peso_x == 2)):

                    # Participa se a Diferença de Processos for Menor que o Intervalo
                    if(diferenca < intervalo):
                        participa += 1
                    else:
                        nao_participa += 1

        # Se o Total de Vezes que Participa for Maior entra no Sorteio
        if (participa > nao_participa):
                lista.append(list(i))
    print("\nParticipantes: " + str(lista))
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
    sql = "SELECT id_servidor_grupo, saldo_servidor_grupo FROM servidores_grupos WHERE id_grupo_servidor_grupo == ? "
    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()

    # Se o Saldo Atual for Maior que o Maximo por conta de Distribuiçao Manual
    # Subtrai a Diferença para Equilibrar o Sorteio
    for i in linha:
        id_servidor_grupo = i[0]
        saldo = int(i[1])
        if (saldo > saldo_max):
            novo_saldo = saldo - saldo_max
        else:
            novo_saldo = 0
        sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
        c_update = con.cursor()
        c_update.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))

    con.commit()
    con.close()


# Funçao que Insere as Designaçoes no Relatorio
def atualiza_relatorio(id_servidor, id_grupo, processo, tp_designacao):
    hoje = datetime.datetime.now()
    con = sqlite3.connect('designacao.db')
    sql = "INSERT INTO relatorios " \
          "(id_servidor_relatorio, id_grupo_relatorio, processo_relatorio, dt_relatorio, tp_designacao_relatorio) " \
          "VALUES (?,?,?,?,?)"
    c = con.cursor()
    c.execute(sql, (str(id_servidor), str(id_grupo), str(processo), str(hoje), str(tp_designacao)))
    con.commit()
    con.close()


# ----------------------------------------------CODIGO DAS TELAS-------------------------------------------------------


# Funçao que monta o Cabeçalho
def cabecalho():
    print("\n***************************************************************")
    print("\n*                  DESIGNAÇÃO AUTOMÁTICA      10/09/2018 v1.9 *")
    print("\n***************************************************************")

# ---------------------------------------------------------------------------------------------------------------------

# Funçao que monta a Tela Inicial
def menu():
    limpa_tela()
    cabecalho()
    print("\n MENU PRINCIPAL\n")
    print("[ 1 ] - DISTRIBUIR JUDICIAL")
    print("[ 2 ] - DISTRIBUIR EXTRAJUDICIAL")
    print("[ 3 ] - DISTRIBUIR DOCUMENTO")
    print("[ 4 ] - TRANCAR DISTRIBUIÇÃO")
    print("[ 5 ] - ABRIR DISTRIBUIÇÃO")
    print("[ 6 ] - RELATÓRIOS")
    print("[ 7 ] - REDISTRIBUIR")
    print("[ S ] - SAIR")

    # Carrega o Menu enquanto nao Escolher uma Opçao Valida
    opcoes = ['1','2','3','4','5','6','7','s','S']
    escolha = input("\nEscolha sua Opção [1/2/3/4/5/6/7] ou [S]air: ")
    while str(escolha.lower()) not in opcoes:
        menu()

    if escolha == '1':
        # JUDICIAL
        menu_designacao('J')

    elif escolha == '2':
        # EXTRAJUDICIAL
        menu_designacao('E')

    elif escolha == '3':
        # ADMINISTRATIVO
        menu_designacao('A')

    elif escolha == '4':
        # TRANCAR DISTRIBUICAO
        alterar_designacao('A', 'B')

    elif escolha == '5':
        # ABRIR DISTRIBUICAO
        alterar_designacao('B', 'A')

    elif escolha == '6':
        # RELATORIOS
        menu_relatorio()

    elif escolha == '7':
        # REDISTRIBUICAO
        menu_redistribuicao()

    elif escolha.lower() == 's':
        # SAIR
        exit()

# ---------------------------------------------------------------------------------------------------------------------4

# Mostra a Tela do Relatorio
def menu_relatorio():
    limpa_tela()
    cabecalho()
    print("\n MENU RELATÓRIOS")
    print("\n******************* Grupos de Distribuição ********************\n")

    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_grupo, nome_grupo " \
          "FROM grupos "
    c = con.cursor()
    c.execute(sql)
    linha = c.fetchall()
    con.close()

    grupos = ['s', 'S']
    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - " + str(i[1]))
        grupos.append(str(i[0]))
    print("[ S ] - SAIR")

    id_grupo = input("\nDigite o Código do GRUPO para Visualizar o RELATÓRIO: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    while id_grupo not in grupos:
        menu_relatorio()

    # Se escolher S, volta para o Menu Principal
    if (id_grupo.lower() == 's'):
        menu()

    # Gera o Relatorio
    con = sqlite3.connect('designacao.db')
    sql = "SELECT nome_servidor as NOME, nome_grupo as GRUPO, " \
          "COUNT(id_relatorio) as TOTAL " \
          "FROM servidores, grupos, relatorios " \
          "WHERE id_servidor == id_servidor_relatorio " \
          "and id_grupo == id_grupo_relatorio " \
          "and id_grupo_relatorio == ? group by NOME, GRUPO"
    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    con.close()

    limpa_tela()
    cabecalho()
    print("\n MENU RELATÓRIOS")
    print("\n************** Total de Distribuições por Grupo ***************\n")

    for i in linha:
        print(i[0] + " : "+ str(i[2]))

    repetir = input("\nDeseja gerar outro Relatório? [ENTER] Sim / [N]ão: ")
    while (repetir.lower() != 'n'):
        menu_relatorio()

    if (repetir.lower() == 'n'):
        menu()

# ---------------------------------------------------------------------------------------------------------------------

# Compensa o Saldo Quando Redistribui para outro Servidor
def menu_redistribuicao():

    limpa_tela()
    cabecalho()
    print("\n MENU REDISTRIBUIR")

    print("\n********** Servidores Ativos e Inativos do Gabinete ***********\n")

    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_servidor, nome_servidor " \
          "FROM servidores "

    c = con.cursor()
    c.execute(sql)
    linha = c.fetchall()
    con.close()
    servidores = ['s', 'S']

    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - " + str(i[1]))
        servidores.append(str(i[0]))
    print("[ S ] - SAIR")

    id_servidor = input("\nCódigo do SERVIDOR para Diminuição do Saldo ou [S]air: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    while (id_servidor not in servidores):
        menu_redistribuicao()

    if (id_servidor.lower() == 's'):
        menu()

    # Seleciona Grupos dos quais o Servidor Participa
    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_servidor_grupo, nome_grupo, saldo_servidor_grupo  " \
          "FROM servidores_grupos, grupos " \
          "WHERE id_grupo == id_grupo_servidor_grupo " \
          "AND st_grupo == 'A'" \
          "AND id_servidor_servidor_grupo = ?"

    c = con.cursor()
    c.execute(sql, str(id_servidor))
    linha = c.fetchall()
    con.close()
    grupos = ['s', 'S']

    print("\n************ Grupos nos quais o Servidor Participa ************\n")

    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - " + str(i[1]))
        grupos.append(str(i[0]))
    print("[ S ] - SAIR")

    id_grupo = input("\nCódigo do GRUPO para Diminuição do Saldo ou [S]air: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    while (id_grupo not in grupos):
        menu_redistribuicao()

    if (id_grupo.lower() == 's'):
        menu_redistribuicao()

    qt_processos = input("\nNúmero de Processos REDISTRIBUÍDOS ou [S]air: ")

    while (not qt_processos.isnumeric()):
        if (qt_processos.lower() == 's'):
            menu()
            break
        qt_processos = input("\nNúmero de Processos que foram REDISTRIBUÍDOS ou [S]air: ")


    # Busca o Saldo Atual do Grupo Escolhido
    con = sqlite3.connect('designacao.db')
    sql = "SELECT saldo_servidor_grupo " \
          "FROM servidores_grupos " \
          "WHERE id_servidor_grupo == ?"
    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    con.close()
    saldo_atual = int(linha[0][0])


    # Calcula o Novo Saldo
    novo_saldo = saldo_atual - int(qt_processos)


    # Altera o Saldo do Servidor no Grupo
    con = sqlite3.connect('designacao.db')
    sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
    c = con.cursor()
    c.execute(sql, (str(novo_saldo), str(id_grupo)))
    con.commit()
    con.close()

    print("\n\n**************** Saldo Alterado com SUCESSO! ******************\n")
    print("AVISO: Para equilibrar a distribuição, DISTRIBUIR os processos\n")
    print("  de forma MANUAL ao servidor que recebeu os redistribuídos.\n")

    repetir = input("\nDeseja realizar outra Redistribuição? [ENTER] Sim / [N]ão: ")
    while (repetir.lower() != 'n'):
        menu_redistribuicao()

    if (repetir.lower() == 'n'):
        menu()

# ---------------------------------------------------------------------------------------------------------------------

# Função que monta a Tela de Mudança do Status da Designaçao
def alterar_designacao(st, nova_st):
    limpa_tela()
    cabecalho()

    if(st.upper() == 'A'):
        print("\n MENU TRANCAR DISTRIBUIÇÃO")
        msg = "TRANCAR"
    else:
        print("\n MENU ABRIR DISTRIBUIÇÃO")
        msg = "ABRIR"

    print("\n************ Servidores para Alterar Distribuição *************\n")
    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_servidor, nome_servidor " \
          "FROM servidores " \
          "WHERE st_servidor == ?"
    c = con.cursor()
    c.execute(sql, str(st))
    linha = c.fetchall()
    servidores = ['s', 'S']
    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - " + str(i[1]))
        servidores.append(str(i[0]))
    con.close()
    print("[ S ] - SAIR")

    if(st.upper() == 'A'):
        id_servidor = input("\nCódigo do Servidor para TRANCAR a Distribuição ou [S]air: ")
    else:
        id_servidor = input("\nCódigo do Servidor para ABRIR a Distribuição ou [S]air: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    while (id_servidor not in servidores):
        alterar_designacao(st, nova_st)

    if (id_servidor.lower() == 's'):
        menu()

    # Altera o Status do Servidor
    con = sqlite3.connect('designacao.db')
    sql = "UPDATE servidores SET st_servidor == ? WHERE id_servidor == ?"
    c = con.cursor()
    c.execute(sql, (str(nova_st), str(id_servidor)))
    con.commit()
    con.close()

    print("\n************* Distribuição Alterada com SUCESSO! **************")

    repetir = input("\nDeseja " + msg + " outra Distribuição? [ENTER] Sim / [N]ão: ")
    while (repetir.lower() != 'n'):
        alterar_designacao(st, nova_st)

    if (repetir.lower() == 'n'):
        menu()

# ---------------------------------------------------------------------------------------------------------------------

# Funçao que monta a Tela JUDICIAL
def menu_designacao(tp):
    limpa_tela()
    cabecalho()
    print("\n MENU DISTRIBUIÇÃO")

    # Lista GRUPOS Ativos e as Opçoes
    print("\n******************* Grupos de Distribuição ********************\n")
    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_grupo, nome_grupo " \
          "FROM grupos " \
          "WHERE tp_grupo == ? " \
          "AND st_grupo == 'A'"
    c = con.cursor()
    c.execute(sql, str(tp))
    linha = c.fetchall()
    con.close()

    grupos = ['s', 'S']
    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - "+ str(i[1]))
        grupos.append(str(i[0]))
    print("[ S ] - SAIR")

    id_grupo = input("\nEscolha o GRUPO para realizar a Distribuição ou [S]air: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    while id_grupo not in grupos:
        menu_designacao(tp)

    # Se escolher S, volta para o Menu Principal
    if (id_grupo.lower() == 's'):
        menu()

    # Lista SERVIDORES Ativos no Grupo escolhido
    con = sqlite3.connect('designacao.db')
    sql = "SELECT id_servidor, nome_servidor, id_servidor_grupo, saldo_servidor_grupo " \
          "FROM servidores, servidores_grupos " \
          "WHERE st_servidor == 'A' " \
          "AND id_servidor == id_servidor_servidor_grupo " \
          "AND id_grupo_servidor_grupo == ?"

    c = con.cursor()
    c.execute(sql, str(id_grupo))
    linha = c.fetchall()
    con.close()

    lst_manual = linha
    servidores = ['s', 'S']
    id_servidor = 0

    print("\n********* Servidores com Distribuição Aberta no Grupo *********\n")

    for i in linha:
        print("[ " + str(i[0]) + " ]" + " - "+ str(i[1]))
        servidores.append(str(i[0]))

    # Solicita que Informe o Tipo de Designação
    tp_designacao = input("\nTipo Distribuição [ENTER] Automática / [M]anual / [S]air: ")

    # Carrega o Menu ate a escolha de uma Opçao Valida
    # while (tp_designacao.lower() != 'a' and tp_designacao.lower() != 'm'):
    #    menu_designacao(tp)
    if (tp_designacao.lower() == 's'):
        menu_designacao(tp)

    # Se a Designacao for Manual, solicita o codigo do SERVIDOR
    if (tp_designacao.lower() == 'm'):
        id_servidor = input("\nDigite o Código do SERVIDOR para Distribuição MANUAL ou [S]air: ")

        while id_servidor not in servidores:
            id_servidor = input("Digite o Código do SERVIDOR para Distribuição MANUAL ou [S]air: ")
            #menu_designacao(tp)

        if (id_servidor.lower() == 's'):
            menu_designacao(tp)

    processo = input("\nInforme o DOCUMENTO/AUTOS para Distribuição: ")

    #if (processo.lower() == 's'):
    #    menu_designacao(tp)

    if(processo == ''):
        processo = 'NAO INFORMADO'

    # Exibe tela de Confirmação
    confirmacao = input("\nConfirmar Distribuição [S]im / [N]ão: ")

    while (confirmacao.lower() != 's' and confirmacao.lower() != 'n'):
        confirmacao = input("Confirmar Distribuição [S]im / [N]ão: ")
        #menu_designacao(tp)

    if (confirmacao.lower() == 'n'):
        menu_designacao(tp)
    else:
        # Caso confirme Designa conforme o Tipo (Manual ou Automatico)
        if (tp_designacao.lower() == 'm'):

            # i: [0] == ID_SERVIDOR, [1] NOME_SERVIDOR, [2] ID_SERVIDOR_GRUPO, [3] SALDO_SERVIDOR_GRUPO
            for i in lst_manual:
                if (int(i[0]) == int(id_servidor)):
                    novo_saldo = int(i[3]) + 1
                    id_servidor_grupo = i[2]
                    nome_servidor = i[1]

                    # Atualiza o SALDO
                    atualiza_saldo(novo_saldo, id_servidor_grupo)

                    # Atualiza RELATORIO
                    atualiza_relatorio(i[0], id_grupo, processo, tp_designacao.upper())

                    # Imprime o Resultado da Designaçao Manual
                    print("\n************************ DISTRIBUIDO **************************")
                    print("\nDocumento/Autos: " + str(processo) + "\n")
                    print(">>> " + nome_servidor)

                    #print("\n" + str(processo) + " Distribuido para: " + nome_servidor)
                    break
        else:
            # Chama as Funçao de Geraçao dos Cupons
            sorteio = cupons(int(id_grupo))  # Parametro: ID_GRUPO

            if len(sorteio) == 0:
                zera_saldo(id_grupo)  # Parâmetro: ID_GRUPO
                sorteio = cupons(id_grupo)  # Parametro: ID_GRUPO

            # Realiza o Sorteio
            # sorteado: [0] == ID_SERVIDOR / [1] == NOME / [2] == PESO / [3] == SALDO
            #           [4] == ID_SERVIDOR_GRUPO / [5] == ID_GRUPO_SERVIDOR_GRUPO
            sorteado = random.choice(sorteio)
            sorteado[3] = int(sorteado[3]) + 1
            atualiza_saldo(sorteado[3], sorteado[4])  # Parametros: NOVO_SALDO, ID_SERVIDOR_GRUPO

            # Atualiza RELATORIO
            atualiza_relatorio(sorteado[0], id_grupo, processo, tp_designacao.upper())

            # Imprime o RESULTADO na Tela

            print("\n************************* SORTEADO ****************************")
            print("Documento/Autos: " + str(processo)+"\n")
            print(">>> " + sorteado[1])

            #print("\n" + str(processo) + " *** Sorteado *** para: " + sorteado[1])

        repetir = input("\nDeseja realizar outra Distribuição? [ENTER] Sim / [N]ão: ")
        while (repetir.lower() != 'n'):
            menu_designacao(tp)

        if (repetir.lower() == 'n'):
            menu()

# ---------------------------------------------------------------------------------------------------------------------

# Chamada Inicial do Sistema
menu()

# lista2 = lista[:] # Para Copiar a lista em uma nova Variável