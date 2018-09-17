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
@data:          13/09/2018
"""

# Importação dos Módulos Necessários
import os
import random
import sqlite3
import datetime

# Variaveis Globais
versao    = 'v2.1'
data      = '13/09/2018'
banco     = 'designacao.db'
saldo_max = 4

# ----------------------------------------------CODIGO DAS FUNCOES------------------------------------------------------

# Funçao que Limpa a Tela do Sistema
def limpa_tela():
    if os.name == 'posix':
        os.system('clear')
    else:  # 'nt'
        os.system('cls')

# ----------------------------------------------CODIGO DAS TELAS-------------------------------------------------------

# Funçao que monta o Cabeçalho
def cabecalho():
    print("\n***************************************************************")
    print("\n*                  DESIGNAÇÃO AUTOMÁTICA      " + data + " " + versao + " *")
    print("\n***************************************************************")
















# ----------------------------------------------CODIGO DAS CLASSES------------------------------------------------------

class Menu:

    # Metodo que monta a Tela Inicial
    def menuPrincipal(self):
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
            return False
            self.menuPrincipal()

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


# Classe Servidores
class Servidor:

    # Metodo Construtor
    def __init__(self, nome='', tipo = '', status=''):
        self.nome = nome
        self.tipo = tipo
        self.status = status

    # Metodo que Retorna os Dados do Servidor
    def getServidor(self, id):
        sql = "SELECT * FROM servidores WHERE id_servidor == ?"
        try:
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, str(id))
            linha = c.fetchall()
            con.close()
            self.id     = linha[0][0]
            self.nome   = linha[0][1]
            self.tipo   = linha[0][2]
            self.status = linha[0][3]
            return list(linha)
        except:
            return False

    # Metodo que Retorna os Dados do Servidor
    def getSaldoGrupo(self, id_grupo_servidor_grupo, id_servidor_servidor_grupo):
        try:
            # Busca os Saldos dos Servidores no Grupo
            sql = "SELECT id_servidor_grupo, saldo_servidor_grupo, peso_servidor_grupo FROM servidores_grupos " \
                    "WHERE id_grupo_servidor_grupo == ? and id_servidor_servidor_grupo == ?"
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, (str(id_grupo_servidor_grupo), str(id_servidor_servidor_grupo)))
            linha = c.fetchall()
            self.id_servidor_grupo = linha[0][0]
            self.saldo             = linha[0][1]
            self.peso              = linha[0][2]
            return list(linha)
        except:
            return False

    # Metodos que Atualiza o Saldo de Processos do Servidor no Grupo
    def setSaldo(self, saldo_servidor_grupo, id_servidor_grupo):
        sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
        try:
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, (str(saldo_servidor_grupo), str(id_servidor_grupo)))
            con.commit()
            con.close()
            return True
        except:
            return False

    # Metodo que Altera o Status do Servidor
    def setStatus(self, st_servidor, id_servidor):
        sql = "UPDATE servidores SET st_servidor == ? WHERE id_servidor == ?"
        try:
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, (str(st_servidor), str(id_servidor)))
            con.commit()
            con.close()
            return True
        except:
            return False


# Classe Grupos
class Grupo:

    # Metodo Construtor
    def __init__(self, nome='', tipo = '', status=''):
        self.nome   = nome
        self.tipo   = tipo
        self.status = status

    def zeraSaldo(self, id_grupo_servidor_grupo):
        try:
            # Busca os Saldos dos Servidores no Grupo
            sql = "SELECT id_servidor_grupo, saldo_servidor_grupo, peso_servidor_grupo FROM servidores_grupos " \
                    "WHERE id_grupo_servidor_grupo == ? "
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, str(id_grupo_servidor_grupo))
            linha = c.fetchall()
        except:
            return False

        # Se Saldo Atual > saldo_max : Subtrai saldo_max do Saldo Atual para Equilibrar o Sorteio
        for i in linha:
            id_servidor_grupo = i[0]
            saldo = int(i[1])
            peso  = int(i[2])

            if (saldo > saldo_max and peso == 2):
                novo_saldo = saldo - saldo_max
            # Se for Estagiario, subtrai a Metade do saldo_max
            elif (saldo > (saldo_max // 2) and peso == 1):
                novo_saldo = saldo - (saldo_max // 2)
            # Se o Saldo Atual nao for > saldo_max :  Zera
            else:
                novo_saldo = 0

            try:
                sql = "UPDATE servidores_grupos SET saldo_servidor_grupo == ? WHERE id_servidor_grupo == ?"
                c_update = con.cursor()
                c_update.execute(sql, (str(novo_saldo), str(id_servidor_grupo)))
            except:
                return False
        con.commit()
        con.close()
        return True


class Sorteio:

    # Metodos Construtor
    def __init__(self):
        return True

    # Funçao que Insere as Designaçoes no Relatorio
    def atualizaRelatorio(self, id_servidor, id_grupo, processo, tp_designacao):
        hoje = datetime.datetime.now()
        sql = "INSERT INTO relatorios " \
                "(id_servidor_relatorio, id_grupo_relatorio, processo_relatorio, dt_relatorio, tp_designacao_relatorio) " \
                    "VALUES (?,?,?,?,?)"
        try:
            con = sqlite3.connect(banco)
            c = con.cursor()
            c.execute(sql, (str(id_servidor), str(id_grupo), str(processo), str(hoje), str(tp_designacao)))
            con.commit()
            con.close()
            return True
        except:
            return False


# --------------------------------------------- EXECUCAO DO PROGRAMA----------------------------------------------------

# Funcao Main do Programa
def main():
    # Cria um objeto Menu
    menu = Menu()
    menu.menuPrincipal()

    # Cria um objeto Servidor
    servidor = Servidor()
    servidor.getSaldoGrupo(1,1)
    print(servidor.peso)

    grupo = Grupo()
    grupo.zeraSaldo(1)


# Executa o programa
if __name__ == "__main__":
    main()




























#    def __str__(self):
#        return "Título: %s , autor: %s, páginas: %s " \
#               % (self.titulo, self.autor, self.paginas)

#    def __len__(self):
#        return self.paginas
