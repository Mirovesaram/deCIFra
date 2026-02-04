from tqdm import tqdm

from datetime import datetime

from interfaceGerada.design import Ui_MainWindow  # Importa a classe gerada pela interface
"""'from pasta.scriptPy import classe' --- interessante"""
#!pip install ipdb Esse ponto de exclamação só funciona no collab para instalação em meio ao código
#import ipdb # Esses comandos foram para importar esse módulo
        # que serviu de ferramenta para estudar erros do código
        # usando debug
from interfaceGerada.janelaGraficoResultados import Ui_MainWindow_graficoResultados

from interfaceGerada.janelaDeteccaoPicosSemRuido import Ui_MainWindow_detectorPicosSemRuido

from interfaceGerada.janelaDeteccaoPicosComRuido import Ui_MainWindow_detectorPicosComRuido
import logging # módulo para permitir colocar os erros num arquivo de log

import sys # módulo para controlar o sistema/programa para poder fechar ele, por exemplo (Acho, não entrei em detalhes)

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QMainWindow, QTextEdit, QDialogButtonBox, QDialog, QPushButton, QVBoxLayout, QLabel, QTableView, QMenu

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QPoint
"""
Importandoo os widgets do PyQt5 que serão necessários para adicionar elementos que não estão na interface visual gerada em .py
que é importada nesse projeto para se colocar os gatilhos e dar vida à interface visual
"""
from PyQt5.QtGui import QIcon
"""
Aqui é para adicionar ícones às janelas
e pop-ups do programa
"""
from PyQt5 import QtGui, QtWidgets
"""
Aqui é para permitir acesso à mudança de fonte
em um pop-up específico da tab Comparar
"""
from PyQt5.QtCore import QEventLoop
# Esse aqui é para importar o evento de loop para
# utilizar com o método open()
from pymatgen.analysis.diffraction.xrd import XRDCalculator # módulo para fazer o padrão de difração dos CIFs selecionados

from pymatgen.io.cif import CifParser # módulo para ler os arquivos CIF e extrair as informações necessárias para fazer
# o padrão de difração

from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

import traceback # módulo para "trazer as linhas de código onde ocorreu um problema" (Não entrei em detalhes)

import pandas as pd # Esse módulo foi utilizada para ter
                    # acesso aos conjuntos de dados bidimen-
                    # sionais conhecidos como DataFrames

import glob # módulo utilizado para criar arrays com os caminhos dos arquivos selecionados

import os # módulo utilizado para criar responsividade e flexibilidade na coleta dos caminhos
# indepente do sistema operacional (Aparentemente, não entrei em muitos detalhes)

import numpy as np 
"""
Necessário para uma certa função que é utilizada no findpeaks
"""
from findpeaks import findpeaks
"""
Necessário para utilizar o método de encontrar
picos com homologia persistente
"""
import matplotlib.pyplot as plt # Utilizado para fazer os plots e
# importar os gráficos feitos
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolBar
from matplotlib.figure import Figure

import matplotlib.colors as mcolors
# Tentar resolver problema dos ícones que não estão aparecendo nas janelas, solução
# retirada de:
# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(caminho_relativo):
    try:
        caminho_base = sys._MEIPASS
    except Exception:
        caminho_base = os.path.abspath(".")

    return os.path.join(caminho_base, caminho_relativo)

# Configuração do arquivo .log de erro
logging.basicConfig(
    # Nome do arquivo
    filename=r'relatorioErros.log',
    level=logging.ERROR, # Nível do aviso do log (Por assim dizer, não entrei em muitos detalhes),
    # como meu caso é erro, pus ERROR

    # Isso eu não entrei em muito detalhes, mas é o formato de como o erro será
    # reportado no arquivo
    format='%(asctime)s - %(levelname)s - %(message)s'
    # Olhando o arquivo de fato é isso, primeiro vem o horário e data em formato asc
    # Depois vem o nível do report
    # E por fim a mensagem sem detalhes que o usuário recebeu do erro
)
# Método para capturar erros de forma global
def capturarExcecao(exctype,value,tb):

    # Essa é a mensagem de erro com detalhes de onde o erro aconteceu no código
    mensagemErro="".join(traceback.format_exception(exctype,value,tb))

    # Esse é o comando para inserir o erro no arquivo .log
    logging.error(mensagemErro)

    # Cria-se uma caixa de erro
    erro=QMessageBox()
    # Coloca-se o ícone da caixa como crítico
    erro.setIcon(QMessageBox.Critical)
    # Insere o texto na caixa de erro
    erro.setText("Ocorreu um erro no aplicativo")
    # E também insere o erro que aconteceu
    erro.setInformativeText(str(value))
    # Esse é o título que aparecerá na caixa,
    # No canto superior esquerdo da caixa
    erro.setWindowTitle("Erro")
    # Comando para adicionar um ícone ao canto superior
    # esquerdo da janela
    erro.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
    # E os detalhes do erro, como onde
    # ocorreu nas linhas de código
    erro.setDetailedText(mensagemErro)
    # Comando para quando fechar a caixa, encerrar o programa
    erro.exec_()

class PandasModel(QAbstractTableModel):

    def __init__(self, dataframe):
        super().__init__()
        self._data = dataframe

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self._data.iat[index.row(), index.column()]
            return str(value)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return str(self._data.index[section])

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Chamando o construtor (Método inicializador)
        # da classe pai no método construtor da classe filha.
        # O uso específico desse comando é no construtor da 
        # classe filha
        super().__init__()
        self.setupUi(self)  # Configura a interface definida em Ui_MainWindow

        

        # Inicialização de diversos atributos que
        # serão utilizados ao longo dos métodos
        # engatilhados ao longo do programa

        # Tais atributos serão classificados também pela aba
        # que pertecem

        #
        # ATRIBUTOS DA ABA DETECTAR PICOS {
        #

        # Esse atributo tem como nome uma convenção
        # da biblioteca findpeaks e virou um atributo 
        # da classe por ter que ser criado em um 
        # método e utilizado em outro
        self.X = None
        """Esse inicializa o valor atual encontrado no spinBox
        da tab Detectar"""
        #self.valorLimite = self.doubleSpinBoxMudarLimite.value()
        """Esse é para armazenar o valor de limite de score para
        ser utilizado como parâmetro no método do findpeaks com
        homologia persistente, para adquirir esse valor usa-se 
        métodos da biblioteca numpy"""
        self.limitePadrao = None
        """
        Esse é para armazenar o caminho do arquivoXy obtido na tab
        Detectar
        """
        self.arquivoXy = None

        self.intensidades = None

        self.angulos = None
        #
        # }
        #

        #
        # ATRIBUTOS DA ABA COMPARAR PICOS {
        #
        """
        Armazenar o diretório do padrão
        para a tab Comparar picos
        """
        self.diretorioPadrao=None
        """
        Armazenar o diretório dos CIFs
        para a tab Comparar picos
        """
        self.diretorioCIFs=None
        """
        Esse vai armazenar os dataframes
        criados das reflexões de cada cif
        entregue pelo usuário
        """
        self.arrayAs3melhores = None
        """
        Esse vai armazenar o dataFrame do padrão
        de difração no todo entregue pelo arquivo
        .xy
        """
        #self.dataFramePadraoNoTodo = None
        # Esse atributo vai armazenar a array
        # criada a partir da ordenação de itens
        # de uma array já criada no método de
        # comparar picos (No caso, tal)
        # array será as dos nomes do CIFs
        self.arrayDfNomesOrden = None
        # Esse atributo vai armazenar 
        # a array de dataframes de comparação
        # ordenadas pela pontuação de cada dataframe
        # de comparação
        self.arrayDfCompOrden=None
        # Esse atributo vai armazenar o número de abas
        # para as planilhas de CIFs e comparações, tal
        # número é ditado a partir do número de arquivos
        # detectados
        self.numeroDeAbas=None
        # Esse atributo é para armazenar a array de dataframes
        # dos CIFs que estão ordenados pela nota
        self.arrayDfCIFsOrden=None
        # Esse atributo armazena valores booleanos
        # que podem informar ao programa se o método principal
        # compararPicos será utilizado no contexto da aba Com-
        # parar Picos
        self.verificou1=None
        # Esse atributo armazena a radiação escolhida na caixa de
        # radiações
        self.valorSelecionado=None
        # Esse atributo armazena o caminho da pasta de CIFs.
        # É usado tanto no contexto do comparar poucos picos
        # quanto no contexto do comparar picos
        self.caminhoCIFs=None
        # Esse atributo armazena o caminho do padrão
        # É usado tanto no contexto do comparar poucos picos
        # quanto no contexto do comparar picos
        self.caminhoPadrao=None
        """
        Esse atributo é criado para abrigar
        um QDialogBox. O porquê de fazer isso
        é para poder utilizar o método .open()
        ao invés do método .exec(), o primeiro
        permite o QDialogBox ficar em segundo
        plano mas caso ele não seja um atributo
        inicial da classe principal após o 
        .open(), o mesmo é destruído caso
        seja armazenado numa variável comum criada
        num método à parte da classe principal
        """
        self.dialogo=None

        self.dataFrameAngulos=None

        self.UtilizouPicos1=None
        #
        # } 
        #

        #
        # ATRIBUTOS DA ABA COMPARAR POUCOS PICOS {
        #


        # Atributo que armazena os dataframes obtidos a partir 
        # de picos importados ou picos detectados
        self.tabelaPadrao=None
        # Atributo que armazena o valor da radiação escolhida
        # na caixa
        self.valorSelecionado2=None
        """
        Essa também é uma trava lógica que permite saber de qual
        método verificar (Como o verificou1) foi utilizado e saber quais dados
        devem ser utilizados sem haver confusão de troca de
        dados entre as tabs Comparar picos e Comparar poucos picos
        que tem métodos que fazem coisas bem parecidas
        """
        self.verificou2=None
        """
        Armazenar o diretório dos CIFs
        para a tab Comparar poucos picos
        """
        self.diretorioCIFs2=None
        """
        Armazenar o diretório do padrão
        para a tab Comparar poucos picos
        """
        self.diretorioPadrao2=None
        """
        Mais uma trava lógica, essa para
        travar o método comparar picos caso 
        dado dataframe necessário não seja feito
        (Essa trava substancialmente é para a aba
        comparar poucos picos). Ela teve que ser
        utilzada pois não existia uma boa condi-
        ção para ser utilizada com o dataFrame
        estar vazio ou não
        """
        self.travaLogica=None
        """
        Armazenar o dataframe de ângulos escolhidos
        pelo usuário na tab Comparar poucos picos
        """
        self.dfPicos=None
        """
        Armazenar os itens que são os ângulos escolhidos
        pelo usuário na tab Comparar poucos picos
        """
        self.arrayPicos=[None, None, None, None,None]
        """
        Armazenar informação para indicar o número
        final de certos laços for, preciso na tab
        comparar Poucos picos
        """
        self.ultimoIndex=None

        self.UtilizouPicos2=None

        #
        # }
        #

        # Comando para deixar a janela não redimensionável
        # e com largura 800 pixels e altura 800 pixels
        self.setFixedSize(800,800)
        # Explicado anteriormente
        self.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))

        ### ABA DETECTAR PICOS ###

        self.botaoSelecionarArquivoXy.clicked.connect(self.abrirArquivoEventXy)

        self.caminhoXYtextEdit.setText('O caminho aparecerá aqui quando selecionado')

        #self.doubleSpinBoxMudarLimite.setEnabled(False)

        self.pushButtonDetectarTopyPeakDetec.setEnabled(False)

        self.pushButtonDetectarCaerus.setEnabled(False)

        self.pushButtonDetectarTopyPeakDetec.clicked.connect(self.iniciarJanelaDeteccaoSemRuidos)

        self.pushButtonDetectarCaerus.clicked.connect(self.iniciarJanelaDeteccaoComRuidos)

        self.label_LogoMaior.setPixmap(QtGui.QPixmap(resource_path(r'icones\logoMaior.png')))

        #self.pushButtonExportar.clicked.connect(self.popUpExportAngulos)

        #self.pushButtonExportar.setEnabled(False)

        ### ABA COMPARAR COM CIFS ###

        self.botaoSelecPadrao.setEnabled(False)

        self.botaoSelecPadrao.clicked.connect(self.abrirDirEventSeuPadrao)

        self.caminhoPadraotextEdit.setText('Aguardando a detecção dos picos...')

        self.botaoSelecCIF.setEnabled(False)

        # Criar um gatilho que envolve clicar esse botão
        # Caso clique no botão, o método abrirDirEventCIFs
        # será chamado e iniciado
        self.botaoSelecCIF.clicked.connect(self.abrirDirEventCIFs)

        self.caminhoCIFstextEdit.setText('Aguardando a detecção dos picos...')

        self.caixaRadiacoes.setEnabled(False)
        # Comandos para adicionar os dados dos itens da combo
        # Box de radiação que são os presentes no laço for
        # Nessa array tem floats que foram tirados como padrão
        # do software Diamond e de um arquivo instrumental utilizado
        # no software GSAS EXPGUI, sendo o terceiro a média aritmética
        # dos dois primeiros
        # e as strings pertencem à documentação do
        # pymatgen para radiação característica
        self.itens = [
            1.540598, 1.544426, 1.542512, "CuKa", "CuKa1", "CuKa2", "CuKb1",
            "CoKb1", "CoKa1", "CoKa2", "CoKa",
            "FeKb1", "FeKa1", "FeKa2", "FeKa",
            "CrKb1", "CrKa1", "CrKa2", "CrKa",
            "MoKa", "MoKa1", "MoKa2", "MoKb1",
            "AgKa", "AgKa1", "AgKa2", "AgKb1"
        ]
        # comando simples para adicionar os valores dos
        # itens selecionados
        # A função enumarate permite ter um index
        # associado ao dado do item que foi puxado
        # evidenciando sua posição
        for self.index, self.item in enumerate(self.itens):
            # setItemData insere o dado de um item em dada
            # posição desse item
            self.caixaRadiacoes.setItemData(self.index,self.item)
            self.caixaRadiacoes_2.setItemData(self.index,self.item)
        # gatilho que usa o sinal activated, que basicamente indica
        # se o checkbox está com algum valor selecionado (Isso significa
        # ele estar ativado) e por padrão, ele está. Com isso, ativa uma função
        # que tem como parâmetro index e resgata a partir desse sinal qual valor
        # é equivalente para o index e aloca o dado desse item numa variável
        # para ser usado na função compararPicos(). Creio que seja assim que funciona
        self.caixaRadiacoes.activated.connect(self.itemSelecionado)
        self.caixaRadiacoes_2.activated.connect(self.itemSelecionado2)
        """
        Uma ação programática para o primeiro item ser escolhido para engatilhar o activated
        No caso a primeira linha de código seleciona o primeiro item
        E a segunda linha emite um sinal de evento activated para o índice 0, disparando o método
        (Tive que fazer isso pois depois de um tempo somente o activated não estava funcionando
        como foi descrito nas linhas de comentários anteriores a essa)
        """
        self.caixaRadiacoes.setCurrentIndex(0)
        self.caixaRadiacoes.activated.emit(0)
        self.caixaRadiacoes_2.setCurrentIndex(0)
        self.caixaRadiacoes_2.activated.emit(0)

        self.botaoComparar.setEnabled(False)
        # Esse método que será chamado é para verificar se o usuário colocou
        # os caminhos necessários antes de apertar o botão para fazer a comparação
        self.botaoComparar.clicked.connect(self.verificar)

        ### ABA COMPARAR POUCOS PICOS ###

        self.botaoSelecPadrao_2.setEnabled(False)

        self.botaoSelecPadrao_2.clicked.connect(self.abrirDirEventSeuPadraoAdicionarPicos)

        self.caminhoPadraotextEdit_2.setText('Aguardando a detecção dos picos...')

        self.comboBoxPico1.setEnabled(False)
        
        self.comboBoxPico2.setEnabled(False)

        self.comboBoxPico3.setEnabled(False)

        self.comboBoxPico4.setEnabled(False)

        self.comboBoxPico5.setEnabled(False)

        self.comboBoxPico1.activated.connect(self.picoSelecionado1)
        self.comboBoxPico2.activated.connect(self.picoSelecionado2)
        self.comboBoxPico3.activated.connect(self.picoSelecionado3)
        self.comboBoxPico4.activated.connect(self.picoSelecionado4)
        self.comboBoxPico5.activated.connect(self.picoSelecionado5)
        # Esse método foi criado pois as linhas de comando
        # necessárias aqui foram repetidas algumas vezes pelo
        # código
        self.emitirSinaisComboBoxPicos()

        self.botaoSelecCIF_2.setEnabled(False)

        self.botaoSelecCIF_2.clicked.connect(self.abrirDirEventCIFs2)

        self.caminhoCIFstextEdit_2.setText('Aguardando a detecção dos picos...')

        self.caixaRadiacoes_2.setEnabled(False)

        self.botaoComparar_2.setEnabled(False)
        
        self.botaoComparar_2.clicked.connect(self.verificar2)

        ### ABA AJUDA ###

        self.labelLink.setText('<a href="https://sites.google.com/view/manual-uso-decifra">https://sites.google.com/view/manual-uso-decifra</a>')

        self.label_LogoFapDF.setPixmap(QtGui.QPixmap(resource_path(r'icones\fapdfLogo.png')))

        self.label_logoIFB.setPixmap(QtGui.QPixmap(resource_path(r'icones\ifbLogoSemFundo.png')))

        self.labelLink.setOpenExternalLinks(True)

    #
    # MÉTODOS CORINGA {
    #
    def mostrarPopUpNaoSalvouArquivo(self):
        mensagem=QMessageBox()
        mensagem.setIcon(QMessageBox.Information)
        mensagem.setText("O arquivo não foi salvo")
        mensagem.setWindowTitle("Arquivo não foi salvo")
        mensagem.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
        mensagem.exec_()
    #
    # }
    #

    #
    # MÉTODOS DA ABA DETECTAR PICOS {
    #
    def inicializacao(self):
        self.X = None
        #self.valorLimite = self.doubleSpinBoxMudarLimite.value()
        self.limitePadrao = None
        self.arquivoXy = None
        self.intensidades = None
        self.angulos = None

        self.diretorioPadrao=None
        self.diretorioCIFs=None
        self.arrayAs3melhores = None
        self.dataFramePadraoNoTodo = None
        self.arrayDfNomesOrden = None
        self.arrayDfCompOrden=None
        self.numeroDeAbas=None
        self.arrayDfCIFsOrden=None
        self.verificou1=None
        self.valorSelecionado=None
        self.caminhoCIFs=None
        self.caminhoPadrao=None
        self.dialogo=None
        
        self.valorSelecionado2=None
        self.verificou2=None
        self.diretorioCIFs2=None
        self.diretorioPadrao2=None
        self.travaLogica=None
        self.dfPicos=None
        self.arrayPicos=[None, None, None, None,None]
        if self.ultimoIndex:
            self.removerItens()
        self.ultimoIndex=None

    def desativarQuaseTudo(self):
        #self.doubleSpinBoxMudarLimite.setEnabled(False)
        #self.pushButtonVisualizar.setEnabled(False)
        #self.pushButtonExportar.setEnabled(False)
        self.pushButtonDetectarCaerus.setEnabled(False)
        self.pushButtonDetectarTopyPeakDetec.setEnabled(False)
        self.botaoSelecPadrao.setEnabled(False)
        self.caminhoPadraotextEdit.setText('Aguardando a detecção dos picos...')
        self.botaoSelecCIF.setEnabled(False)
        self.caminhoCIFstextEdit.setText('Aguardando a detecção dos picos...')
        self.caixaRadiacoes.setEnabled(False)
        self.botaoComparar.setEnabled(False)
        self.botaoSelecPadrao_2.setEnabled(False)
        self.caminhoPadraotextEdit_2.setText('Aguardando a detecção dos picos...')
        self.comboBoxPico1.setEnabled(False)
        self.comboBoxPico2.setEnabled(False)
        self.comboBoxPico3.setEnabled(False)
        self.comboBoxPico4.setEnabled(False)
        self.comboBoxPico5.setEnabled(False)
        self.botaoSelecCIF_2.setEnabled(False)
        self.caminhoCIFstextEdit_2.setText('Aguardando a detecção dos picos...')
        self.caixaRadiacoes_2.setEnabled(False)
        self.botaoComparar_2.setEnabled(False)

    def ativarTudo(self):
        #self.doubleSpinBoxMudarLimite.setEnabled(True)
        #self.pushButtonVisualizar.setEnabled(True)
        #self.pushButtonExportar.setEnabled(True)
        self.pushButtonDetectarCaerus.setEnabled(True)
        self.pushButtonDetectarTopyPeakDetec.setEnabled(True)
        self.botaoSelecPadrao.setEnabled(True)
        self.caminhoPadraotextEdit.setText('O caminho aparecerá aqui quando selecionado')
        self.botaoSelecCIF.setEnabled(True)
        self.caminhoCIFstextEdit.setText('O caminho aparecerá aqui quando selecionado')
        self.caixaRadiacoes.setEnabled(True)
        self.botaoComparar.setEnabled(True)
        self.botaoSelecPadrao_2.setEnabled(True)
        self.caminhoPadraotextEdit_2.setText('O caminho aparecerá aqui quando selecionado')
        self.comboBoxPico1.setEnabled(True)
        self.comboBoxPico2.setEnabled(True)
        self.comboBoxPico3.setEnabled(True)
        self.comboBoxPico4.setEnabled(True)
        self.comboBoxPico5.setEnabled(True)
        self.botaoSelecCIF_2.setEnabled(True)
        self.caminhoCIFstextEdit_2.setText('O caminho aparecerá aqui quando selecionado')
        self.caixaRadiacoes_2.setEnabled(True)
        self.botaoComparar_2.setEnabled(True)
    #Esse método também é um pouco diferente do comum
    def abrirArquivoEventXy(self):
        self.arquivoXy=None
        opcoes = QFileDialog.Options()
        #Aqui muda um pouco para procurar arquivos .xy, não entendi 
        # bem como ele faz a busca especificamente por .xy, 
        # não ficou muito claro nas linhas de código
        arquivoXy, _ = QFileDialog.getOpenFileName(self, 'Selecionar arquivo .xy', '', 'Arquivos XY (*.xy);;Todos os arquivos (*)', options=opcoes)
        #Se o atributo do arquivo não está vazio
        if arquivoXy:
            
            self.arquivoXy=arquivoXy
            self.ativarTudo()
            self.caminhoXYtextEdit.setText(arquivoXy)
            # Ler o arquivo .xy e forma o dataframe com ângulos e intensidades do padrão
            dataFramePadrao = pd.read_csv(self.arquivoXy, delim_whitespace=True, header=None, names=['x','y'])

            # MÓDULO PARA FACILITAÇÃO DA UTILIZAÇÃO DO MÉTODO TOPOLOGYZ - INÍCIO
            #print(dataFramePadrao['y'].min())
            fatorDeEscala=100/(dataFramePadrao['y'].min())
            dataFramePadrao['y']=dataFramePadrao['y']*fatorDeEscala
            # MÓDULO PARA FACILITAÇÃO - FIM

            # Pega os ângulos (Dados da coluna 'x') e coloca em uma array
            self.angulos=dataFramePadrao.x.values
            # Pega os ângulos (Dados da coluna 'y') e coloca em uma array
            self.intensidades=dataFramePadrao.y.values
            #Endereça a uma nova array
            self.X = self.intensidades
            # Aqui o atibuto armazena o valor do score padrão 
            # para o método com homologia persistente 
            # do findpeaks
            #self.limitePadrao=np.min(np.min(self.X))-1
            #self.doubleSpinBoxMudarLimite.setEnabled(True)
            # Coloca o valor apresentado no doubleSpin como sendo o
            # valor do score padrão
            #self.doubleSpinBoxMudarLimite.setValue(self.limitePadrao)
            #self.pushButtonVisualizar.setEnabled(True)
            #self.pushButtonExportar.setEnabled(True)
            # Inicia o método para mostrar o padrão numa label
            # enquanto os dados do padrão estiverem carregados
            #self.mostrarLimitePadrao()
        else:
            self.X=None
            self.intensidades=None
            self.angulos=None
            self.arquivoXy=None
            self.limitePadrao=None
            #self.mostrarLimitePadrao()
            # Coloca o valor como 0
            #self.doubleSpinBoxMudarLimite.setValue(0)
            #self.valorLimite=None
            self.caminhoXYtextEdit.setText('O caminho aparecerá aqui quando selecionado')
            self.desativarQuaseTudo()
            self.inicializacao()

    def iniciarJanelaDeteccaoSemRuidos(self):
        
        self.deletouAdicionouCelulas = False
        self.dataFramePicos=None

        # É importante falar que essa ideia da estrutura 
        # do "if self.arquivoXy e else" não faz mais tanto 
        # sentido mas mantenho por falta de motivos para 
        # retirar - Mesmo que sinceramente não há problemas 
        # para retirar, aparentemente

        if self.arquivoXy:
            # Criação do objeto da classe 
            # Ui_MainWindow_detectorPicosSemRuido()
            self.uiGraficoDeteccaoSemRuidos = Ui_MainWindow_detectorPicosSemRuido()
            # Criação do objeto da classe pai
            self.windowSR = QtWidgets.QMainWindow()
            # Utilização do método da classe citada anterior e 
            # utilização do objeto da classe pai como parâmetro
            self.uiGraficoDeteccaoSemRuidos.setupUi(self.windowSR)
            self.windowSR.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
            # Mostrar a janela
            self.windowSR.show()
            # Variável para referenciar o layout do container frame do gráfico
            self.layout = self.uiGraficoDeteccaoSemRuidos.gridLayout_GraficoSR

            self.uiGraficoDeteccaoSemRuidos.comboBoxMetodos.setItemData(0,None)
            self.uiGraficoDeteccaoSemRuidos.comboBoxMetodos.setItemData(1,'peakdetect')
            self.uiGraficoDeteccaoSemRuidos.comboBoxMetodos.setItemData(2,'topology')
            # Agora é um objeto da FigureCanvas que vai criar o 
            # gráfico. É importante inicializar esse atributo aqui 
            # junto ao método da criação de objeto da segunda janela 
            # para garantir que não haja problemas com o fechar da 
            # janela (O que indica a destruição desse atributo)
            self.canvas = FigureCanvas(Figure(figsize=(5,4)))
            # Criando esse objeto para aparecer a toolbar que estava 
            # presente quando se usava o plt.show()

            self.ax = self.canvas.figure.add_subplot(111)

            #A observação da primeira inicialização aqui vale para o 
            # atributo toolbar também
            self.toolbar = NavigationToolBar(self.canvas, self)

            self.uiGraficoDeteccaoSemRuidos.horizontalSliderParametroDeteccao.valueChanged.connect(self.mostrarGraficoTabelaDeteccaoPicosSemRuido)

            self.uiGraficoDeteccaoSemRuidos.comboBoxMetodos.currentIndexChanged.connect(self.verificarIndexDoQComboBox)

            self.uiGraficoDeteccaoSemRuidos.spinBoxLimiteInferior.setValue(0)

            self.uiGraficoDeteccaoSemRuidos.spinBox_LimiteSuperior.setValue(100)

            self.uiGraficoDeteccaoSemRuidos.labelLimiteInferior.setText(str(self.uiGraficoDeteccaoSemRuidos.spinBoxLimiteInferior.value()))

            self.uiGraficoDeteccaoSemRuidos.labelLimiteSuperior.setText(str(self.uiGraficoDeteccaoSemRuidos.spinBox_LimiteSuperior.value()))

            self.uiGraficoDeteccaoSemRuidos.doubleSpinBoxValorPassoSlider.setValue(1)

            self.uiGraficoDeteccaoSemRuidos.label_valorPasso.setText(f"Cada passo equivale a {str(self.uiGraficoDeteccaoSemRuidos.doubleSpinBoxValorPassoSlider.value())}")

            self.uiGraficoDeteccaoSemRuidos.spinBoxLimiteInferior.valueChanged.connect(self.configurarSliderHorizontal)

            self.uiGraficoDeteccaoSemRuidos.spinBox_LimiteSuperior.valueChanged.connect(self.configurarSliderHorizontal)

            self.uiGraficoDeteccaoSemRuidos.doubleSpinBoxValorPassoSlider.valueChanged.connect(self.configurarSliderHorizontal)

            self.tabela=self.uiGraficoDeteccaoSemRuidos.tableViewAnguloIntensidade

            self.tabela.setContextMenuPolicy(Qt.CustomContextMenu)

            self.tabela.customContextMenuRequested.connect(self.abrirMenuContexto)

            self.tabela.clicked.connect(self.celulaSelecionada)

            self.uiGraficoDeteccaoSemRuidos.pushButtonExportarPicos.clicked.connect(lambda: self.popUpExportAngulos('pushButtonExportarPicos'))

            self.uiGraficoDeteccaoSemRuidos.pushButtonUtilizarPicos.clicked.connect(lambda: self.utilizarPicosDetectados('pushButtonUtilizarPicos'))

            self.uiGraficoDeteccaoSemRuidos.pushButtonUtilizarPicos.clicked.connect(lambda: self.utilizarPicosDetectados2('pushButtonUtilizarPicos'))
            
            self.mostrarGraficoTabelaDeteccaoPicosSemRuido()

        else:
            raise ValueError('O arquivo .xy não foi selecionado.')

    def clicouNoGrafico(self, event):

        if event.button == 3:
            
            menu = QMenu(self)

            menu.addAction("Adicionar esse ângulo como pico", lambda: self.adicionarPico(event))

            menu.exec_(self.canvas.mapToGlobal(QPoint(event.x, event.y)))

    def adicionarPico(self, event):

        if event.xdata is not None and event.ydata is not None:
            distancias = [abs(x - event.xdata) for x in self.angulos]
            indiceMaisProximo = distancias.index(min(distancias))
            anguloAdicionado = self.angulos[indiceMaisProximo]
            intensidadeAnguloAdicionado = self.intensidades[indiceMaisProximo]
            novoPico = {"Ângulo": anguloAdicionado, "Intensidade": intensidadeAnguloAdicionado}
            self.dataFramePicos = pd.concat([self.dataFramePicos, pd.DataFrame([novoPico])], ignore_index = True)
            # Ordenar as linhas pelos valores do ângulo
            self.dataFramePicos = self.dataFramePicos.sort_values(by="Ângulo").reset_index(drop=True)
            self.deletouAdicionouCelulas = True
            self.mostrarGraficoTabelaDeteccaoPicosSemRuido()

    def configurarSliderHorizontal(self):

        slider = self.uiGraficoDeteccaoSemRuidos.horizontalSliderParametroDeteccao

        labelLimiteInferior = self.uiGraficoDeteccaoSemRuidos.labelLimiteInferior

        labelLimiteSuperior = self.uiGraficoDeteccaoSemRuidos.labelLimiteSuperior

        labelValorPasso = self.uiGraficoDeteccaoSemRuidos.label_valorPasso

        limiteInferior = self.uiGraficoDeteccaoSemRuidos.spinBoxLimiteInferior.value()

        limiteSuperior = self.uiGraficoDeteccaoSemRuidos.spinBox_LimiteSuperior.value()

        valorPasso = self.uiGraficoDeteccaoSemRuidos.doubleSpinBoxValorPassoSlider.value()

        if limiteInferior < limiteSuperior:

            slider.setMinimum(limiteInferior)

            labelLimiteInferior.setText(str(limiteInferior))

            slider.setMaximum(limiteSuperior)

            labelLimiteSuperior.setText(str(limiteSuperior))

        slider.setSingleStep(int(valorPasso))

        labelValorPasso.setText(f"Cada passo equivale a {str(int(valorPasso))}")

    def abrirMenuContexto(self, position: QPoint):

        index = self.tabela.indexAt(position)
        if not index.isValid():
            return
        
        self.celulaSelecionada(index)
        
        row = index.row()

        menu = QMenu(self)
        acaoDeletar = menu.addAction("Deletar")

        action = menu.exec_(self.tabela.viewport().mapToGlobal(position))

        if action == acaoDeletar:

            if 0 <= row < self.modelo._data.shape[0]:

                self.modelo._data.drop(index=row, inplace=True)
                self.modelo._data.reset_index(drop=True, inplace=True)
                self.modelo.layoutChanged.emit()

                self.dataFramePicos = self.modelo._data.copy()
                self.deletouAdicionouCelulas = True
                self.mostrarGraficoTabelaDeteccaoPicosSemRuido()

            else:
                raise ValueError(f"A linha {row} é inválida.")

    def celulaSelecionada(self, index):
        for bar in self.ax.patches:
            bar.remove()
        row=index.row()
        self.ax.bar(self.dataFramePicos.iloc[row,0],self.dataFramePicos.iloc[row,1], color='red', width=0.1)
        self.canvas.draw()

    # Para garantir que a atualização do gráfico mediante QComboBox 
    # só aconteça em caso do item selecionado ser 'Nenhum'
    def verificarIndexDoQComboBox(self, index):
        if index == 0:
            self.mostrarGraficoTabelaDeteccaoPicosSemRuido()

    def mostrarGraficoTabelaDeteccaoPicosSemRuido(self):

        """print(self.ax.get_children())"""
        
        """# Esse comando hasattr serve para ver se o objeto (self) 
        # (Creio que da classe da primeira janela, mesmo que o 
        # atributo canvas seja adicionado ao layout da segunda 
        # janela) tem um atributo chamado canvas
        
        if hasattr(self, 'canvas'):
            # Se sim, primeiro remove esse atributo do layout
            self.layout.removeWidget(self.canvas)
            # Caso não seja vazio
            if self.canvas is not None:
                #Comando para destruir esse atributo da memória após o fim do evento
                self.canvas.deleteLater()
            # Tornar o atributo vazio
            self.canvas = None

        if hasattr(self, 'toolbar'):
            self.layout.removeWidget(self.toolbar)
            if self.toolbar is not None:
                self.toolbar.deleteLater()
            self.toolbar = None

        self.valorLimite=self.uiGraficoDeteccaoSemRuidos.horizontalSliderParametroDeteccao.value()
        
        self.valorPasso=self.uiGraficoDeteccaoSemRuidos.doubleSpinBoxValorPassoSlider.value()

        # Novamente inicializa-se os atributos anteriormente 
        # destruídos a fim de haver uma atualização do gráfico
        self.canvas = FigureCanvas(Figure(figsize=(5,4)))
        # O canvas é basicamente um quadro

        # O gráfico em si é feito pelo ax (axes - eixos)

        # O add_subplot permite isso com parâmetros numéricos que 
        # não vou entrar em detalhes
        self.ax = self.canvas.figure.add_subplot(111)"""
        if hasattr(self, 'canvas'):
            pass
        else:
            self.canvas = FigureCanvas(Figure(figsize=(5,4)))
            self.ax = self.canvas.figure.add_subplot(111)

        #self.ax.clear()

        # Remover plots do tipo ax.plot
        for line in self.ax.lines:
            line.remove()

        # Remover scatter plots
        for collection in self.ax.collections:
            collection.remove()

        # Remover patches (como barras)
        for patch in self.ax.patches:
            patch.remove()

        # Remover a legenda
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

        self.ax.plot(self.angulos, self.intensidades, label='Dados', color='blue', linestyle='-', marker='.')

        self.canvas.mpl_connect('button_press_event', self.clicouNoGrafico)

        self.valorLimite=self.uiGraficoDeteccaoSemRuidos.horizontalSliderParametroDeteccao.value()

        self.metodoEscolhido = self.uiGraficoDeteccaoSemRuidos.comboBoxMetodos.currentData()

        if self.deletouAdicionouCelulas == True:

            self.modelo = PandasModel(self.dataFramePicos)

            self.tabela.setModel(self.modelo)

            self.modelo.layoutChanged.emit()

            self.ax.scatter(self.dataFramePicos["Ângulo"], self.dataFramePicos["Intensidade"], color="red", label="Picos")

        else:

            if self.metodoEscolhido == 'topology':

                fp = findpeaks(method=self.metodoEscolhido,limit=self.valorLimite, verbose=0)
                results = fp.fit(self.X)
                angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
                
                self.ax.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
                self.ax.set_title(f"Picos detectados com limit igual a {self.valorLimite}", fontsize=15)

                self.dataFramePicos = pd.DataFrame({'Ângulo':self.angulos[angulosPicos],'Intensidade': self.intensidades[angulosPicos]})

                self.modelo = PandasModel(self.dataFramePicos)

                self.tabela.setModel(self.modelo)


            if self.metodoEscolhido == 'peakdetect':
                
                fp = findpeaks(method=self.metodoEscolhido,lookahead=self.valorLimite, verbose=0)
                results = fp.fit(self.X)
                angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
                
                self.ax.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
                self.ax.set_title(f"Picos detectados com lookahead igual a {self.valorLimite}", fontsize=15)

                self.dataFramePicos = pd.DataFrame({'Ângulo':self.angulos[angulosPicos],'Intensidade': self.intensidades[angulosPicos]})

                self.modelo = PandasModel(self.dataFramePicos)

                self.tabela.setModel(self.modelo)

                
            if self.metodoEscolhido == None:

                self.ax.set_title("", fontsize=15)

                self.tabela=self.uiGraficoDeteccaoSemRuidos.tableViewAnguloIntensidade

                self.dataFramePicos = pd.DataFrame(columns=['Ângulo','Intensidade'])

                self.modelo = PandasModel(self.dataFramePicos)

                self.tabela.setModel(self.modelo)
                
                #self.canvas.draw

        # Colocando título e labels dos eixos com seus 
        # respectivos tamanhos de fonte
        self.ax.set_xlabel("2θ (°)", fontsize=14)
        self.ax.set_ylabel("Intensidade (u.a.)", fontsize=14)
        
        # Importante lembrar desse comando abaixo caso queira que 
        # sua label apareça corretamente
        self.ax.legend()

        self.canvas.draw()

        if not hasattr(self, 'toolbar'):
            self.toolbar = NavigationToolBar(self.canvas, self)
        
        """# Novamente inicialização para atualização do gráfico no 
        # todo
        self.toolbar = NavigationToolBar(self.canvas, self)"""

        # Adicionando o gráfico e a toolbar ao layout
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self.deletouAdicionouCelulas = False

    def iniciarJanelaDeteccaoComRuidos(self):
        
        self.deletouAdicionouCelulasCR = False
        self.dataFramePicosCR=None
        

        # É importante falar que essa ideia da estrutura 
        # do "if self.arquivoXy e else" não faz mais tanto 
        # sentido mas mantenho por falta de motivos para 
        # retirar - Mesmo que sinceramente não há problemas 
        # para retirar, aparentemente

        if self.arquivoXy:
            # Criação do objeto da classe 
            # Ui_MainWindow_detectorPicosComRuido()
            self.uiGraficoDeteccaoComRuidos = Ui_MainWindow_detectorPicosComRuido()
            # Criação do objeto da classe pai
            self.windowCR = QtWidgets.QMainWindow()
            # Utilização do método da classe citada anterior e 
            # utilização do objeto da classe pai como parâmetro
            self.uiGraficoDeteccaoComRuidos.setupUi(self.windowCR)
            # Mostrar a janela
            self.windowCR.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
            self.windowCR.show()
            # Variável para referenciar o layoutCR do container frame do gráfico
            self.layoutCR = self.uiGraficoDeteccaoComRuidos.gridLayout_Grafico
            
            # Agora é um objeto da FigureCanvas que vai criar o 
            # gráfico. É importante inicializar esse atributo aqui 
            # junto ao método da criação de objeto da segunda janela 
            # para garantir que não haja problemas com o fechar da 
            # janela (O que indica a destruição desse atributo)
            self.canvasCR = FigureCanvas(Figure(figsize=(5,4)))
            # Criando esse objeto para aparecer a toolbar que estava 
            # presente quando se usava o plt.show()

            self.axCR = self.canvasCR.figure.add_subplot(111)

            #A observação da primeira inicialização aqui vale para o 
            # atributo toolbar também
            self.toolbar = NavigationToolBar(self.canvasCR, self)

            self.uiGraficoDeteccaoComRuidos.pushButtonDetectar.clicked.connect(self.mostrarGraficoTabelaDeteccaoPicosComRuido)

            self.uiGraficoDeteccaoComRuidos.spinBoxLimiteInferiorWindow.setValue(0)

            self.uiGraficoDeteccaoComRuidos.spinBox_LimiteSuperiorWindow.setValue(100)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteInferiorThreshold.setValue(0)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteSuperiorThreshold.setValue(1)

            self.uiGraficoDeteccaoComRuidos.labelLimiteInferiorWindow.setText(str(self.uiGraficoDeteccaoComRuidos.spinBoxLimiteInferiorWindow.value()))

            self.uiGraficoDeteccaoComRuidos.labelLimiteSuperiorWindow.setText(str(self.uiGraficoDeteccaoComRuidos.spinBox_LimiteSuperiorWindow.value()))

            self.uiGraficoDeteccaoComRuidos.labelLimiteInferiorThreshold.setText(str(self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteInferiorThreshold.value()))

            self.uiGraficoDeteccaoComRuidos.labelLimiteSuperiorThreshold.setText(str(self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteSuperiorThreshold.value()))

            self.uiGraficoDeteccaoComRuidos.spinBoxValorPassoWindow.setValue(1)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxValorPassoThreshold.setValue(0.001)

            self.uiGraficoDeteccaoComRuidos.labelCadaPassoEquivaleParametroWindow.setText(f"Cada passo equivale a {str(self.uiGraficoDeteccaoComRuidos.spinBoxValorPassoWindow.value())}")

            self.uiGraficoDeteccaoComRuidos.labelCadaPassoEquivaleParametroThreshold.setText(f"Cada passo equivale a {str(self.uiGraficoDeteccaoComRuidos.doubleSpinBoxValorPassoThreshold.value())}")

            self.uiGraficoDeteccaoComRuidos.labelValorParametroWindow.setText(f"Window: {self.uiGraficoDeteccaoComRuidos.horizontalSliderParametroWindow.value()}")

            self.uiGraficoDeteccaoComRuidos.horizontalSliderParametroWindow.valueChanged.connect(self.atualizarLabelDoParametroWindow)

            self.uiGraficoDeteccaoComRuidos.spinBoxLimiteInferiorWindow.valueChanged.connect(self.configurarSliderHorizontalWindow)

            self.uiGraficoDeteccaoComRuidos.spinBox_LimiteSuperiorWindow.valueChanged.connect(self.configurarSliderHorizontalWindow)

            self.uiGraficoDeteccaoComRuidos.spinBoxValorPassoWindow.valueChanged.connect(self.configurarSliderHorizontalWindow)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteInferiorThreshold.valueChanged.connect(self.configurarSliderHorizontalThreshold)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteSuperiorThreshold.valueChanged.connect(self.configurarSliderHorizontalThreshold)

            self.uiGraficoDeteccaoComRuidos.doubleSpinBoxValorPassoThreshold.valueChanged.connect(self.configurarSliderHorizontalThreshold)

            self.tabelaCR=self.uiGraficoDeteccaoComRuidos.tableViewAngIntCaerus

            self.tabelaCR.setContextMenuPolicy(Qt.CustomContextMenu)

            self.tabelaCR.customContextMenuRequested.connect(self.abrirMenuContextoCR)

            self.tabelaCR.clicked.connect(self.celulaSelecionadaCR)

            self.uiGraficoDeteccaoComRuidos.pushButtonExportarPicosCaerus.clicked.connect(lambda: self.popUpExportAngulos('pushButtonExportarPicosCaerus'))

            self.uiGraficoDeteccaoComRuidos.pushButton_UtilizarPicosCaerus.clicked.connect(lambda: self.utilizarPicosDetectados('pushButton_UtilizarPicosCaerus'))

            self.uiGraficoDeteccaoComRuidos.pushButton_UtilizarPicosCaerus.clicked.connect(lambda: self.utilizarPicosDetectados2('pushButton_UtilizarPicosCaerus'))
            
            self.mostrarGraficoTabelaDeteccaoPicosComRuido()

        else:
            raise ValueError('O arquivo .xy não foi selecionado.')

    def atualizarLabelDoParametroWindow(self):
        self.uiGraficoDeteccaoComRuidos.labelValorParametroWindow.setText(f"Window: {self.uiGraficoDeteccaoComRuidos.horizontalSliderParametroWindow.value()}")

    def clicouNoGraficoCR(self, event):

        if event.button == 3:
            
            menu = QMenu(self)

            menu.addAction("Adicionar esse ângulo como pico", lambda: self.adicionarPicoCR(event))

            menu.exec_(self.canvasCR.mapToGlobal(QPoint(event.x, event.y)))

    def adicionarPicoCR(self, event):

        if event.xdata is not None and event.ydata is not None:
            distancias = [abs(x - event.xdata) for x in self.angulos]
            indiceMaisProximo = distancias.index(min(distancias))
            anguloAdicionado = self.angulos[indiceMaisProximo]
            intensidadeAnguloAdicionado = self.intensidades[indiceMaisProximo]
            novoPico = {"Ângulo": anguloAdicionado, "Intensidade": intensidadeAnguloAdicionado}
            self.dataFramePicosCR = pd.concat([self.dataFramePicosCR, pd.DataFrame([novoPico])], ignore_index = True)
            # Ordenar as linhas pelos valores do ângulo
            self.dataFramePicosCR = self.dataFramePicosCR.sort_values(by="Ângulo").reset_index(drop=True)
            self.deletouAdicionouCelulasCR = True
            self.mostrarGraficoTabelaDeteccaoPicosComRuido()

    def configurarSliderHorizontalWindow(self):

        slider = self.uiGraficoDeteccaoComRuidos.horizontalSliderParametroWindow

        labelLimiteInferior = self.uiGraficoDeteccaoComRuidos.labelLimiteInferiorWindow

        labelLimiteSuperior = self.uiGraficoDeteccaoComRuidos.labelLimiteSuperiorWindow

        labelValorPasso = self.uiGraficoDeteccaoComRuidos.labelCadaPassoEquivaleParametroWindow

        limiteInferior = self.uiGraficoDeteccaoComRuidos.spinBoxLimiteInferiorWindow.value()

        limiteSuperior = self.uiGraficoDeteccaoComRuidos.spinBox_LimiteSuperiorWindow.value()

        valorPasso = self.uiGraficoDeteccaoComRuidos.spinBoxValorPassoWindow.value()

        if limiteInferior < limiteSuperior:

            slider.setMinimum(limiteInferior)

            labelLimiteInferior.setText(str(limiteInferior))

            slider.setMaximum(limiteSuperior)

            labelLimiteSuperior.setText(str(limiteSuperior))

        slider.setSingleStep(int(valorPasso))

        labelValorPasso.setText(f"Cada passo equivale a {str(valorPasso)}")

    def configurarSliderHorizontalThreshold(self):

        doubleSpinBox = self.uiGraficoDeteccaoComRuidos.doubleSpinBoxParametroThreshold

        labelLimiteInferior = self.uiGraficoDeteccaoComRuidos.labelLimiteInferiorThreshold

        labelLimiteSuperior = self.uiGraficoDeteccaoComRuidos.labelLimiteSuperiorThreshold

        labelValorPasso = self.uiGraficoDeteccaoComRuidos.labelCadaPassoEquivaleParametroThreshold

        limiteInferior = self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteInferiorThreshold.value()

        limiteSuperior = self.uiGraficoDeteccaoComRuidos.doubleSpinBoxLimiteSuperiorThreshold.value()

        valorPasso = self.uiGraficoDeteccaoComRuidos.doubleSpinBoxValorPassoThreshold.value()

        if limiteSuperior > limiteInferior:

            doubleSpinBox.setMinimum(limiteInferior)

            labelLimiteInferior.setText(f"{limiteInferior:.3f}")

            doubleSpinBox.setMaximum(limiteSuperior)

            labelLimiteSuperior.setText(f"{limiteSuperior:.3f}")

        doubleSpinBox.setSingleStep(valorPasso)

        labelValorPasso.setText(f"Cada passo equivale a {valorPasso:.3f}")

    def abrirMenuContextoCR(self, position: QPoint):

        index = self.tabelaCR.indexAt(position)
        if not index.isValid():
            return
        
        self.celulaSelecionadaCR(index)
        
        row = index.row()

        menu = QMenu(self)
        acaoDeletar = menu.addAction("Deletar")

        action = menu.exec_(self.tabelaCR.viewport().mapToGlobal(position))

        if action == acaoDeletar:

            if 0 <= row < self.modeloCR._data.shape[0]:

                self.modeloCR._data.drop(index=row, inplace=True)
                self.modeloCR._data.reset_index(drop=True, inplace=True)
                self.modeloCR.layoutChanged.emit()

                self.dataFramePicosCR = self.modeloCR._data.copy()
                self.deletouAdicionouCelulasCR = True
                self.mostrarGraficoTabelaDeteccaoPicosComRuido()

            else:
                raise ValueError(f"A linha {row} é inválida.")

    def celulaSelecionadaCR(self, index):
        for patch in self.axCR.patches:
            patch.remove()
        row=index.row()
        self.axCR.bar(self.dataFramePicosCR.iloc[row,0],self.dataFramePicosCR.iloc[row,1], color='red', width=0.1)
        self.canvasCR.draw()

    def mostrarGraficoTabelaDeteccaoPicosComRuido(self):

        if hasattr(self, 'canvasCR'):
            pass
        else:
            self.canvasCR = FigureCanvas(Figure(figsize=(5,4)))
            self.axCR = self.canvasCR.figure.add_subplot(111)

        # Remover plots do tipo axCR.plot
        for line in self.axCR.lines:
            line.remove()

        # Remover scatter plots
        for collection in self.axCR.collections:
            collection.remove()

        # Remover patches (como barras)
        for patch in self.axCR.patches:
            patch.remove()

        # Remover a legenda
        if self.axCR.get_legend() is not None:
            self.axCR.get_legend().remove()

        self.axCR.plot(self.angulos, self.intensidades, label='Dados', color='blue', linestyle='-', marker='.')

        self.canvasCR.mpl_connect('button_press_event', self.clicouNoGraficoCR)

        self.valorLimiteWindow=self.uiGraficoDeteccaoComRuidos.horizontalSliderParametroWindow.value()

        self.valorLimiteThreshold=self.uiGraficoDeteccaoComRuidos.doubleSpinBoxParametroThreshold.value()
        
        if self.deletouAdicionouCelulasCR == True:

            self.modeloCR = PandasModel(self.dataFramePicosCR)

            self.tabelaCR.setModel(self.modeloCR)

            self.modeloCR.layoutChanged.emit()

            self.axCR.scatter(self.dataFramePicosCR["Ângulo"], self.dataFramePicosCR["Intensidade"], color="red", label="Picos")

        else:
            # Comando abaixo necessário para não aparecer 
            # um erro referente ao fato de que ele não 
            # conseguiu mostrar uma barra de carregamento 
            # em um console (SIMPLIFICAÇÃO ULTRA DEMASIADA)
            tqdm.disable = True
            fp = findpeaks(method='caerus', params={'window': self.valorLimiteWindow, 'threshold': self.valorLimiteThreshold}, verbose=0)
            results = fp.fit(self.X)
            angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
            
            self.axCR.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
            self.axCR.set_title(f"Picos detectados com window = {self.valorLimiteWindow} e threshold = {self.valorLimiteThreshold:.3f}", fontsize=15)

            self.dataFramePicosCR = pd.DataFrame({'Ângulo':self.angulos[angulosPicos],'Intensidade': self.intensidades[angulosPicos]})

            self.modeloCR = PandasModel(self.dataFramePicosCR)

            self.tabelaCR.setModel(self.modeloCR)



        # Colocando título e labels dos eixos com seus 
        # respectivos tamanhos de fonte
        self.axCR.set_xlabel("2θ (°)", fontsize=14)
        self.axCR.set_ylabel("Intensidade (u.a.)", fontsize=14)
        
        # Importante lembrar desse comando abaixo caso queira que 
        # sua label apareça corretamente
        self.axCR.legend()

        self.canvasCR.draw()

        if not hasattr(self, 'toolbar'):
            self.toolbar = NavigationToolBar(self.canvasCR, self)
        
        # Adicionando o gráfico e a toolbar ao layoutCR
        self.layoutCR.addWidget(self.toolbar)
        self.layoutCR.addWidget(self.canvasCR)

        self.deletouAdicionouCelulasCR = False
    # Abre um pop-up para escolha do diretório onde irá ser salvo a planilha com ângulos
    def popUpExportAngulos(self, nomeAtributo):
        if self.arquivoXy:
            nomeArquivo=None
            nomeAtributo=nomeAtributo
            opcoes=QFileDialog.Options()
            filtroDeArquivo = "Arquivos de texto (*.txt);;Todos os arquivos (*)"
            tituloPopUp=f"Exportar picos encontrados"
            nomeArquivo, _ = QFileDialog.getSaveFileName(self, tituloPopUp, "", filtroDeArquivo, options=opcoes)
            if nomeArquivo:
                # Se o o nome do arquivo não terminar com .txt
                if not nomeArquivo.endswith('.txt'):
                    # Adicione .txt
                    nomeArquivo += '.txt'
                # Mande o nome do arquivo com o diretório 
                # escolhido para o método que salvará
                # a planilha no diretório escolhido com
                # o nome escolhido
                self.salvarPlanilhaAngulos(nomeArquivo, nomeAtributo)
            else:
                # Caso o usuário desista de salvar emita um pop-up
                # informando que não foi salvo
                self.mostrarPopUpNaoSalvouArquivo
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
    # O método que vai receber o caminho e salvar no mesmo
    def salvarPlanilhaAngulos(self, parametroArquivo, nomeAtributo):
        dataFramePicos = None
        nomeAtributo = nomeAtributo
        if nomeAtributo == 'pushButtonExportarPicos':
            dataFramePicos = self.dataFramePicos
        if nomeAtributo == 'pushButtonExportarPicosCaerus':
            dataFramePicos = self.dataFramePicosCR
        nomeArquivo=parametroArquivo
        # Transforma em dataframe
        dataFrame_Picos=pd.DataFrame({'Ângulos': dataFramePicos['Ângulo'],'Intensidades': dataFramePicos["Intensidade"]})
        # Salva com o caminho e nome indicados
        with open(nomeArquivo, "w") as file:
            file.write(dataFrame_Picos.to_string(header=False, index=False))
        

    def utilizarPicosDetectados(self, nomeAtributo):
        horario = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        nomeAtributo = nomeAtributo
        dataFramePicos = None
        if nomeAtributo == 'pushButtonUtilizarPicos':
            dataFramePicos = self.dataFramePicos
        if nomeAtributo == 'pushButton_UtilizarPicosCaerus':
            dataFramePicos = self.dataFramePicosCR
        quantidadePicos=len(dataFramePicos)
        if nomeAtributo == 'pushButtonUtilizarPicos':
            self.caminhoPadraotextEdit.setText(f'Utilizando os {quantidadePicos} picos encontrados a partir dos métodos peak-detect ou topology às {horario}')
        if nomeAtributo == 'pushButton_UtilizarPicosCaerus':
            self.caminhoPadraotextEdit.setText(f'Utilizando os {quantidadePicos} picos encontrados a partir do método caerus às {horario}')
        self.dataFrameAngulos=pd.DataFrame({'Ângulos': dataFramePicos['Ângulo'], 'Intensidades': dataFramePicos['Intensidade']})
        self.UtilizouPicos1=True
        if nomeAtributo == "pushButtonUtilizarPicos":
            self.windowSR.close()
        if nomeAtributo == "pushButton_UtilizarPicosCaerus":
            self.windowCR.close()
        #print(self.dataFrameAngulos)
    #
    # }
    #

    #
    # MÉTODOS DA ABA COMPARAR PICOS {
    #

    # Método para abrir o explorer do computador e selecionar a pasta necessária
    def abrirDirEventCIFs(self):
        """
        Essa primeira linha de código garante que toda vez que o botão seja aberto
        e o diálogo de diretório seja iniciado o valor volte novamente a ser None não importa
        quantas vezes o usuário faz isso. Não sei se pode causar um erro no futuro, caso ocorra
        retirarei essa linha por ela não ser exatamente tão necessária. Essas medidas vão ser colocados no
        outro método de abrir diretórios também
        """
        self.diretorioCIFs=None      
        # Essa variável aloca a classe Options, não sei exatamente o que faz (Não entrei em detalhes)
        opcoes = QFileDialog.Options()
        # Não sei que operador é esse, mas essa função também dá a variável inicializada na linha anterior
        # a função de somente mostrar diretórios (pastas), nada de arquivos
        opcoes |= QFileDialog.ShowDirsOnly
        # Esse é o comando da caixinha que apresenta o explorer para o usuário selecionar a pasta
        # bem como essa variável aloca a string obtida (string do caminho da pasta) quando o usuário 
        # seleciona a pasta nessa caixinha criada (Entenda caixinha como a janela que abre do explorer)
        diretorioCIFs = QFileDialog.getExistingDirectory(self,'Selecionar Pasta dos CIFs','',options=opcoes)
        # Atualiza o atributo antigamente inicializado para receber como valor a string do caminho
        # da pasta
        self.diretorioCIFs=diretorioCIFs
        # laço condicional para mudar o texto da caixa de texto antes feita
        # Se diretorioCIFs não está vazio...
        if diretorioCIFs:
            # ...mude o texto da caixa de texto para o valor
            # do diretorioCIFs
            self.caminhoCIFstextEdit.setText(diretorioCIFs)
        # Essa segunda linha de código garante que caso o usuário não selecione nada no
        # diálogo de diretórios ele seja informado disso mostrando que não há caminho selecionado
        # Setar None é interessante pois no momento que o diálogo é iniciado, não importa se já
        # tivesse um caminho selecionado, novamente ele voltaria à mensagem padrão imediatamente
        # demonstrando que a informação do caminho já foi sobrescrita
        else:
            self.caminhoCIFstextEdit.setText('O caminho aparecerá aqui quando selecionado')
    # Não vou me estender, basicamente o mesmo do anterior
    def abrirDirEventSeuPadrao(self):
        self.dataFrameAngulos=None
        self.diretorioPadrao=None
        opcoes = QFileDialog.Options()
        filtroDeArquivo = "Arquivos de texto (*.txt);;Todos os arquivos (*)"
        tituloPopUp='Selecionar o arquivo do seu padrão de difração'
        arquivoPadrao, _ = QFileDialog.getOpenFileName(self,tituloPopUp,'', filtroDeArquivo, options=opcoes)
        self.diretorioPadrao=arquivoPadrao
        if arquivoPadrao:
            self.caminhoPadraotextEdit.setText(arquivoPadrao)
            self.UtilizouPicos1=False
        else:
            self.caminhoPadraotextEdit.setText('O caminho aparecerá aqui quando selecionado')
        
    # O método que tinha sido citado anteriormente que age junto ao caixaRadiacoes
    def itemSelecionado(self,index):
        self.valorSelecionado=self.caixaRadiacoes.itemData(index)
    # Método que verifica se os atributos do construtor de diretório dessa aba  
    # deixaram de ser Nones (vazios)
    def verificar(self):
        # Se os dois atributos estão preenchidos simultaneamente
        #( Não são mais vazios)
        if self.diretorioCIFs and (self.diretorioPadrao or self.UtilizouPicos1==True):
            # Atributos que vão receber e adicionar os caminhos em string para utilizar mais na frente
            self.caminhoCIFs=self.diretorioCIFs
            self.caminhoPadrao=self.diretorioPadrao
            # Mudamos a trava para permitir a entrada de dados
            # no contexto da tab Comparar Picos
            self.verificou2=False
            self.verificou1=True
            # Inicia a comparação
            self.compararPicos()
        # Se não
        else:
            self.verificou2=None
            self.verificou1=None
            # Se esse atributo ainda está vazio
            if not self.diretorioCIFs:
                #Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("A pasta dos CIFs não foi selecionado.")
            # Se esse atributo ainda está vazio
            if not self.diretorioPadrao:
                # Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("O arquivo do seu padrão de difração não foi selecionado e os picos detectados não foram utilizados.")

    # Método para comparar picos
    def compararPicos(self):
        self.mostrarInicio()

        self.picosDetectados = None
        # Variável responsável por armazenar qual tipo de arquivo deve ser buscado
        extensaoArquivo='*.cif'
        # Aqui se utiliza os valores das travas lógicas
        # passadas nos métodos de verificar para saber de
        # qual comboBox de radiação pegar o valor de com-
        # primento de onda
        if self.verificou1==True:
            #Variável para saber o comprimento de onda utilizado para montar os padrões de difração dos CIFs
            comprimentoOndaAngstron=self.valorSelecionado #Utiliza o valor selecionado na caixaRadiacoes
        elif self.verificou2==True:
            comprimentoOndaAngstron=self.valorSelecionado2
        # Arquivo que vai guardar o caminho do arquivo .xy
        #buscaXyPadrao = os.path.join(self.caminhoPadrao,'*.xy')
        # Transforma numa array de strings caminho
        #ArrayCaminhoXy=glob.glob(buscaXyPadrao)
        # Arquivo que vai guardar o caminho do arquivo .xlsx
        #buscaTabelaPadrao = os.path.join(self.caminhoPadrao,'*.txt')
        #ArrayCaminhoTabelaPadrao = glob.glob(buscaTabelaPadrao)
        # Coleta-se o único item dessa array criada na linha anterior
        caminhoPadrao=self.caminhoPadrao
        # DataFrame criado com os dados do arquivo .xy
        #dataFramePadraoNoTodo = pd.read_csv(ArrayCaminhoXy[0], delim_whitespace=True,header=None, names=['x','y'])
        # Contagem de linhas para determinar qual é a última linha do padrão
        #quantLinhasPadraoNoTodo = dataFramePadraoNoTodo['x'].count()
        quantLinhasPadraoNoTodo = len(self.angulos)
        ultimaLinha=quantLinhasPadraoNoTodo-1
        # Variável para ter o primeiro ângulo do nosso padrão de difração
        #primeiroAnguloPadrao=dataFramePadraoNoTodo.iloc[0,0]
        primeiroAnguloPadrao=self.angulos[0]
        # Variável para ter o último ângulo do nosso padrão de difração
        #UltimoAnguloPadrao=dataFramePadraoNoTodo.iloc[ultimaLinha,0]
        UltimoAnguloPadrao=self.angulos[ultimaLinha]
        # Se trata do comando para buscar os arquivos CIF no caminho especificado de maneira responsiva
        buscaDosCIFs=os.path.join(self.caminhoCIFs,extensaoArquivo)
        # Array com os caminhos de cada arquivo
        arrayCaminhosCIF=glob.glob(buscaDosCIFs)
        # Quantidade de arquivos e portanto de abas presentes na planilha dos CIFs e de comparação
        numeroDeAbas=len(arrayCaminhosCIF)
        #Array com os nomes dos arquivos feita utilizando uma sacada interessante do chamado "Compreensão de lista"
        #É uma maneira bem simples e rápida de criar uma array
        arrayNomesCIF=[os.path.basename(itemDoCaminhosCIF) for itemDoCaminhosCIF in arrayCaminhosCIF]
        # A partir daqui criamos uma array de DataFrames com 
        # ângulo e intensidade de cada CIF que será utilizado 
        # para comparar com o padrão de difração
        arrayDeDataFramesCIFs=[]
        for numeroAba in range(numeroDeAbas):
            # Seleciona o caminho do arquivo da lista de caminhos
            arquivoCIF=arrayCaminhosCIF[numeroAba]
            # Variável responsável por armazenar a leitura do 
            # arquivo .cif 
            # O nome da variável é em referência ao processo de 
            # parsing 
            # (Leitura de um arquivo, explicando de um jeito bem 
            # rude)
            parser = CifParser(arquivoCIF, occupancy_tolerance=100)
            # Variável para armazenar a estrutura cristalina do 
            # arquivo a partir dessa leitura
            # o [0] se deve ao fato de o parse_structures ser uma 
            # lista de estruturas
            # Isso eu já não sei explicar pois não me delonguei 
            # muito no módulo
            # O parâmetro primitive deve se relacionar à procura 
            # de células unitárias primitivas (True) ou não 
            # (False)
            estrutura = parser.parse_structures(primitive=False)[0]
            # Variável para obter grupo espacial
            analisador = SpacegroupAnalyzer(estrutura)
            # É importante adicionar essa condicional para os casos onde o arquivo .cif 
            # não apresenta uma notação válida para o space_group_symbol - Se bem que 
            # pelo que eu vi ele na verdade obtém a notação por meio das análises de 
            # simetria
            if analisador._space_group_data is not None:
                # Esse "_" na frente do space_group_data é uma convenção 
                # para indicar que se trata de um atributo interno e que 
                # não deve ser acessado diretamente por código externo. 
                # Pode ser que o atributo não seja de fato privado, mas 
                # por convenção ele é destinado a uso interno
                grupo_espacial = analisador.get_space_group_symbol()
            # Caso esteja vazio, deixe essa informação em branco
            else:
                grupo_espacial = ""
            # Segunda criação de variável para poder obter a 
            # fórmula química do CIF
            estruturaParaObterFormulasQuimicas = parser.get_structures()[0]
            # Obtenção da fórmula reduzida
            formulaQuimica = estruturaParaObterFormulasQuimicas.composition.reduced_formula
            # Aqui adiciono essas duas informações ao nome do 
            # arquivo presente nos itens da array arrayNomesCIF
            arrayNomesCIF[numeroAba]=f'{formulaQuimica}_{grupo_espacial}_{arrayNomesCIF[numeroAba]}'
            # Variável que guarda a configuração do calculador de 
            # difração de raio x ou x-ray diffraction (xrd)
            xrdCalculador = XRDCalculator(wavelength=comprimentoOndaAngstron)
            # Variável que guarda o padrão de difração com os 
            # valores de ângulo e intendidade do arquivo CIF
            xrdCIF = xrdCalculador.get_pattern(estrutura)
            # Aqui vamos criar uma variável que vai alocar um 
            # valor lógico, verdadeiro ou falso. No caso,
            # se o padrão calculado está dentro do intervalo 
            # pensado para o nosso padrão de difração.
            # Ângulo é uma variável temporária

            # Essa solução utilizando esse molde -
            # ('proposição com variável temporária' for 'variável 
            # temporária' in 'Dada array') -
            # está ficando cada vez mais comum e é cada vez mais 
            # interessante (Comentário fora de cronologia, 
            # desconsidere)
            angulosNoIntervalo=all(primeiroAnguloPadrao <= angulo <= UltimoAnguloPadrao for angulo in xrdCIF.x)
            # Se verdadeiro
            if angulosNoIntervalo:
                # Variável para alocar o dataFrame recém criado
                df = pd.DataFrame({"Ângulo-2theta": xrdCIF.x, "Intensidade": xrdCIF.y})
                # Por fim, esses dados devem ser transpostos em 
                # uma array
                arrayDeDataFramesCIFs.append(df)
            else:
                # Aqui ocorre uma filtragem para as únicas linhas 
                # que podem estar no dataframe
                # são linhas dentro do intervalo
                df = pd.DataFrame({"Ângulo-2theta": xrdCIF.x, "Intensidade": xrdCIF.y})
                linhasFiltradas= df.loc[(df["Ângulo-2theta"]>=primeiroAnguloPadrao) & (df["Ângulo-2theta"]<=UltimoAnguloPadrao)]
                df = linhasFiltradas
                arrayDeDataFramesCIFs.append(df)
        #Criacao da tabela que armazenara as linhas criadas
        dataFrameResultados=pd.DataFrame(columns=['Ângulos 2theta do seu padrão','Intensidades do seu padrão','Ângulos 2theta do CIF','Intensidade do CIF','Distância entre os picos','Intensidade relativa entre os picos','O pico corresponde?','Classificação do pico','Picos Excedentes','Picos Faltantes','Nota'])
        #Criação do DataFrame modelo vazio com todas as suas colunas correspondentes, tal modelo é que será utilizado em cada aba da planilha de saída
        arrayDataFramesComparacao=[] #Aqui é o array de DataFrames modelo, tal arranjo é importante para haver uma distinção autônoma de cada dataFrame para cada aba construída na planilha de saída

        for numeroAba in range(numeroDeAbas): #A função desse laço é criar cópias do DataFrame modelo e adicionar
                                    #as mesmas ao array
            dataFrameResultadosCopia=dataFrameResultados.copy() #Aqui a cópia é feita
            arrayDataFramesComparacao.append(dataFrameResultadosCopia) #Aqui a cópia é adicionada ao array
        #Então tudo se repete até o número da quantidade de abas da planilha de saída ser alcançado
        
        #Aqui vou criar uma array que vai armazenar a média aritmética das notas individuais da coluna nota
        arrayMedias=[]
        #Nesse próximo for começa a análise de fato, o primeiro for ler os dados das planilhas que você
        #passou e então chega no while que seleciona a linha da amostra que você quer comparar com o
        #seu padrão de difração e por fim o segundo while fica selecionando cada linha do padrão e com-
        #para todas elas com a linha escolhida no primeiro while

        #Criando variável que lerá os dados de pico na coluna 2theta da planilha do seu padrão designado
        if self.verificou1 == True:
            if self.UtilizouPicos1 == True:
                tabelaPadrao=self.dataFrameAngulos
                #print(tabelaPadrao)
                # LEMBRE-SE: ESSE É O CASO EM QUE OS PICOS DETECTADOS SÃO UTILIZADOS
            else:
                tabelaPadrao = pd.read_csv(caminhoPadrao,delim_whitespace=True,header=None,names=["Ângulos","Intensidades"])
                #print(tabelaPadrao)
                # AQUI OS PICOS QUE FORAM IMPORTADOS
        elif self.verificou2 == True:
            tabelaPadrao = self.dfPicos

        self.picosDetectados = tabelaPadrao

        variavelControladora=1
        # Essas serão as arrays para guardar as classificações gerais
        arrayDfCompOrdenGeral=[]
        arrayDfCIFsOrdenGeral=[]
        arrayDfNomesOrdenGeral=[]
        # Esse vai ser o contador de rodadas, esse dado será importante 
        # mais à frente
        numeroDeRodadas=0
        while variavelControladora==1:
            numeroDeRodadas+=1

            if numeroDeRodadas == 1:
    
                intensidadesTabelaPadrao=tabelaPadrao.Intensidades.values
                # Coletando a intensidade com maior pico para posterior uso
                maiorPicoPadrao = intensidadesTabelaPadrao.max()
                
                # Normalizando as intensidades para valores entre 0 e 1
                intensidadesPadraoNormalizadasPara1 = (intensidadesTabelaPadrao)/maiorPicoPadrao
                menorPicoPadrao =  intensidadesPadraoNormalizadasPara1.min()
                intensidadesPadraoNormalizadasPara1SemBackground = intensidadesPadraoNormalizadasPara1 - menorPicoPadrao

            for numeroAba in range(0,numeroDeAbas):
                # Trazendo o item da lista de dataframes do cif para comparacao
                tabelaAmostra = arrayDeDataFramesCIFs[numeroAba]
                #print(tabelaAmostra)
                # Trazendo o pico com maior intensidade desse CIF:
                # Primeiro, coletando a array de intensidades
                picosDoCIFemQuestao = tabelaAmostra.Intensidade.values
                #print(picosDoCIFemQuestao)
                maiorPicoCIF = picosDoCIFemQuestao.max()
                intensidadesCIFNormalizadasPara1 = picosDoCIFemQuestao/maiorPicoCIF
                # Criando variável para endereço da linha da amostra que vai ser comparada
                indexLinhaAmostra=0
                # Variável para o número máximo de iterações
                numeroLinhas=tabelaAmostra.iloc[:,0].count() # A função .iloc localiza linhas e colunas pelo seu índice
                                            # numérico que começa no 0, o : é para indicar que todas as linhas devem ser contadas
                                            # e o 0 é para indicar o índice da coluna (Que se espera ser a dos ângulos) a qual deve 
                                            # ser contada todas as linhas que não estão vazias, assim [linha,coluna]
                                            # e a função .count() é responsável pela tarefa de
                                            # contar essas linhas que não estão vazias
            
                #Variável para o indíce da linha que ajudará na adição de linhas para a tabela que foi criada
                contador=0
                #Variável que vai guardar o número de picos que não batem com o padrão
                picoExcedente=0
                #Variável que vai guardar o número de picos do padrão que não batem com o CIF
                picoFaltante=0
                #Essas variáveis...
                muitoBom=0
                bom=0
                medio=0
                poucoBom=0
                menosBom=0
                #...são para armazenar a quantidade de picos respectivos à cada classificação
                nota=0 #Uma variável para armazenar a nota individual de certo pico
                while indexLinhaAmostra < numeroLinhas:
                    #Variável que vai guardar o ângulo do pico que será analisado
                    picoDaVez=tabelaAmostra.iloc[indexLinhaAmostra,0] #<--Mudei de 0 para 1 para corresponder a um capricho meu
                    #Variável que vai guardar a intensidade do pico que será analisado. Antes era um capricho, mas após mudanças de fato é bom manter
                    #esse índice
                    intensidadePicoAmostra = intensidadesCIFNormalizadasPara1[indexLinhaAmostra]
                    # Criando variável para saber quantas linhas há na coluna em questão para servir de quantidade final ao while
                    numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
                    #Criando variável para o endereço de linha do seu padrão de difração que vai variar no laço while
                    indexLinhaPadrao=0
                    #Variável que vai guardar o número de rejeições a um dado pico da amostra
                    numeroRejeicoes=0

                    while indexLinhaPadrao < numeroLinhasPadrao:
                        # Criando variável para selecionar a linha do seu padrão que será comparado com a linha da amostra da vez
                        linhaPico=tabelaPadrao.iloc[indexLinhaPadrao,0]
                        #intensidadePicoPadrao = intensidadesPadraoNormalizadasPara1SemBackground[indexLinhaPadrao]
                        if indexLinhaPadrao < len(intensidadesPadraoNormalizadasPara1SemBackground):
                            intensidadePicoPadrao = intensidadesPadraoNormalizadasPara1SemBackground[indexLinhaPadrao]
                        else:
                            print(f"Index {indexLinhaPadrao} is out of bounds.")
                            print(len(intensidadesPadraoNormalizadasPara1SemBackground))
                        # Criando a variável que vai analisar o quão distante estão os ângulos
                        
                        distancia=abs(linhaPico-picoDaVez) #A função abs() retorna o valor absoluto de um certo valor, logo mesmo que
                                                        #essa subtração dê um valor negativo, virá o valor absoluto dela

                        nivelTolerancia = 1

                        """
                        Nível 1 -> Nível 2 -> Nível 5 -> Nível 10
                        0.5 -> 0.25 -> 0.10 -> 0.05
                        0.4 -> 0.20 -> 0.08 -> 0.04
                        0.3 -> 0.15 -> 0.06 -> 0.03
                        0.2 -> 0.10 -> 0.04 -> 0.02
                        0.1 -> 0.05 -> 0.02 -> 0.01
                        """

                        if distancia <= (0.1/nivelTolerancia):
                            notaDistancia=1
                            qualidade=self.calcularDesnivelEntrePicos(intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia)
                            if qualidade == 5:
                                muitoBom+=1
                            elif qualidade == 4:
                                bom+=1
                            elif qualidade == 3:
                                medio+=1
                            elif qualidade == 2:
                                poucoBom+=1
                            elif qualidade == 1:
                                menosBom+=1
                        elif (0.1/nivelTolerancia) < distancia <= (0.2/nivelTolerancia):
                            notaDistancia = 0.8
                            qualidade=self.calcularDesnivelEntrePicos(intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia)
                            if qualidade == 5:
                                muitoBom+=1
                            elif qualidade == 4:
                                bom+=1
                            elif qualidade == 3:
                                medio+=1
                            elif qualidade == 2:
                                poucoBom+=1
                            elif qualidade == 1:
                                menosBom+=1
                        elif (0.2/nivelTolerancia) < distancia <= (0.3/nivelTolerancia):
                            notaDistancia = 0.6
                            qualidade=self.calcularDesnivelEntrePicos(intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia)
                            if qualidade == 5:
                                muitoBom+=1
                            elif qualidade == 4:
                                bom+=1
                            elif qualidade == 3:
                                medio+=1
                            elif qualidade == 2:
                                poucoBom+=1
                            elif qualidade == 1:
                                menosBom+=1
                        elif (0.3/nivelTolerancia) < distancia <= (0.4/nivelTolerancia):
                            notaDistancia = 0.4
                            qualidade=self.calcularDesnivelEntrePicos(intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia)
                            if qualidade == 5:
                                muitoBom+=1
                            elif qualidade == 4:
                                bom+=1
                            elif qualidade == 3:
                                medio+=1
                            elif qualidade == 2:
                                poucoBom+=1
                            elif qualidade == 1:
                                menosBom+=1
                        elif (0.4/nivelTolerancia) < distancia <= (0.5/nivelTolerancia):
                            notaDistancia = 0.2
                            qualidade=self.calcularDesnivelEntrePicos(intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia)
                            if qualidade == 5:
                                muitoBom+=1
                            elif qualidade == 4:
                                bom+=1
                            elif qualidade == 3:
                                medio+=1
                            elif qualidade == 2:
                                poucoBom+=1
                            elif qualidade == 1:
                                menosBom+=1
                        # Cada loc tem como indície de linha a variável contador 
                        # que sempre vai somando 1 ao fim de cada linha padrão comparada
                        # com a linha amostra, utilizar o contador como indície de linha 
                        # no DataFrame é importante pois assim toda vez que um
                        # dos condicionais forem satisfeitos, o índicie utilizado 
                        # será um indície indisponível no DataFrame o que faz a função
                        # .loc[] adicionar essa linha
                        else:
                            numeroRejeicoes+=1
                        #Quando nenhum dos condicionais é satisfeito, é adicionado 1 na variável acima
                        if numeroRejeicoes == numeroLinhasPadrao:
                        #E caso esse número de rejeições seja igual ao número de linhas do padrão, ou seja, caso
                        #todos os ângulos do padrão rejeitem esse ângulo da amostra, é adicionado um na variável abaixo
                        #que indica a quantidade de picos que não correspondem com o padrão
                            picoExcedente+=1
                            nota=0
                        #Por fim, esse ângulo é exposto com uma linha só para ele
                            arrayDataFramesComparacao[numeroAba].loc[contador]=['-','-',picoDaVez,intensidadePicoAmostra,'-','-','Não','-','Sim','Não',nota]
                        # Cada loc tem como indície de linha a variável contador que sempre vai somando 1 ao fim de cada linha padrão comparada
                        # com a linha amostra, utilizar o contador como indície de linha no DataFrame é importante pois assim toda vez que um
                        # dos condicionais forem satisfeitos, o índicie utilizado será um indície indisponível no DataFrame o que faz a função
                        # .loc[] adicionar essa linha
                        
                        contador+=1
                        indexLinhaPadrao+=1
                    indexLinhaAmostra += 1
                # Agora inverte-se a ordem da escolha de picos para poder analisar o quanto de picos faltantes tem:
                # A lógica é: Escolha um pico do padrão, então o compare aos picos do CIF, caso nenhum pico corresponda,
                # isso mostra que que esse pico do padrão falta quando se trata em corresponder aos picos do CIF.
                contador += 1
                indexLinhaPadrao=0
                numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
                while indexLinhaPadrao < numeroLinhasPadrao:
                    linhaPico=tabelaPadrao.iloc[indexLinhaPadrao,0]
                    intensidadePicoPadrao=intensidadesPadraoNormalizadasPara1SemBackground[indexLinhaPadrao]
                    indexLinhaAmostra = 0
                    numeroLinhas=tabelaAmostra.iloc[:,1].count()
                    numeroRejeicoes=0
                    while indexLinhaAmostra < numeroLinhas:
                        picoDaVez=tabelaAmostra.iloc[indexLinhaAmostra,0]
                        distancia=abs(linhaPico-picoDaVez) 
                        if distancia > (0.5/nivelTolerancia):
                            numeroRejeicoes+=1
                        if numeroRejeicoes == numeroLinhas:
                            picoFaltante+=1
                            nota=0
                            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,'-','-','-','-','Não','-','Não','Sim',nota]
                        contador+=1
                        indexLinhaAmostra += 1
                    indexLinhaPadrao += 1
                df_temporario = arrayDataFramesComparacao[numeroAba].copy()
                numeroLinhas=len(arrayDataFramesComparacao[numeroAba])
                for i in range(0,numeroLinhas):
                    if isinstance(arrayDataFramesComparacao[numeroAba].iloc[i,10], str):
                        df_temporario.iloc[i, 10] = float('nan')
                # Variável que armazena a média das notas
                #print(df_temporario)
                mediaColunaNotas=df_temporario.iloc[1:,10].mean()
                # Comando para adicionar essa média na array de médias
                arrayMedias.append(mediaColunaNotas)
                contador+=1
                # Cada tabela deve ter uma linha com informações no final:
                arrayDataFramesComparacao[numeroAba].loc[contador]=['','Quantidade\nde Muito bom(s):','Quantidade\nde Bom(s):',
                                                            'Quantidade\nde Médio(s):','Quantidade\nde Pouco bom(s):',
                                                            'Quantidade\nde Ruim(s):','',''
                                                            ,'Quantidade\nde picos\nexcedentes:'
                                                            ,'Quantidade\nde picos\nfaltantes:','Nota\nfinal\né:']
                contador+=1
                arrayDataFramesComparacao[numeroAba].loc[contador]=['',muitoBom,bom,
                                                            medio,poucoBom,
                                                            menosBom,'',''
                                                            ,picoExcedente
                                                            ,picoFaltante,mediaColunaNotas]                                        
            
            # Agora vou ordenar todas as arrays criadas usando como critério de ordenação a média aritmética dos dataframes da arrayDataFramesComparacao
            # Para isso vou criar uma array que tem como item tuplas que guardam um conjunto de itens por vez das arrays selecionadas
            arrayMedCompCIFNomes=list(zip(arrayMedias,arrayDataFramesComparacao,arrayDeDataFramesCIFs,arrayNomesCIF)) # O zip() se responsabiliza por criar um iterável (Não pesquisei
            # ao certo o que isso significa, mas por intuição creio que seja uma variável que para acessar seus valores tem que se usar laços de iteração
            # como arrays (listas) ou tuplas) em que cada item é um conjunto de valores, um valor de um item da arrayMedias, um valor de um item da 
            # arrayDataFramesComparacao, um valor de um item da arrayDeDataFramesCIFs e um valor de um item da arrayNomesCIF, 
            # por sua vez o list() transforma isso numa array no todo.

            #Essa array criada é ordenada e alocada para a array seguinte, a ordenação é feita em função do item de arrayMedias da tupla
            array_ordenada_com_medias=sorted(arrayMedCompCIFNomes, key=lambda itemMedia: itemMedia[0], reverse=True)
            # Aqui temos a extração dos itens de DataFrame a partir 
            # da array ordenada de tuplas.
            # No caso, as variáveis temporárias representam os 4 itens 
            # presentes na tupla.
            # Então primeiro se escolhe quais desses itens será
            # escolhido para array e expõe
            # quais serão os nomes temporários desses itens e por fim se
            # referencia de qual array está se
            # tirando esses itens referenciados.
            # Essa utilização da compreensão de lista é algo poderoso
            # mas que eu não dominei bem. Sinto que pode ser aplicado 
            # nas partes mais a cima do código, por exemplo na criação da 
            # alocação de dataFrames. Em algum nível sinto que a criação 
            # dos dataframes pode se dar nos próprios encadeamentos do while 
            # com seu append feito nesse próprio array

            # Esses antes eram as arrays com os dataframes e itens com 
            # a ordenação geral. Mas como agora haverão ordenações em
            # cada rodada, eles deixaram de ser o geral.
            arrayDfCompOrdenDaRodada = [itemComparacao for itemMedia, itemComparacao, itemCIF, itemNome in array_ordenada_com_medias]
            #Agora vamos garantir que os arrays que dizem respeito à planilha de CIFs seguem a mesma linha
            arrayDfCIFsOrdenDaRodada = [itemCIF for itemMedia, itemComparacao, itemCIF, itemNome in array_ordenada_com_medias]
            arrayDfNomesOrdenDaRodada = [itemNome for itemMedia,itemComparacao,itemCIF,itemNome in array_ordenada_com_medias]
            # Aqui são adicionados os melhores dataframes e itens de 
            # cada array de classificação da rodada aos arrays de 
            # classificação geral
            arrayDfCompOrdenGeral.append(arrayDfCompOrdenDaRodada[0])
            arrayDfCIFsOrdenGeral.append(arrayDfCIFsOrdenDaRodada[0])
            arrayDfNomesOrdenGeral.append(arrayDfNomesOrdenDaRodada[0])
            #print(arrayDfCompOrdenDaRodada[0])
           
            # Essa condicional é necessária pois caso não haja picos 
            # faltantes não haverá uma tabela padrão com linhas e 
            # muito menos a coluna de intensidades para aplicar a 
            # soma e a multiplicação com os valores menorPicoPadrao e 
            # maiorPicoPadrao, respectivamente e ocasionará um erro.

            if arrayDfCompOrdenDaRodada[0].iloc[-1,9] != 0:
                tabelaPadrao=tabelaPadrao[0:0]
                listaComPicosFaltantesSeusAngulosSuasInt=[{'Ângulos': row['Ângulos 2theta do seu padrão'], 'Intensidades': row['Intensidades do seu padrão']} for _, row in arrayDfCompOrdenDaRodada[0].iterrows() if row['Picos Faltantes'] == 'Sim']
                tabelaPadrao = pd.DataFrame(listaComPicosFaltantesSeusAngulosSuasInt)
                #tabelaPadrao['Intensidades'] = (tabelaPadrao['Intensidades'] + menorPicoPadrao) * maiorPicoPadrao
            else:
                variavelControladora=0
            
            # Se a nota final da primeira comparação (A melhor) é igual a zero 
            # ou o número de picos faltantes é igual a zero, pode parar os loops. 
            # Se os dois forem diferentes de zero pode continuar
            
            if arrayDfCompOrdenDaRodada[0].iloc[-1,-1] == 0 or arrayDfCompOrdenDaRodada[0].iloc[-1,9] == 0:
                variavelControladora=0
            else:
                variavelControladora=1
            # É interessante utilizar o arrayDfCIFsOrdenDaRodada para excluir daraframes da arrayDeDataFramesCIFs. 
            # Pega-se o primeiro item da primeira array citada utiliza ela para comparar com todos os Dataframes 
            # (itens) da arrayDeDataFramesCIFs e em caso afirmativo de serem iguais, retira esse dataframe da 
            # arrayDeDataFramesCIFs. Fazer essa comparação utilizando o método .equals() da biblioteca Pandas

            # Lembre-se: range(inicio, parada, passo)
            for i in range(0,numeroDeAbas):
                if i < len(arrayDeDataFramesCIFs):
                    if arrayDfCIFsOrdenDaRodada[0].equals(arrayDeDataFramesCIFs[i]) == True:
                    # Esse método remove o item pelo índice, há mais métodos para remoção de itens de arrays
                        arrayDeDataFramesCIFs.pop(i)
                else:
                    pass

            for i in range(0,numeroDeAbas):
                if i < len(arrayNomesCIF):
                    if arrayDfNomesOrdenDaRodada[0] == arrayNomesCIF[i]:
                    # Esse método remove o item pelo índice, há mais métodos para remoção de itens de arrays
                        arrayNomesCIF.pop(i)
                else:
                    pass
                
            numeroDeAbas=len(arrayDeDataFramesCIFs)

            # É necessário limpar as linhas dos dataframes pois caso não seja feito, não haverá a limpeza de 
            # forma automática e se criará um loop infinito
            for i in range(0,numeroDeAbas):
                arrayDataFramesComparacao[i] = arrayDataFramesComparacao[i][0:0]
                arrayDfCompOrdenDaRodada[i] = arrayDfCompOrdenDaRodada[i][0:0]
                arrayDfCIFsOrdenDaRodada[i] = arrayDfCIFsOrdenDaRodada[i][0:0]
                arrayDfNomesOrdenDaRodada[i] = arrayDfNomesOrdenDaRodada[i][0:0]
            #print(arrayDfCIFsOrdenGeral[0])

            # Isso também vale para as arrays, provavelmente. Pela via das dúvidas parece mais seguro limpar 
            # elas também
            arrayMedias.clear()
            array_ordenada_com_medias.clear()
            arrayMedCompCIFNomes.clear()
 
        #print(tabelaPadrao)
        # É aqui onde os atributos recebem valores
        # para utilizar no método mostrarPlot()
        self.arrayAs3melhores=arrayDfCIFsOrdenGeral
        #self.dataFramePadraoNoTodo=dataFramePadraoNoTodo
        self.arrayDfNomesOrden=arrayDfNomesOrdenGeral
        self.arrayDfCompOrden=arrayDfCompOrdenGeral
        self.numeroDeAbas=numeroDeRodadas
        self.numeroDeRodadas=numeroDeRodadas
        self.arrayDfCIFsOrden=arrayDfCIFsOrdenGeral
        self.mostrarResultados()
        # Após o QDialogBox ser fechado, as linhas de comando
        # continuam e colocam o valor padrão dos atributos para
        # não haver problemas
        self.arrayAs3melhores=None
        #self.dataFramePadraoNoTodo=None
        self.arrayDfNomesOrden=None
        self.arrayDfCompOrden=None
        self.numeroDeAbas=None
        self.arrayDfCIFsOrden=None
        self.caminhoCIFs=None
        self.caminhoPadrao=None
        self.verificou1=None
        self.verificou2=None
        self.UtilizouPicos1=None
        self.UtilizouPicos2=None
        self.numeroDeRodadas=None
        self.picosDetectados = None

    # Os métodos a seguir são pop-ups como o de método de erro 
    # (Exceto a calcularDesnivelEntrePicos).
    # Por isso vou me abster de explicar esses comandos de novo
    # com a ressalva de um que vou citar no primeiro método

    def mostrarInicio(self):
        inicio=QMessageBox()
        inicio.setIcon(QMessageBox.Information) #O ícone que aparece dentro do pop-up é de informação
        inicio.setText('A comparação vai começar. Isso normalmente demora alguns segundos, mas pode demorar minutos. Clique em OK para continuar.')
        inicio.setWindowTitle("Processo de comparação iniciada")
        inicio.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
        inicio.exec_()
    
    # Essa função será necessária para otimizar o número de 
    # linhas nos laços condicionais na hora de calcular as 
    # distâncias e o desnível do pico escolhido e ela será 
    # usada na função compararPicos

    def calcularDesnivelEntrePicos(self,intensidadePicoPadrao,notaDistancia,arrayDataFramesComparacao,numeroAba,contador,linhaPico,picoDaVez,intensidadePicoAmostra,distancia):
        desnivel=abs(intensidadePicoPadrao-intensidadePicoAmostra)
        if desnivel <= 0.01:
            notaDesnivel = 1
        elif 0.01 < desnivel <= 0.02:
            notaDesnivel = 0.8
        elif 0.02 < desnivel <= 0.03:
            notaDesnivel = 0.6
        elif 0.03 < desnivel <= 0.04:
            notaDesnivel = 0.4
        elif 0.04 < desnivel <= 0.05:
            notaDesnivel = 0.2
        elif 0.05 < desnivel <= 0.1:
            notaDesnivel = 0
        elif 0.1 < desnivel <= 0.2:
            notaDesnivel = -0.2
        elif 0.2 < desnivel <= 0.3:
            notaDesnivel = -0.4
        elif 0.3 < desnivel <= 0.4:
            notaDesnivel = -0.6
        elif 0.4 < desnivel <= 0.5:
            notaDesnivel = -0.8
        elif desnivel > 0.5:
            notaDesnivel = -1
        nota = (notaDistancia+notaDesnivel)/2
        if 0.8 < nota <= 1:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,picoDaVez,intensidadePicoAmostra,distancia,desnivel,'Sim','Muito boa','Não','Não',nota]
            return 5
        elif 0.6 < nota <= 0.8:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,picoDaVez,intensidadePicoAmostra,distancia,desnivel,'Sim','Boa','Não','Não',nota]
            return 4
        elif 0.4 < nota <= 0.6:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,picoDaVez,intensidadePicoAmostra,distancia,desnivel,'Sim','Média','Não','Não',nota]
            return 3
        elif 0.2 < nota <= 0.4:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,picoDaVez,intensidadePicoAmostra,distancia,desnivel,'Sim','Ruim','Não','Não',nota]
            return 2
        elif nota <= 0.2:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,intensidadePicoPadrao,picoDaVez,intensidadePicoAmostra,distancia,desnivel,'Sim','Muito ruim','Não','Não',nota]
            return 1

    #Esse método é acionado no fim do método compararPicos em que mostra um gráfico com os três melhores CIFs
    def mostrarResultados(self):
        #Aqui, o atributo antes criado armazena o pop-up do QDialog
        self.dialogo=QDialog()
        self.dialogo.setWindowTitle("Comparação concluída")
        #self.dialogo.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        #self.dialogo.setFixedSize(650,100)
        self.dialogo.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
        #E cria-se um layout para esse pop-up
        layout=QVBoxLayout()
        #Então uma label com o seguinte texto
        texto=QLabel("Comparação concluída. Resultados disponíveis para salvamento:")
        # Adiciona-se esse texto ao layout do Pop-up
        layout.addWidget(texto)
        # Cria-se uma caixa para botões do QDialog
        caixaBotoes=QDialogButtonBox()
        # Com um botão para criar o gráfico
        botaoMostrarGrafico = QPushButton("Mostrar Gráfico")
        # Um botão para salvar as planilhas de CIFs
        botaoSalvarPlanilhaCIF = QPushButton("Salvar planilha de CIFs")
        # Um botão para salvar as planilhas de comparação
        botaoSalvarPlanilhaComp = QPushButton("Salvar planinhas de comparação")
        # Adicionam-se os botões à caixa
        caixaBotoes.addButton(botaoMostrarGrafico, QDialogButtonBox.ActionRole)
        caixaBotoes.addButton(botaoSalvarPlanilhaCIF, QDialogButtonBox.ActionRole)
        caixaBotoes.addButton(botaoSalvarPlanilhaComp, QDialogButtonBox.ActionRole)
        # e então adiciona-se a caixa ao layout
        layout.addWidget(caixaBotoes)
        # e então de fato seta esse diálogo para o Pop-up       
        self.dialogo.setLayout(layout)
        #Aqui cria-se uma variável para alterar a fonte desse pop-up para o tamanho 11
        fonte = QtGui.QFont()
        fonte.setPointSize(11)
        self.dialogo.setFont(fonte)
        botaoMostrarGrafico.clicked.connect(self.iniciarJanelaResultados)
        botaoSalvarPlanilhaCIF.clicked.connect(self.popUpPlanilhaCIF)
        botaoSalvarPlanilhaComp.clicked.connect(self.popUpPlanilhaComparacao)
        # Vou colocar essa variável para iniciar um evento de loop
        # e encerrar a execução de código como estivesse o .exec()
        # sem a parte ruim de tornar o QDialog em primeiro plano
        # e sem permitir que as outras janelas sejam executadas
        loop = QEventLoop()
        #A utilização do método .open() ao invés do método .exec()
        # para permitir que o pop-up fique em segundo plano
        self.dialogo.open()
        #Iniciar o evento de loop, impedindo o código de continuar
        loop.exec_()
    # Método para mostrar o gráfico que é engatilhado
    def iniciarJanelaResultados(self):
        # Criação do objeto da classe 
        # Ui_MainWindow_graficoResultados
        self.uiGraficoResultados = Ui_MainWindow_graficoResultados()
        # Criação do objeto da classe pai
        self.window = QtWidgets.QMainWindow()
        # Utilização do método da classe citada anterior e 
        # utilização do objeto da classe pai como parâmetro
        self.uiGraficoResultados.setupUi(self.window)
        self.window.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
        # Mostrar a janela
        self.window.show()
        # Variável para referenciar o layout do container frame do gráfico
        self.layout = self.uiGraficoResultados.gridLayout_Grafico
        # Agora é um objeto da FigureCanvas que vai criar o 
        # gráfico. É importante inicializar esse atributo aqui 
        # junto ao método da criação de objeto da segunda janela 
        # para garantir que não haja problemas com o fechar da 
        # janela (O que indica a destruição desse atributo)
        self.canvas = FigureCanvas(Figure(figsize=(5,4)))
        # Criando esse objeto para aparecer a toolbar que estava 
        # presente quando se usava o plt.show()

        self.ax = self.canvas.figure.add_subplot(111)

        # A observação da primeira inicialização aqui vale 
        # para o 
        # atributo toolbar também
        self.toolbar = NavigationToolBar(self.canvas, self)
        # Criação da array de checkBoxes para posterior 
        # manipulação
        self.listaCheckBoxes=[]

        for i in range(self.numeroDeRodadas):
            # a variável i é usada como parâmetro para distinção 
            # dos nomes dos objetos sem uso de um dict e o return 
            # do objeto permite que o mesmo seja adicionado como 
            # um item na array listaCheckBoxes
            self.listaCheckBoxes.append(self.criarEmostrarCheckBoxes(i))

        self.mostrarGrafico()
        
        #for i in range(self.numeroDeRodadas):
    
        #print(self.listaCheckBoxes)

        # Antigamente havia o problema de não conseguir a plena
        # instalação dinâmica dos checkBoxes, sendo que os mesmos 
        # eram criados dentro do laço de repetição propiamente 
        # dito. Depois percebeu-se que fora do laço for a 
        # instalação dos checkBoxes era bem sucedida. Assim 
        # constatou-se que o problema estava sendo a maneira como 
        # era usado o laço for. Pois mesmo utilizando o mesmo 
        # nome do checkBox previamente instalado para referência
        # (checkBox), um segundo checkBox foi criado (Quando
        # isolado). A solução foi: fazer um método que cria os 
        # checkBoxes e utilizar o laço for para repetir o método 
        # em si e não a ação como estava tentando ser feito antes

    def criarEmostrarCheckBoxes(self, numeroDoCheckBox):
        # Esse método cria checkboxes e os adiciona ao layout do container frame designado
        
        # Aqui cria-se o objeto enquanto referencia a classe
        # uiGraficosResultados (Muito importante) e referencia 
        # sua criação ao containerFrameDosCheckBoxes que também 
        # referencia à classe anteriormente citada
        self.uiGraficoResultados.checkBox = QtWidgets.QCheckBox(self.uiGraficoResultados.containerFrameDosCheckBoxes)
        # Aqui coloca-se o nome do objeto e aqui também é 
        # utilizado o parâmetro numeroDoCheckbOX requisitado 
        # pelo método justamente para haver distinção no nome 
        # dos objetos
        self.uiGraficoResultados.checkBox.setObjectName(f'Check_Box{numeroDoCheckBox}')
        # Colocando o texto que aparecerá ao usuário
        self.uiGraficoResultados.checkBox.setText(f'{numeroDoCheckBox+1}° rodada')
        #self.uiGraficoResultados.checkBox.setText(f'Check_Box{numeroDoCheckBox}')
        
        # Caso um checkBox tenha seu estado alterado, atualizar o # gráfico analisando se cada checkBox está checkado ou não
        self.uiGraficoResultados.checkBox.stateChanged.connect(self.prepararParaMostrarNoGrafico)

        # Adicionando esse checkBox ao lauyout vertical para 
        # eles serem se organizar de maneira responsiva no código
        self.uiGraficoResultados.verticalLayout_CheckBoxes.addWidget(self.uiGraficoResultados.checkBox)
        # Ele retorna o objeto
        return self.uiGraficoResultados.checkBox

    def prepararParaMostrarNoGrafico(self):
        for container in list(self.ax.containers):
            try:
                container.remove()
            except (ValueError, AttributeError):
                pass  # Ignorar erros ao tentar remover
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()
        self.mostrarGrafico()

    def mostrarGrafico(self):
        dataFramePicos = self.picosDetectados
        """# Esse comando hasattr serve para ver se o objeto (self) 
        # (Creio que da classe da primeira janela, mesmo que o 
        # atributo canvas seja adicionado ao layout da segunda 
        # janela) tem um atributo chamado canvas
        if hasattr(self, 'canvas'):
            # Se sim, primeiro remove esse atributo do layout
            self.layout.removeWidget(self.canvas)
            # Caso não seja vazio
            if self.canvas is not None:
                #Comando para destruir esse atributo da memória após o fim do evento
                self.canvas.deleteLater()
            # Tornar o atributo vazio
            self.canvas = None

        if hasattr(self, 'toolbar'):
            self.layout.removeWidget(self.toolbar)
            if self.toolbar is not None:
                self.toolbar.deleteLater()
            self.toolbar = None"""

        if hasattr(self, 'canvas'):
            pass
        else:
            self.canvas = FigureCanvas(Figure(figsize=(5,4)))
            self.ax = self.canvas.figure.add_subplot(111)

        for line in self.ax.lines:
            line.remove()

        for collection in self.ax.collections:
            collection.remove()
        
        for patch in self.ax.patches:
            patch.remove()

        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()
        

        
        # Pega-se o maior valor de intensidade do padrão também
        maiorValor=self.intensidades.max()
        # Divide todas as intensidades pela maior
        intensidadesPadraoNormalizadasPara1=(self.intensidades)/maiorValor
        # Pega-se o menor valor de intensidade normalizada
        menorValor = intensidadesPadraoNormalizadasPara1.min()
        # E subtrai todas as intensidades pelo mesmo para fazer um 
        # modesto 'subtract background'
        intensidadesPadraoNormalizadasPara1SemBackground = intensidadesPadraoNormalizadasPara1 - menorValor
        # Array para colocar os dataframes dos cifs com 
        # intensidades normalizadas
        arrayParaAsnovasIntensidadesCIF=[]

        # Agora para o dataFramePicos

        """maiorValorPico = dataFramePicos['Intensidades'].max()
        intensidadesPicoNormalizadaPara1=(dataFramePicos['Intensidades'])/maiorValorPico
        menorValorPico = intensidadesPicoNormalizadaPara1.min()
        intensidadesPicoNormalizadaPara1SemBackground = intensidadesPicoNormalizadaPara1 - menorValorPico"""

        # Existe uma desnível entre as intensidades dos picos e do padrão, vou tentar corrigir esse desnível

        # se valorDadoArray é igual valorDadoDeOutraArray
        #   pegar o index desse dadoDeOutraArray

        angulosPico = dataFramePicos.Ângulos.values
        #print(self.angulos)
        #print(angulosPico)
        """quantidadeAngulosPico = len(angulosPico)
        quantidadeAngulosPadrao = len(self.angulos)"""
        arrayIndexes = []

        for i, anguloAtual in enumerate(self.angulos):
            # for indice, valor in enumerate(nparray):
            # Onde enumerate é um comando que gera uma tupla do
            # índice do valor e o valor em si para iterar sobre 
            # cada valor da nparray self.angulos
            for j, anguloPicoAtual in enumerate(angulosPico):
                if np.isclose(anguloAtual, anguloPicoAtual, atol=1e-5):
                # Comparação de valores float com tolerãncia de 
                # 10^-5 (atol=1e-5)
                    arrayIndexes.append(i)

        """for anguloAtual in self.angulos:
            indices = np.where(np.isclose(anguloAtual, angulosPico))[0]
            if indices.size > 0:
                arrayIndexes.extend(indices.tolist())"""

        """for i in range(quantidadeAngulosPadrao):
            anguloAtual = self.angulos[i]
            for j in range(quantidadeAngulosPico):
                anguloPicoAtual = angulosPico[j]
                indice = np.where(anguloAtual == anguloPicoAtual)[0]
                if indice.size > 0:
                    indexAtual = indice[0]
                    arrayIndexes.append(indexAtual)"""

    

        #print(len(angulosPico))
        #print(len(arrayIndexes))

        #print(arrayIndexes)




        #print(intensidadesPadraoNormalizadasPara1SemBackground)
        #print(intensidadesPicoNormalizadaPara1SemBackground)

        # Aqui ocorre o mesmo processo que ocorreu com as 
        # intensidades do padrão de difração
        for i in range(self.numeroDeRodadas):
            dataFrameDaVez=self.arrayAs3melhores[i]
            #print(dataFrameDaVez)
            intensidadesCIF=dataFrameDaVez.Intensidade.values
            #print(intensidadesCIF)
            maiorValor2=intensidadesCIF.max()
            intensidadesCIFNormalizadasPara1=intensidadesCIF/maiorValor2
            #print(intensidadesCIFNormalizadasPara1)
            arrayParaAsnovasIntensidadesCIF.append(intensidadesCIFNormalizadasPara1)
            #print(self.arrayParaAsnovasIntensidadesCIF[i])

        # Novamente inicializa-se os atributos anteriormente 
        # destruídos a fim de haver uma atualização do gráfico

        #self.canvas = FigureCanvas(Figure(figsize=(5,4)))

        # O canvas é basicamente um quadro

        # O gráfico em si é feito pelo ax (axes - eixos)

        # O add_subplot permite isso com parâmetros numéricos que 
        # não vou entrar em detalhes

        #self.ax = self.canvas.figure.add_subplot(111)

        cores = list(mcolors.TABLEAU_COLORS.keys())

        #cores = [cor for cor in cores if cor not in ['blue', 'red', 'white']]

        # Faz o plot do padrão
        self.ax.plot(self.angulos,intensidadesPadraoNormalizadasPara1SemBackground, label='Dados', color='blue')

        self.ax.scatter(self.angulos[arrayIndexes], intensidadesPadraoNormalizadasPara1SemBackground[arrayIndexes], label='Picos', color='red')

        for i in range(self.numeroDeRodadas):
            # Então faça um gráfico de barras para cada CIF tendo 
            # como label sua colocação e seu nome,
            # como largura tem-se 0.1 pixels
            
            # Se um dos checkboxes da array estiver marcado 
            if self.listaCheckBoxes[i].isChecked() == True:
                
                # Faça o plot em barras das reflexões desse cif 
                # em específico
                self.ax.bar(self.arrayAs3melhores[i].iloc[:,0],arrayParaAsnovasIntensidadesCIF[i],label=f'{i+1}° rodada: {self.arrayDfNomesOrden[i]}', width=0.1, color=cores[i % len(cores)])
            else:
                pass
        # Colocando título e labels dos eixos com seus 
        # respectivos tamanhos de fonte
        self.ax.set_xlabel("2θ (°)", fontsize=14)
        self.ax.set_ylabel("Intensidade (u.a.)", fontsize=14)
        self.ax.set_title("Melhor CIF de cada rodada", fontsize=15)
        # Importante lembrar desse comando abaixo caso queira que 
        # sua label apareça corretamente
        self.ax.legend()

        self.canvas.draw()

        # Novamente inicialização para atualização do gráfico # no 
        # todo

        #self.toolbar = NavigationToolBar(self.canvas, self)

        if not hasattr(self, 'toolbar'):
            self.toolbar = NavigationToolBar(self.canvas, self)

        # Adicionando o gráfico e a toolbar ao layout
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        
    # Esse método é para escolha de um diretório para salvar
    # os arquivos que foram criados seja com o compararPicos no
    # contexto do de comparar com todos picos
    # ou com alguns picos e para salvamento de ângulos.
    # Funciona como o método de salvar planilha de ângulos
    # na aba de detectar picos. Isso vale para os outros 
    # métodos à frente também
    def popUpPlanilhaCIF(self):
        nomeArquivo=None
        opcoes=QFileDialog.Options()
        filtroDeArquivo = "Excel Files (*.xlsx);;All Files (*)"
        nomeArquivo, _ = QFileDialog.getSaveFileName(self.dialogo, "Salvar planilha dos CIFs", "", filtroDeArquivo, options=opcoes)
        if nomeArquivo:
            if not nomeArquivo.endswith('.xlsx'):
                    nomeArquivo += '.xlsx'
            self.salvarPlanilhaCIF(nomeArquivo)
        else:
            self.mostrarPopUpNaoSalvouArquivo()
        self.dialogo.raise_()
        self.dialogo.activateWindow()

    def popUpPlanilhaComparacao(self):
        nomeArquivo=None
        opcoes=QFileDialog.Options()
        filtroDeArquivo = "Excel Files (*.xlsx);;All Files (*)"
        nomeArquivo, _ = QFileDialog.getSaveFileName(self.dialogo, "Salvar planilhas de comparação", "", filtroDeArquivo, options=opcoes)
        if nomeArquivo:
            if not nomeArquivo.endswith('.xlsx'):
                    nomeArquivo += '.xlsx'
            self.salvarPlanilhaComparacao(nomeArquivo)
        else:
            self.mostrarPopUpNaoSalvouArquivo()
        self.dialogo.raise_()
        self.dialogo.activateWindow()

    def salvarPlanilhaCIF(self,parametroNomeArquivo):
        nomeArquivo=parametroNomeArquivo
        #print(f'Tamanho da array self.arrayDfCIFsOrden: {len(self.arrayDfCIFsOrden)}')
        with pd.ExcelWriter(nomeArquivo) as writer2:
            for numeroAba in range(self.numeroDeAbas):
                #print(f'numeroAba={numeroAba}')

                # Aqui há uma correção no space group symbol 
                # presente no nome de cada aba para garantir que 
                # não há caracteres inválidos pelo excel
                self.arrayDfNomesOrden[numeroAba]=self.corrigirSheetNames(self.arrayDfNomesOrden[numeroAba])
                #print(self.arrayDfNomesOrden[numeroAba])
                self.arrayDfCIFsOrden[numeroAba].to_excel(writer2,sheet_name=self.arrayDfNomesOrden[numeroAba],index=False)

    def salvarPlanilhaComparacao(self,parametroNomeArquivo):
        nomeArquivo=parametroNomeArquivo
        #print(f'Tamanho da array self.arrayDfCompOrden: {len(self.arrayDfCompOrden)}')
        with pd.ExcelWriter(nomeArquivo) as writer1: #Cria-se um objeto para a planilha saída
        
        #Basicamente, ao fim das análises, os DataFrames criados são alojados na array de DataFrames e
        #cada dataFrame é endereçado a sua aba, garanta que cada aba tenha o nome correto da amostra que foi
        #comparada
            for numeroAba in range(self.numeroDeAbas): #Aqui esse for é para garantir que diferentes dataFrames estão sendo
                                        #sendo adicionados em abas diferentes à planilha saída
                #print(f'numeroAba={numeroAba}')
                #print(f'DATAFRAME N {numeroAba}')
                #print(self.arrayDfCompOrden[numeroAba])

                # Mesma ressalva feita no método anterior é 
                # válida aqui
                self.arrayDfNomesOrden[numeroAba]=self.corrigirSheetNames(self.arrayDfNomesOrden[numeroAba])
                self.arrayDfCompOrden[numeroAba].to_excel(writer1,sheet_name=self.arrayDfNomesOrden[numeroAba],index=False)

    # Método de correção do nome das abas da planilha
    def corrigirSheetNames(self, parametroNomeSheet):
        nomeSheet=parametroNomeSheet
        # Array de caracteres inválidos
        chars_invalidos = ['\\', '/', '*', '[', ']', ':', '?', "'", '"', '<', '>', '|']
        # Laço de repetição analisando cada caractere do 
        # nomeSheet comparando com os caracteres inválidos
        for char in chars_invalidos:
            # Onde caso ocorra presença de algum caractere do   
            # tipo inválido deve haver reposição pelo caractere _
            nomeSheet=nomeSheet.replace(char, '_')
        # Verificando se o número de caracteres excede 31
        if len(nomeSheet) > 31:
            # Se sim, restringir aos 31 caracteres
            nomeSheet = nomeSheet[:31]
        # O método strip() garante que não haja espaços vazios (Eu acho)
        return nomeSheet.strip()

    #
    # }
    #

    #
    # MÉTODOS DA ABA COMPARAR POUCOS PICOS {
    #

    # Aqui a ideia é parecida com os métodos de busca de diretório
    # da aba comparar picos mas existe certas mudanças
    def abrirDirEventSeuPadraoAdicionarPicos(self):
        # Vou inicializar esse atributo aqui para não ter problemas no futuro
        self.tabelaPadrao = None
        self.arrayPicos=[None,None,None,None,None]
        self.diretorioPadrao2=None
        opcoes = QFileDialog.Options()
        filtroDeArquivo = "Arquivos de texto (*.txt);;Todos os arquivos (*)"
        tituloPopUp='Selecionar o arquivo do seu padrão de difração'
        diretorioPadrao, _ = QFileDialog.getOpenFileName(self,tituloPopUp,'', filtroDeArquivo,options=opcoes)
        self.diretorioPadrao2=diretorioPadrao
        #Se diretorioPadrao tem um caminho
        if diretorioPadrao:
            #Variaveis que vão receber e adicionar os caminhos em string para utilizar mais na frente
            #caminhoPadrao=diretorioPadrao
            #Arquivo que vai guardar o caminho do arquivo .xlsx
            #buscaTabelaPadrao = os.path.join(caminhoPadrao,'*.txt')
            #Array que vai guardar os caminhos dos arquivos .xlsx
            #ArrayCaminhoTabelaPadrao = glob.glob(buscaTabelaPadrao)
            #ArrayCaminhoTabelaPadrao=diretorioPadrao
            # Se a array não está vazia
            #if ArrayCaminhoTabelaPadrao:
            #Só se o caminho houver pelo menos uma pasta,
            #ou seja, ArrayCaminhoPlanilhaPadrao != None,
            #será adiconado caminho à caixa de texto editável
            self.caminhoPadraotextEdit_2.setText(diretorioPadrao)
            #Aqui entra aquele atributo do ultimoIndex
            #Caso haja algo guardado nela, indica que já existem
            #itens nos comboBoxes, portando o método é utilizado
            #para remover esses itens e ter ideia do ultimoIndex
            #é importante para determinar o limite do laço de
            #repetição
            if self.ultimoIndex:
                self.removerItens()
            #Coleta-se o único item dessa array criada na linha anterior
            #caminhoPadrao=ArrayCaminhoTabelaPadrao[0]
            self.tabelaPadrao = pd.read_csv(diretorioPadrao,delim_whitespace=True,names=["Ângulos","Intensidades"],header=None)# data-
            # rame criado para armazenar os ângulos do
            # arquivo de texto encontrado (Alguns lugares pode estar
            # planilhas mas essa funcionalidade foi alterada a fim de 
            # trabalhar com os arquivos mais comuns para leitura de dados,
            # deixou-se de trabalhar com .xlsx e sim com .txt para entrada
            # de dados)
            
            #
            # TESTE
            #

            #print(self.tabelaPadrao)

            #Armazenar o número de linhas ao todo
            numeroLinhasPadrao=self.tabelaPadrao.iloc[:,0].count()
            for numeroLinha in range(numeroLinhasPadrao):
                #Ver qual o ângulo de 0 até numeroLinhasPadrao
                pico=self.tabelaPadrao.iloc[numeroLinha,0]
                #Adiciona a string do ângulo ao comboBox
                self.comboBoxPico1.addItem(str(pico))
                #Adiciona a informação relacionada
                # ao string deesse dado item, 
                # tem que ser +1 pois já exiiste o item 0 
                # que é o Vazio
                self.comboBoxPico1.setItemData(numeroLinha+1,pico)
            for numeroLinha in range(numeroLinhasPadrao):
                pico=self.tabelaPadrao.iloc[numeroLinha,0]
                self.comboBoxPico2.addItem(str(pico))
                self.comboBoxPico2.setItemData(numeroLinha+1,pico)
            for numeroLinha in range(numeroLinhasPadrao):
                pico=self.tabelaPadrao.iloc[numeroLinha,0]
                self.comboBoxPico3.addItem(str(pico))
                self.comboBoxPico3.setItemData(numeroLinha+1,pico)
            for numeroLinha in range(numeroLinhasPadrao):
                pico=self.tabelaPadrao.iloc[numeroLinha,0]
                self.comboBoxPico4.addItem(str(pico))
                self.comboBoxPico4.setItemData(numeroLinha+1,pico)
            for numeroLinha in range(numeroLinhasPadrao):
                pico=self.tabelaPadrao.iloc[numeroLinha,0]
                self.comboBoxPico5.addItem(str(pico))
                self.comboBoxPico5.setItemData(numeroLinha+1,pico)
            #Aqui é onde de fato o atributo self.ultimoIndex deixa de ser None
            self.ultimoIndex=self.comboBoxPico1.count()-1
            self.UtilizouPicos2=False
        #Se o atributo de caminhos está vazio                 
        else:
            self.caminhoPadraotextEdit_2.setText('O caminho aparecerá aqui quando selecionado')
            if self.ultimoIndex:
                self.removerItens()
    #Esse aqui é basicamente para fazer o mesmo que o próximo método, não repetir
    #um monte de linhas, a explicação vou fazer no método
    def removerItens(self):
        #Aqui é utilizado um laço de repetição que 
        #começa no atributo ultimoIndex (Caso ele
        #esteja com algum valor diferente de None)
        #e é para terminar no 0 e decresce 1
        #unidade a cada repetição. Fazer a remoção 
        #dos itens começando do último para o pri-
        # meiro se deve ao fato de que caso 
        # seja feito o do primeiro para o últi-
        # mo, constantemente o tamanho das comboBoxes esta-
        # rão sendo trocados. No fim, só vai sobrar o valor 
        # Vazio nesse caso
        for i in range(self.ultimoIndex,0,-1):
            self.comboBoxPico1.removeItem(i)
        for i in range(self.ultimoIndex,0,-1):
            self.comboBoxPico2.removeItem(i)
        for i in range(self.ultimoIndex,0,-1):
            self.comboBoxPico3.removeItem(i)
        for i in range(self.ultimoIndex,0,-1):
            self.comboBoxPico4.removeItem(i)
        for i in range(self.ultimoIndex,0,-1):
            self.comboBoxPico5.removeItem(i)
        self.emitirSinaisComboBoxPicos()
    # A explicação dessas linhas de comando e a necessidade do método já foram explicados
    def emitirSinaisComboBoxPicos(self):
            self.comboBoxPico1.setCurrentIndex(0)
            self.comboBoxPico1.activated.emit(0)
            self.comboBoxPico2.setCurrentIndex(0)
            self.comboBoxPico2.activated.emit(0)
            self.comboBoxPico3.setCurrentIndex(0)
            self.comboBoxPico3.activated.emit(0)
            self.comboBoxPico4.setCurrentIndex(0)
            self.comboBoxPico4.activated.emit(0)
            self.comboBoxPico5.setCurrentIndex(0)
            self.comboBoxPico5.activated.emit(0)
    def utilizarPicosDetectados2(self, nomeAtributo):
        # Vou inicializar esse atributo aqui para não ter problemas no futuro
        self.tabelaPadrao = None
        horario = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        dataFramePicos = None
        nomeAtributo = nomeAtributo
        if nomeAtributo == 'pushButtonUtilizarPicos':
            dataFramePicos = self.dataFramePicos
        if nomeAtributo == 'pushButton_UtilizarPicosCaerus':
            dataFramePicos = self.dataFramePicosCR
        quantidadePicos=len(dataFramePicos)
        if nomeAtributo == "pushButtonUtilizarPicos":
            self.caminhoPadraotextEdit_2.setText(f'Utilizando os {quantidadePicos} picos encontrados a partir dos métodos peak-detect ou topology às {horario}')
        if nomeAtributo == "pushButton_UtilizarPicosCaerus":
            self.caminhoPadraotextEdit_2.setText(f'Utilizando os {quantidadePicos} picos encontrados a partir do método caerus às {horario}')
        dataFrameAngulos2=pd.DataFrame({'Ângulos': dataFramePicos['Ângulo'], 'Intensidades': dataFramePicos['Intensidade']})
        if self.ultimoIndex:
            self.removerItens()
        self.tabelaPadrao=dataFrameAngulos2
        if nomeAtributo == "pushButtonUtilizarPicos":
            self.windowSR.close()
        if nomeAtributo == "pushButton_UtilizarPicosCaerus":
            self.windowCR.close()
        
        # data-
        # rame criado para armazenar os ângulos do
        # arquivo de texto encontrado (Alguns lugares pode estar
        # planilhas mas essa funcionalidade foi alterada a fim de 
        # trabalhar com os arquivos mais comuns para leitura de dados,
        # deixou-se de trabalhar com .xlsx e sim com .txt para entrada
        # de dados)
        
        #
        # TESTE
        #

        #print(tabelaPadrao)

        #Armazenar o número de linhas ao todo
        numeroLinhasPadrao=self.tabelaPadrao.iloc[:,0].count()
        for numeroLinha in range(numeroLinhasPadrao):
            #Ver qual o ângulo de 0 até numeroLinhasPadrao
            pico=self.tabelaPadrao.iloc[numeroLinha,0]
            #Adiciona a string do ângulo ao comboBox
            self.comboBoxPico1.addItem(str(pico))
            #Adiciona a informação relacionada
            # ao string deesse dado item, 
            # tem que ser +1 pois já exiiste o item 0 
            # que é o Vazio
            self.comboBoxPico1.setItemData(numeroLinha+1,pico)
        for numeroLinha in range(numeroLinhasPadrao):
            pico=self.tabelaPadrao.iloc[numeroLinha,0]
            self.comboBoxPico2.addItem(str(pico))
            self.comboBoxPico2.setItemData(numeroLinha+1,pico)
        for numeroLinha in range(numeroLinhasPadrao):
            pico=self.tabelaPadrao.iloc[numeroLinha,0]
            self.comboBoxPico3.addItem(str(pico))
            self.comboBoxPico3.setItemData(numeroLinha+1,pico)
        for numeroLinha in range(numeroLinhasPadrao):
            pico=self.tabelaPadrao.iloc[numeroLinha,0]
            self.comboBoxPico4.addItem(str(pico))
            self.comboBoxPico4.setItemData(numeroLinha+1,pico)
        for numeroLinha in range(numeroLinhasPadrao):
            pico=self.tabelaPadrao.iloc[numeroLinha,0]
            self.comboBoxPico5.addItem(str(pico))
            self.comboBoxPico5.setItemData(numeroLinha+1,pico)
        #Aqui é onde de fato o atributo self.ultimoIndex deixa de ser None
        self.ultimoIndex=self.comboBoxPico1.count()-1
        self.UtilizouPicos2=True
    # Se o atributo de caminhos está vazio                 
    # Métodos engatilhados quando o activated é acionado
    # para selecionar os itens em cada comboBox
    def picoSelecionado1(self,index):
        # Caso não haja esses laços condicionais aparecerá 5 erros, 
        # no momento que o programa for iniciado irá aparecer um 
        # mesmo erro 5 vezes, basicamente o erro trata-se de tentar 
        # ler uma array que ainda está setada como None
        if self.intensidades is None:
            pass # Comando para o programa não fazer nada
        else:
            # Mesmo motivo anterior
            if self.tabelaPadrao is None:
                pass
            else:
                pico1=self.comboBoxPico1.itemData(index)
                intensidadePico1=self.tabelaPadrao.iloc[index-1,1]
                self.arrayPicos[0]=[pico1,intensidadePico1]
        #Somente para testes
        #print(self.arrayPicos)
    def picoSelecionado2(self,index):
        if self.intensidades is None:
            pass
        else:
            if self.tabelaPadrao is None:
                pass
            else:
                pico2=self.comboBoxPico2.itemData(index)
                intensidadePico2=self.tabelaPadrao.iloc[index-1,1]
                self.arrayPicos[1]=[pico2,intensidadePico2]
        #print(self.arrayPicos)
    def picoSelecionado3(self,index):
        if self.intensidades is None:
            pass
        else:
            if self.tabelaPadrao is None:
                pass
            else:
                pico3=self.comboBoxPico3.itemData(index)
                intensidadePico3=self.tabelaPadrao.iloc[index-1,1]
                self.arrayPicos[2]=[pico3,intensidadePico3]
        #print(self.arrayPicos)
    def picoSelecionado4(self,index):
        if self.intensidades is None:
            pass
        else:
            if self.tabelaPadrao is None:
                pass
            else:
                pico4=self.comboBoxPico4.itemData(index)
                intensidadePico4=self.tabelaPadrao.iloc[index-1,1]
                self.arrayPicos[3]=[pico4,intensidadePico4]
        #print(self.arrayPicos)  
    def picoSelecionado5(self,index):
        if self.intensidades is None:
            pass
        else:
            if self.tabelaPadrao is None:
                pass
            else:
                pico5=self.comboBoxPico5.itemData(index)
                intensidadePico5=self.tabelaPadrao.iloc[index-1,1]
                self.arrayPicos[4]=[pico5,intensidadePico5]          
            """self.arrayPicosSemNone=[item for item in self.arrayPicos if item is not None]
        print(self.arrayPicosSemNone)"""
        #print(self.arrayPicos)
    # Esse é igualzinho ao método de procura
    # do diretório de CIFs da aba comparar
    # picos
    def abrirDirEventCIFs2(self):
        self.diretorioCIFs2=None
        opcoes = QFileDialog.Options()
        opcoes |= QFileDialog.ShowDirsOnly
        diretorioCIFs = QFileDialog.getExistingDirectory(self,'Selecionar Pasta dos CIFs','',options=opcoes)
        self.diretorioCIFs2=diretorioCIFs
        if diretorioCIFs:
            self.caminhoCIFstextEdit_2.setText(diretorioCIFs)
        else:
            self.caminhoCIFstextEdit_2.setText('O caminho aparecerá aqui quando selecionado')
    # Método ativado quando um item na caixa de radiações
    # é selecionado
    def itemSelecionado2(self,index):
        self.valorSelecionado2=self.caixaRadiacoes_2.itemData(index)
    # Método idêntico ao verificar utilizado na aba comparar picos
    def verificar2(self):
        #Se os dois atributos estão preenchidos simultaneamente
        #(Não são mais vazios)
        if self.diretorioCIFs2 and (self.diretorioPadrao2 or self.UtilizouPicos2==True):
            self.arrayParaDataFrame()
            #Se a trava lógica está desativada
            if self.travaLogica == False:
                self.caminhoCIFs=self.diretorioCIFs2
                self.caminhoPadrao=self.diretorioPadrao2
                # Seta as travas para permitirem a entrada de
                # dados no contexto da tab Comparar Poucos
                # Picos 
                self.verificou2=True
                self.verificou1=False
                #Inicia a comparação
                self.compararPicos()
            else:
                self.verificou2=None
                self.verificou1=None
                raise ValueError("Nenhum pico foi selecionado.")
        #Se não
        else:
            self.verificou2=None
            self.verificou1=None
            #Se esse atributo ainda está vazio
            if not self.diretorioCIFs2:
                #Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("A pasta dos CIFs não foi selecionado.")
            #Se esse atributo ainda está vazio
            if not self.diretorioPadrao2:
                #Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("O arquivo do seu padrão de difração não foi selecionado e os picos detectados não foram utilizados.")
    #Esse método converte uma array para um dataframe
    def arrayParaDataFrame(self):
        #Primeiro, é criado uma array que não tem itens None
        #acho que dá para considerar isso uma compreensão de
        #lista
        self.arraySemNone = [item for item in self.arrayPicos if item is not None]
        #Se array não está vazia
        if self.arraySemNone != []:
            # Use o método set para criar uma array com
            # um conjunto de itens não repetidos e ordenados
            # (Todos os itens são float)
            # Transforme essa array em um dataframe de uma única
            # coluna chamada "Ângulos 2theta (°)"
            self.arraySNoneSRepet = set(tuple(item) if isinstance(item, list) else item for item in self.arraySemNone)
            tuplaOrdenada = sorted(self.arraySNoneSRepet)
            # Note, antes de passar pelo método set, a lista passa 
            # por uma compreensão de gerador em que ele transforma os itens lista em tuplas 
            # caso seja avaliado que o item é uma lista utilizando o método isinstance que 
            # pede como parâmtros o objeto e a classe, caso o objeto (Aqui chamado de item) 
            # seja da classe lista (list) ele retornará true e passará ele como tupla para 
            # poder passar pelo método set que só aceita objetos imutáveis como objetos da 
            # classe tupla, objetos hasháveis
            self.dfPicos=pd.DataFrame(tuplaOrdenada, columns=["Ângulos","Intensidades"])

            # Para fins de teste e avaliação do valor recebido

            #print(self.dfPicos)

            #Não haverá trava lógica para a ação do método comparar picos
            #sendo utilizado no contexto do tab Comparar Poucos Picos
            self.travaLogica=False
        #Caso a array esteja vazia (Todos os comboBox estão com
        #o dado "Vazio" selecionado)
        else:
            #Reinicie o atributo dfPicos para o valor
            #padrão None
            self.dfPicos=None
            #Acione a trava lógica para não haver acionamento
            #do método comparar picos no contexto da tab Comparar
            #Poucos Picos
            self.travaLogica=True
    # A partir daqui o método utilizado também é o compararPicos()
    # que foi colocado na parte da aba de comparar picos

    #
    # }
    #

#Caso o código seja inicializado? Esse arranjo do if (Ainda mais
#por ser considerado um bom comportamento na escrita de códigos python)
# e o operador |= parecem ser conhecimentos importantes de se ter em
#detalhes
if __name__ == "__main__":
    #O erro do sistema vai ser direcionado ao método global (Acho)
    sys.excepthook=capturarExcecao
    #Tente
    try:
        #Variável que aloca a classe que tem como função considerar
        #a configuração do sistema para adequar a janela ao visual
        #comum de uma janela desse sistema.
        app = QApplication(sys.argv)
        window = MainWindow() #window é uma instância (Um objeto) criado a partir do molde (classe)
        #MainWindow
        #Comando de saída do código utilizando o fechamento da janela e o encerramento da janela
        window.show()
        sys.exit(app.exec_())
    #Exceto se
    except Exception as e:
        #Utiliza o método global para mostrar o erro no código
        capturarExcecao(*sys.exc_info())