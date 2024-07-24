#ATENÇÃO
#Em alguns lugares do código, haverá eu dizendo coisas como "Acho, não entrei em detalhes"
#Isso se deve ao fato de que esse código foi feito em auxílio com o ChatGPT, no caso,
#foram pedidos sugestões e ajuda para desenvolver as funcionalidades que estavam além do meu
#raciocínio no momento de concepção do código. No caso, eu me pus a entender o máximo que eu
#achava cabível até para adicionar essas funcionalidades isoladas no código que eu primei-
#ramente escrevi sem auxílio do mesmo. O ponto é que o raciocínio de como o código funciona
#e como sua estrutura se interliga é de meu conhecimento. Até porque a ideia é poder melhorar
#o que já foi construído, então sem ter a base não teria como construir mais andares. O ponto
#é que a utilização do ChatGPT foi na sintaxe da linguagem que muito é de meu desconhecimento
#bem como a sugestão de módulos e a explicação de como usá-los, o que me faz utilizar isso
#como detalhes ao que exatamente quis dizer com "ajuda para desenvolver as funcionalidades"
#que eu disse no começo. 

from interfaceGerada.design import Ui_MainWindow  # Importa a classe gerada pela interface
"""'from pasta.scriptPy import classe' --- interessante"""
#!pip install ipdb Esse ponto de exclamação só funciona no collab para instalação em meio ao código
#import ipdb #Esses comandos foram para importar esse módulo
        #que serviu de ferramenta para estudar erros do código
        #usando debug

import logging #módulo para permitir colocar os erros num arquivo de log

import sys #módulo para controlar o sistema/programa para poder fechar ele, por exemplo (Acho, não entrei em detalhes)

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QMainWindow, QTextEdit, QDialogButtonBox, QDialog, QPushButton, QVBoxLayout, QLabel
"""
Importandoo os widgets do PyQt5 que serão necessários para adicionar elementos que não estão na interface visual gerada em .py
que é importada nesse projeto para se colocar os gatilhos e dar vida à interface visual
"""
from PyQt5.QtGui import QIcon
"""
Aqui é para adicionar ícones às janelas
e pop-ups do programa
"""
from PyQt5 import QtGui
"""
Aqui é para permitir acesso à mudança de fonte
em um pop-up específico da tab Comparar
"""
from PyQt5.QtCore import QEventLoop
# Esse aqui é para importar o evento de loop para
# utilizar com o método open()
from pymatgen.analysis.diffraction.xrd import XRDCalculator #módulo para fazer o padrão de difração dos CIFs selecionados

from pymatgen.io.cif import CifParser #módulo para ler os arquivos CIF e extrair as informações necessárias para fazer
#o padrão de difração

import traceback #módulo para "trazer as linhas de código onde ocorreu um problema" (Não entrei em detalhes)

import pandas as pd #Esse módulo foi utilizada para ter
                    #acesso aos conjuntos de dados bidimen-
                    #sionais conhecidos como DataFrames

import glob #módulo utilizado para criar arrays com os caminhos dos arquivos selecionados

import os #módulo utilizado para criar responsividade e flexibilidade na coleta dos caminhos
#indepente do sistema operacional (Aparentemente, não entrei em muitos detalhes)

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
#importar os gráficos feitos

# Tentar resolver problema dos ícones que não estão aparecendo nas janelas, solução
# retirada de:
# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(caminho_relativo):
    try:
        caminho_base = sys._MEIPASS
    except Exception:
        caminho_base = os.path.abspath(".")

    return os.path.join(caminho_base, caminho_relativo)

#Configuração do arquivo .log de erro
logging.basicConfig(
    #Nome do arquivo
    filename=r'relatorioErros.log',
    level=logging.ERROR, #Nível do aviso do log (Por assim dizer, não entrei em muitos detalhes),
    #como meu caso é erro, pus ERROR

    #Isso eu não entrei em muito detalhes, mas é o formato de como o erro será
    #reportado no arquivo
    format='%(asctime)s - %(levelname)s - %(message)s'
    #Olhando o arquivo de fato é isso, primeiro vem o horário e data em formato asc
    #Depois vem o nível do report
    #E por fim a mensagem sem detalhes que o usuário recebeu do erro
)
#Método para capturar erros de forma global
def capturarExcecao(exctype,value,tb):

    #Essa é a mensagem de erro com detalhes de onde o erro aconteceu no código
    mensagemErro="".join(traceback.format_exception(exctype,value,tb))

    #Esse é o comando para inserir o erro no arquivo .log
    logging.error(mensagemErro)

    #Cria-se uma caixa de erro
    erro=QMessageBox()
    #Coloca-se o ícone da caixa como crítico
    erro.setIcon(QMessageBox.Critical)
    #Insere o texto na caixa de erro
    erro.setText("Ocorreu um erro no aplicativo")
    #E também insere o erro que aconteceu
    erro.setInformativeText(str(value))
    #Esse é o título que aparecerá na caixa,
    #No canto superior esquerdo da caixa
    erro.setWindowTitle("Erro")
    #Comando para adicionar um ícone ao canto superior
    #esquerdo da janela
    erro.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
    #E os detalhes do erro, como onde
    #ocorreu nas linhas de código
    erro.setDetailedText(mensagemErro)
    #Comando para quando fechar a caixa, encerrar o programa
    erro.exec_()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        #Chamando o construtor (Método inicializador)
        #da classe pai no método construtor da classe filha.
        #O uso específico desse comando é no construtor da classe filha
        super().__init__()
        self.setupUi(self)  # Configura a interface definida em Ui_MainWindow

        #Inicialização de diversos atributos que
        #serão utilizados ao longo dos métodos
        #engatilhados ao longo do programa

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
        self.valorLimite = self.doubleSpinBoxMudarLimite.value()
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
        self.dataFramePadraoNoTodo = None
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
        #
        # } 
        #

        #
        # ATRIBUTOS DA ABA COMPARAR POUCOS PICOS {
        #

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
        #
        # }
        #

        #Comando para deixar a janela não redimensionável
        #e com largura 800 pixels e altura 800 pixels
        self.setFixedSize(800,800)
        #Explicado anteriormente
        self.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))

        self.commandLinkButtonAjudaSelecionarXY

        self.caminhoXYtextEdit.setText('O caminho aparecerá aqui quando selecionado')

        self.doubleSpinBoxMudarLimite.setEnabled(False)

        self.pushButtonDetectar.setEnabled(False)

        self.pushButtonExportar.setEnabled(False)
        
        self.informacoesPicostextEdit.setText('Aguardando a detecção dos picos...')



        #Criar um gatilho que envolve clicar esse botão
        #Caso clique no botão, o método abrirDirEventCIFs
        #será chamado e iniciado
        self.botaoSelecCIF.clicked.connect(self.abrirDirEventCIFs)
        #Criação de uma caixa de texto que permite scrollar para 
        #textos maiores
        #self.caminhoCIFsText = QTextEdit(self.tabComparar)
        """#Comando para permitir somente leitura, sem alteração
        #do texto pelo usuário
        self.caminhoCIFsText.setReadOnly(True)
        #Inserir o texto padrão presente nessa caixa de texto
        self.caminhoCIFsText.setText('O caminho aparecerá aqui quando selecionado')
        #Padding cria uma margem interna de 10 px
        self.caminhoCIFsText.setStyleSheet("padding: 10px;")
        #Comando que ajusta a posição x, a posição y, a largura,
        #a altura, respectivamente na caixa de edição de texto
        self.caminhoCIFsText.setGeometry(0,80,800,100)"""
        #Já explicado
        self.botaoSelecPadrao.clicked.connect(self.abrirDirEventSeuPadrao)
        #A utilização de uma caixa de texto é um recurso, do ponto de vista de design,
        #estranho. Mas foi a maneira proposta para garantir que caso um caminho seja
        #muito grande, ele não ultrapasse o tamanho proposto da janela, pois a primeira
        #ideia foi utilizar um QLabel seguido de adjustSize().
        #Já explicados
        #self.caminhoPadraoText = QTextEdit(self.tabComparar)
        """self.caminhoPadraoText.setReadOnly(True)
        self.caminhoPadraoText.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoPadraoText.setStyleSheet('padding: 10px;')
        self.caminhoPadraoText.setGeometry(0,260,800,100)"""
        #Comandos para adicionar os dados dos itens da combo
        #Box de radiação que são os presentes no laço for
        #Nessa array tem floats que foram tirados como padrão
        #do software Diamond e de um arquivo instrumental utilizado
        #no software GSAS EXPGUI, sendo o terceiro a média aritmética
        #dos dois primeiros
        #e as strings pertencem à documentação do
        #pymatgen para radiação característica
        self.itens = [
            1.540598, 1.544426, 1.542512, "CuKa", "CuKa1", "CuKa2", "CuKb1",
            "CoKb1", "CoKa1", "CoKa2", "CoKa",
            "FeKb1", "FeKa1", "FeKa2", "FeKa",
            "CrKb1", "CrKa1", "CrKa2", "CrKa",
            "MoKa", "MoKa1", "MoKa2", "MoKb1",
            "AgKa", "AgKa1", "AgKa2", "AgKb1"
        ]
        #comando simples para adicionar os valores dos
        #itens selecionados
        #A função enumarate permite ter um index
        #associado ao dado do item que foi puxado
        #evidenciando sua posição
        for self.index, self.item in enumerate(self.itens):
            #setItemData insere o dado de um item em dada
            #posição desse item
            self.caixaRadiacoes.setItemData(self.index,self.item)
            self.caixaRadiacoes_2.setItemData(self.index,self.item)
        #gatilho que usa o sinal activated, que basicamente indica
        #se o checkbox está com algum valor selecionado (Isso significa
        #ele estar ativado) e por padrão, ele está. Com isso, ativa uma função
        #que tem como parâmetro index e resgata a partir desse sinal qual valor
        #é equivalente para o index e aloca o dado desse item numa variável
        #para ser usado na função compararPicos(). Creio que seja assim que funciona
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
        #Armando gatilho para o botão ajuda direcionar para a aba ajuda
        #self.commandLinkButtonAjuda.clicked.connect(self.mudarParaAbaAjuda)
        #Esse método que será chamado é para verificar se o usuário colocou
        #os caminhos necessários antes de apertar o botão para fazer a comparação
        self.botaoComparar.clicked.connect(self.verificar)
        #pequeno teste para ver se os itens da
        #comboBox foram corretamente adicionados
        """self.botaoComparar.clicked.connect(self.testeComboBox)
        self.label = QLabel(self.tabComparar)
        self.label.move(200,650)"""
        #self.caminhoArquivoXyText = QTextEdit(self.tabDetectar)
        """self.caminhoArquivoXyText.setReadOnly(True)
        self.caminhoArquivoXyText.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoArquivoXyText.setStyleSheet("padding: 10px;")
        self.caminhoArquivoXyText.setGeometry(0,40,800,100)"""

        self.botaoSelecionarArquivoXy.clicked.connect(self.abrirArquivoEventXy)

        self.pushButtonDetectar.clicked.connect(self.detectarVisualizarPicos)

        self.pushButtonImportar.clicked.connect(self.popUpPlanilhaAngulos)

        self.botaoSelecPadrao_2.clicked.connect(self.abrirDirEventSeuPadraoAdicionarPicos)

        #self.commandLinkButtonAjuda_2.clicked.connect(self.mudarParaAbaAjuda)
        
        #self.caminhoPadraoText_2 = QTextEdit(self.tabCompararPoucosPicos)
        """self.caminhoPadraoText_2.setReadOnly(True)
        self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoPadraoText_2.setStyleSheet("padding: 10px;")
        self.caminhoPadraoText_2.setGeometry(0,80,800,100)"""

        self.comboBoxPico1.activated.connect(self.picoSelecionado1)
        self.comboBoxPico2.activated.connect(self.picoSelecionado2)
        self.comboBoxPico3.activated.connect(self.picoSelecionado3)
        self.comboBoxPico4.activated.connect(self.picoSelecionado4)
        self.comboBoxPico5.activated.connect(self.picoSelecionado5)
        #Esse método foi criado pois as linhas de comando
        #necessárias aqui foram repetidas algumas vezes pelo
        #código
        self.emitirSinaisComboBoxPicos()
        #pequeno teste para ver se os itens da
        #comboBox foram corretamente adicionados
        """self.botaoComparar_2.clicked.connect(self.testeComboBox)
        self.label = QLabel(self.tabCompararPoucosPicos)
        self.label.move(200,650)"""
        self.botaoSelecCIF_2.clicked.connect(self.abrirDirEventCIFs2)

        #self.caminhoCIFsText_2 = QTextEdit(self.tabCompararPoucosPicos)
        """
        self.caminhoCIFsText_2.setReadOnly(True)
        self.caminhoCIFsText_2.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoCIFsText_2.setStyleSheet("padding: 10px;")
        self.caminhoCIFsText_2.setGeometry(0,340,800,100)
        """
        self.botaoComparar_2.clicked.connect(self.verificar2)

        #self.commandLinkButtonAjuda_3.clicked.connect(self.mudarParaAbaAjuda)

        # Adicionando texto e o link para a label de link na tab ajuda
        self.labelLinkRepositorio.setText("<a href=https://github.com/Mirovesaram/comparadorPicos.git>Repositório do comparador de picos</a>")
        # Permitindo que esse link exeterno seja aberto em um navegador quando clicado
        self.labelLinkRepositorio.setOpenExternalLinks(True)
        #Para fins de teste
        #self.botaoComparar_2.clicked.connect(self.arrayParaDataFrame)
        
    #pequeno teste para ver se os itens da
    #comboBox foram corretamente adicionados
    """def testeComboBox(self):
        self.index = self.comboBoxPico1.currentIndex()
        self.data = self.comboBoxPico1.currentData()
        self.text = self.comboBoxPico1.currentText()
        self.label.setText(f"Índice: {self.index}, Dado: {self.data}, Texto: {self.text}")
        self.label.adjustSize()"""
    #
    # MÉTODOS DA ABA AJUDAR {
    #
    def mudarParaAbaAjuda(self):
        self.tabWidget.setCurrentIndex(3)
    #
    # }
    #

    #
    # MÉTODOS DA ABA COMPARAR POUCOS PICOS {
    #

    # Aqui a ideia é parecida com os métodos de busca de diretório
    # da aba comparar picos mas existe certas mudanças
    def abrirDirEventSeuPadraoAdicionarPicos(self):
        self.diretorioPadrao2=None
        opcoes = QFileDialog.Options()
        opcoes |= QFileDialog.ShowDirsOnly
        diretorioPadrao = QFileDialog.getExistingDirectory(self,'Selecionar Pasta do seu Padrão','',options=opcoes)
        self.diretorioPadrao2=diretorioPadrao
        #Se diretorioPadrao tem um caminho
        if diretorioPadrao:
            #Variaveis que vão receber e adicionar os caminhos em string para utilizar mais na frente
            caminhoPadrao=diretorioPadrao
            #Arquivo que vai guardar o caminho do arquivo .xlsx
            buscaTabelaPadrao = os.path.join(caminhoPadrao,'*.txt')
            #Array que vai guardar os caminhos dos arquivos .xlsx
            ArrayCaminhoTabelaPadrao = glob.glob(buscaTabelaPadrao)
            #Se a array não está vazia
            if ArrayCaminhoTabelaPadrao:
                #Só se o caminho houver pelo menos uma pasta,
                #ou seja, ArrayCaminhoPlanilhaPadrao != None,
                #será adiconado caminho à caixa de texto editável
                self.caminhoPadraoText_2.setText(diretorioPadrao)
                #Aqui entra aquele atributo do ultimoIndex
                #Caso haja algo guardado nela, indica que já existem
                #itens nos comboBoxes, portando o método é utilizado
                #para remover esses itens e ter ideia do ultimoIndex
                #é importante para determinar o limite do laço de
                #repetição
                if self.ultimoIndex:
                    self.removerItens()
                #Coleta-se o único item dessa array criada na linha anterior
                caminhoPadrao=ArrayCaminhoTabelaPadrao[0]
                tabelaPadrao = pd.read_csv(caminhoPadrao,delim_whitespace=True,names=["angulos"],header=None)# data-
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
                numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
                for numeroLinha in range(numeroLinhasPadrao):
                    #Ver qual o ângulo de 0 até numeroLinhasPadrao
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    #Adiciona a string do ângulo ao comboBox
                    self.comboBoxPico1.addItem(str(pico))
                    #Adiciona a informação relacionada
                    # ao string deesse dado item, 
                    # tem que ser +1 pois já exiiste o item 0 
                    # que é o Vazio
                    self.comboBoxPico1.setItemData(numeroLinha+1,pico)
                for numeroLinha in range(numeroLinhasPadrao):
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    self.comboBoxPico2.addItem(str(pico))
                    self.comboBoxPico2.setItemData(numeroLinha+1,pico)
                for numeroLinha in range(numeroLinhasPadrao):
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    self.comboBoxPico3.addItem(str(pico))
                    self.comboBoxPico3.setItemData(numeroLinha+1,pico)
                for numeroLinha in range(numeroLinhasPadrao):
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    self.comboBoxPico4.addItem(str(pico))
                    self.comboBoxPico4.setItemData(numeroLinha+1,pico)
                for numeroLinha in range(numeroLinhasPadrao):
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    self.comboBoxPico5.addItem(str(pico))
                    self.comboBoxPico5.setItemData(numeroLinha+1,pico)
                #Aqui é onde de fato o atributo self.ultimoIndex deixa de ser None
                self.ultimoIndex=self.comboBoxPico1.count()-1
            #Se está vazia
            else:
                self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
                if self.ultimoIndex:
                    self.removerItens()
                raise ValueError("A pasta não tem um arquivo .xlsx.")
        #Se o atributo de caminhos está vazio                 
        else:
            self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
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
    #A explicação dessas linhas de comando e a necessidade do método já foram explicados
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
    #Métodos engatilhados quando o activated é acionado
    #para selecionar os itens em cada comboBox
    def picoSelecionado1(self,index):
        pico1=self.comboBoxPico1.itemData(index)
        self.arrayPicos[0]=pico1
        #Somente para testes
        #print(self.arrayPicos)
    def picoSelecionado2(self,index):
        pico2=self.comboBoxPico2.itemData(index)
        self.arrayPicos[1]=pico2
        #print(self.arrayPicos)
    def picoSelecionado3(self,index):
        pico3=self.comboBoxPico3.itemData(index)
        self.arrayPicos[2]=pico3
        #print(self.arrayPicos)
    def picoSelecionado4(self,index):
        pico4=self.comboBoxPico4.itemData(index)
        self.arrayPicos[3]=pico4
        #print(self.arrayPicos)  
    def picoSelecionado5(self,index):
        pico5=self.comboBoxPico5.itemData(index)
        self.arrayPicos[4]=pico5          
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
            self.caminhoCIFsText_2.setText(diretorioCIFs)
        else:
            self.caminhoCIFsText_2.setText('O caminho aparecerá aqui quando selecionado')
    # Método ativado quando um item na caixa de radiações
    # é selecionado
    def itemSelecionado2(self,index):
        self.valorSelecionado2=self.caixaRadiacoes_2.itemData(index)
    # Método idêntico ao verificar utilizado na aba comparar picos
    def verificar2(self):
        #Se os dois atributos estão preenchidos simultaneamente
        #(Não são mais vazios)
        if self.diretorioCIFs2 and self.diretorioPadrao2:
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
                raise ValueError("A pasta dos arquivos do seu padrão de difração não foi selecionado.")
    #Esse método converte uma array para um dataframe
    def arrayParaDataFrame(self):
        #Primeiro, é criado uma array que não tem itens None
        #acho que dá para considerar isso uma compreensão de
        #lista
        self.arraySemNone = [item for item in self.arrayPicos if item is not None]
        #Se array não está vazia
        if self.arraySemNone != []:
            #Use o método set para criar uma array com
            #um conjunto de itens não repetidos e ordenados
            #(Todos os itens são float)
            self.arraySNoneSRepet=set(self.arraySemNone)
            #Transforme essa array em um dataframe de uma única
            #coluna chamada "Ângulos 2theta (°)"
            self.dfPicos=pd.DataFrame(self.arraySNoneSRepet, columns=["Ângulos"])
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

    #
    # MÉTODOS DA ABA DETECTAR PICOS {
    #
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
            self.caminhoArquivoXyText.setText(arquivoXy)
            #Ler o arquivo .xy e forma o dataframe com ângulos e intensidades do padrão
            dataFramePadrao = pd.read_csv(self.arquivoXy, delim_whitespace=True, header=None, names=['x','y'])
            #Pega os ângulos (Dados da coluna 'x') e coloca em uma array
            self.angulos=dataFramePadrao.x.values
            #Pega os ângulos (Dados da coluna 'y') e coloca em uma array
            self.intensidades=dataFramePadrao.y.values
            #Endereça a uma nova array
            self.X = self.intensidades
            #Aqui o atibuto armazena o valor do score padrão 
            # para o método com homologia persistente 
            # do findpeaks
            self.limitePadrao=np.min(np.min(self.X))-1
            #Coloca o valor apresentado no doubleSpin como sendo o
            #valor do score padrão
            self.doubleSpinBoxMudarLimite.setValue(self.limitePadrao)
            #Inicia o método para mostrar o padrão numa label
            #enquanto os dados do padrão estiverem carregados
            self.mostrarLimitePadrao()
        else:
            self.X=None
            self.arquivoXy=None
            self.limitePadrao=None
            self.mostrarLimitePadrao()
            #Coloca o valor como 0
            self.doubleSpinBoxMudarLimite.setValue(0)
            self.valorLimite=None
            self.caminhoArquivoXyText.setText('O caminho aparecerá aqui quando selecionado')
    #Método da label que mostra o limite padrão para aqueles dados
    def mostrarLimitePadrao(self):
        if self.limitePadrao:
            self.labelValorLimite.setText(str(self.limitePadrao))
        else:
            self.labelValorLimite.setText('-')
     #Aqui é o método engatilhado do botão de detectar e visualizar o gráfico
    def detectarVisualizarPicos(self):
        #buscaXyPadrao=os.path.join(caminho,'*.xy')
        #ArrayCaminhoXy=glob.glob(buscaXyPadrao)
        #Se o arquivo está preenchido
        if self.arquivoXy:
            # Tal comando evita que o caso o usuário pressione mais uma vez o
            # botão de mostrar gráfico, o que estava já aberto seja fechado
            plt.close()
            #Armazenar o valorLimite com o valor presente no doubleSpinBox
            self.valorLimite=self.doubleSpinBoxMudarLimite.value()
            #Armazenar o método findpeaks com o limit sendo o valorLimite na variável fp   
            fp = findpeaks(method='topology',limit=self.valorLimite)
            #E armazenar o ajuste desse método para a array X na variável results
            results = fp.fit(self.X)
            #fp.plot()
            # Extrair os indexes dos ângulos dos picos do dataframe criado pelo results.
            # Como pegar a coluna peak do df do results e ver quais tem valor
            # igual a True e utilizar o método .tolist() do numpy para colocar em uma array/lista
            angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
            # Plotando os resultados
            #plt.switch_backend('Qt5Agg')
            # Plot se trata da linha comum, com uma label de Dados para ela e a cor azul
            plt.plot(self.angulos, self.intensidades, label='Dados', color='blue')
            #Scatter se trata de pontos, com uma label de Picos e a cor vermelha. Utiliza os indexes do 
            # angulosPicos para saber quais pontos específicos pegar das arrays angulos e intensidades
            plt.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
            #Setar as labels dos eixos x e y
            plt.xlabel("Ângulo 2theta (°)")
            plt.ylabel("Intensidade (Contagens)")
            #Colocar as labels de fato na figura
            plt.legend()
            # Ter acesso ao gerenciador da imagem
            gerenciador=plt.get_current_fig_manager()
            # Para poder trocar o título da janela gerada no plt.show()
            gerenciador.set_window_title("Picos detectados com o limite "+str(self.valorLimite))
            plt.show()
        #Se não
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
    # Abre um pop-up para escolha do diretório onde irá ser salvo a planilha com ângulos
    def popUpPlanilhaAngulos(self):
        if self.arquivoXy:
            nomeArquivo=None
            opcoes=QFileDialog.Options()
            filtroDeArquivo = "Excel Files (*.xlsx);;All Files (*)"
            nomeArquivo, _ = QFileDialog.getSaveFileName(self, "Salvar planilha com ângulos", "", filtroDeArquivo, options=opcoes)
            if nomeArquivo:
                # Se o o nome do arquivo não terminar com .xlsx
                if not nomeArquivo.endswith('.xlsx'):
                    #Adicione .xlsx
                    nomeArquivo += '.xlsx'
                # Mande o nome do arquivo com o diretório 
                # escolhido para o método que salvará
                # a planilha no diretório escolhido com
                # o nome escolhido
                self.salvarPlanilhaAngulos(nomeArquivo)
            else:
                # Caso o usuário desista de salvar emita um pop-up
                # informando que não foi salvo
                mensagem=QMessageBox()
                mensagem.setIcon(QMessageBox.Information)
                mensagem.setText("A planilha de ângulos não foi salva")
                mensagem.setWindowTitle("Arquivo não foi salvo")
                mensagem.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
                mensagem.exec_()
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
    # O método que vai receber o caminho e salvar no mesmo
    def salvarPlanilhaAngulos(self, parametroArquivo):
        nomeArquivo=parametroArquivo
        self.valorLimite=self.doubleSpinBoxMudarLimite.value()   
        fp = findpeaks(method='topology',limit=self.valorLimite)
        results = fp.fit(self.X)
        angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
        # Transforma em dataframe
        dataFramePicos=pd.DataFrame(self.angulos[angulosPicos], columns=["Ângulos"])
        # Salva com o caminho e nome indicados
        with pd.ExcelWriter(nomeArquivo) as writer:
            dataFramePicos.to_excel(writer,sheet_name="Ângulos encontrados",index=True)
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
        #Essa variável aloca a classe Options, não sei exatamente o que faz (Não entrei em detalhes)
        opcoes = QFileDialog.Options()
        #Não sei que operador é esse, mas essa função também dá a variável inicializada na linha anterior
        #a função de somente mostrar diretórios (pastas), nada de arquivos
        opcoes |= QFileDialog.ShowDirsOnly
        #Esse é o comando da caixinha que apresenta o explorer para o usuário selecionar a pasta
        #bem como essa variável aloca a string obtida (string do caminho da pasta) quando o usuário 
        #seleciona a pasta nessa caixinha criada (Entenda caixinha como a janela que abre do explorer)
        diretorioCIFs = QFileDialog.getExistingDirectory(self,'Selecionar Pasta dos CIFs','',options=opcoes)
        #Atualiza o atributo antigamente inicializado para receber como valor a string do caminho
        #da pasta
        self.diretorioCIFs=diretorioCIFs
        #laço condicional para mudar o texto da caixa de texto antes feita
        #Se diretorioCIFs não está vazio...
        if diretorioCIFs:
            #...mude o texto da caixa de texto para o valor
            #do diretorioCIFs
            self.caminhoCIFsText.setText(diretorioCIFs)
        #Essa segunda linha de código garante que caso o usuário não selecione nada no
        #diálogo de diretórios ele seja informado disso mostrando que não há caminho selecionado
        #Setar None é interessante pois no momento que o diálogo é iniciado, não importa se já
        #tivesse um caminho selecionado, novamente ele voltaria à mensagem padrão imediatamente
        #demonstrando que a informação do caminho já foi sobrescrita
        else:
            self.caminhoCIFsText.setText('O caminho aparecerá aqui quando selecionado')
    #Não vou me estender, basicamente o mesmo do anterior
    def abrirDirEventSeuPadrao(self):
        self.diretorioPadrao=None
        opcoes = QFileDialog.Options()
        opcoes |= QFileDialog.ShowDirsOnly
        diretorioPadrao = QFileDialog.getExistingDirectory(self,'Selecionar Pasta do seu Padrão','',options=opcoes)
        self.diretorioPadrao=diretorioPadrao
        if diretorioPadrao:
            self.caminhoPadraoText.setText(diretorioPadrao)
        else:
            self.caminhoPadraoText.setText('O caminho aparecerá aqui quando selecionado')
    # O método que tinha sido citado anteriormente que age junto ao caixaRadiacoes
    def itemSelecionado(self,index):
        self.valorSelecionado=self.caixaRadiacoes.itemData(index)
    # Método que verifica se os atributos do construtor de diretório dessa aba  
    # deixaram de ser Nones (vazios)
    def verificar(self):
        #Se os dois atributos estão preenchidos simultaneamente
        #(Não são mais vazios)
        if self.diretorioCIFs and self.diretorioPadrao:
            #Atributos que vão receber e adicionar os caminhos em string para utilizar mais na frente
            self.caminhoCIFs=self.diretorioCIFs
            self.caminhoPadrao=self.diretorioPadrao
            #Mudamos a trava para permitir a entrada de dados
            # no contexto da tab Comparar Picos
            self.verificou2=False
            self.verificou1=True
            #Inicia a comparação
            self.compararPicos()
        #Se não
        else:
            self.verificou2=None
            self.verificou1=None
            #Se esse atributo ainda está vazio
            if not self.diretorioCIFs:
                #Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("A pasta dos CIFs não foi selecionado.")
            #Se esse atributo ainda está vazio
            if not self.diretorioPadrao:
                #Avisa para o usuário com um pequeno pop-up que ele não preencheu esse diretório
                raise ValueError("A pasta dos arquivos do seu padrão de difração não foi selecionado.")
    #Método para comparar picos
    def compararPicos(self):
        self.mostrarInicio()
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
        #Arquivo que vai guardar o caminho do arquivo .xy
        buscaXyPadrao = os.path.join(self.caminhoPadrao,'*.xy')
        #Transforma numa array de strings caminho
        ArrayCaminhoXy=glob.glob(buscaXyPadrao)
        #Arquivo que vai guardar o caminho do arquivo .xlsx
        buscaTabelaPadrao = os.path.join(self.caminhoPadrao,'*.txt')
        ArrayCaminhoTabelaPadrao = glob.glob(buscaTabelaPadrao)
        #Coleta-se o único item dessa array criada na linha anterior
        caminhoPadrao=ArrayCaminhoTabelaPadrao[0]
        #DataFrame criado com os dados do arquivo .xy
        dataFramePadraoNoTodo = pd.read_csv(ArrayCaminhoXy[0], delim_whitespace=True,header=None, names=['x','y'])
        #Contagem de linhas para determinar qual é a última linha do padrão
        quantLinhasPadraoNoTodo = dataFramePadraoNoTodo['x'].count()
        ultimaLinha=quantLinhasPadraoNoTodo-1
        #Variável para ter o primeiro ângulo do nosso padrão de difração
        primeiroAnguloPadrao=dataFramePadraoNoTodo.iloc[0,0]
        #Variável para ter o último ângulo do nosso padrão de difração
        UltimoAnguloPadrao=dataFramePadraoNoTodo.iloc[ultimaLinha,0]
        #Se trata do comando para buscar os arquivos CIF no caminho especificado de maneira responsiva
        buscaDosCIFs=os.path.join(self.caminhoCIFs,extensaoArquivo)
        #Array com os caminhos de cada arquivo
        arrayCaminhosCIF=glob.glob(buscaDosCIFs)
        #Quantidade de arquivos e portanto de abas presentes na planilha dos CIFs e de comparação
        numeroDeAbas=len(arrayCaminhosCIF)
        #Array com os nomes dos arquivos feita utilizando uma sacada interessante do chamado "Compreensão de lista"
        #É uma maneira bem simples e rápida de criar uma array
        arrayNomesCIF=[os.path.basename(itemDoCaminhosCIF) for itemDoCaminhosCIF in arrayCaminhosCIF]
        #A partir daqui criamos uma array de DataFrames com ângulo e intensidade de cada CIF que será utilizado para comparar com o padrão de difração
        arrayDeDataFramesCIFs=[]
        for numeroAba in range(numeroDeAbas):
            #Seleciona o caminho do arquivo da lista de caminhos
            arquivoCIF=arrayCaminhosCIF[numeroAba]
            #Variável responsável por armazenar a leitura do arquivo .cif 
            #O nome da variável é em referência ao processo de parsing 
            #(Leitura de um arquivo, explicando de um jeito bem rude)
            parser = CifParser(arquivoCIF, occupancy_tolerance=100)
            #Variável para armazenar a estrutura cristalina do arquivo a partir dessa leitura
            #o [0] se deve ao fato de o parse_structures ser uma lista de estruturas
            #Isso eu já não sei explicar pois não me delonguei muito no módulo
            estrutura = parser.parse_structures(primitive=False)[0]
            #Variável que guarda a configuração do calculador de difração de raio x ou x-ray diffraction (xrd)
            xrdCalculador = XRDCalculator(wavelength=comprimentoOndaAngstron)
            #Variável que guarda o padrão de difração com os valores de ângulo e intendidade do arquivo CIF
            xrdPadrao = xrdCalculador.get_pattern(estrutura)
            #Aqui vamos criar uma variável que vai alocar um valor lógico, verdadeiro ou falso. No caso,
            #se o padrão calculado está dentro do intervalo pensado para o nosso padrão de difração.
            #Ângulo é uma variável temporária

            #essa solução utilizando esse molde -
            #('proposição com variável temporária' for 'variável temporária' in 'Dada array') -
            #está ficando cada vez mais comum e é cada vez mais interessante (Comentário fora de cronologia, desconsidere)
            angulosNoIntervalo=all(primeiroAnguloPadrao <= angulo <= UltimoAnguloPadrao for angulo in xrdPadrao.x)
            #Se verdadeiro
            if angulosNoIntervalo:
                #Variável para alocar o dataFrame recém criado
                df = pd.DataFrame({"Ângulo-2theta": xrdPadrao.x, "Intensidade": xrdPadrao.y})
                #Por fim, esses dados devem ser transpostos em uma array
                arrayDeDataFramesCIFs.append(df)
            else:
                #Aqui ocorre uma filtragem para as únicas linhas que podem estar no dataframe
                #são linhas dentro do intervalo
                df = pd.DataFrame({"Ângulo-2theta": xrdPadrao.x, "Intensidade": xrdPadrao.y})
                linhasFiltradas= df.loc[(df["Ângulo-2theta"]>=primeiroAnguloPadrao) & (df["Ângulo-2theta"]<=UltimoAnguloPadrao)]
                df = linhasFiltradas
                arrayDeDataFramesCIFs.append(df)
        #Criacao da tabela que armazenara as linhas criadas
        dataFrameResultados=pd.DataFrame(columns=['2theta-Padrão','2theta','Intensidade','Diferença','Corresponde','Classificação','Picos Excedentes','Picos Faltantes','Nota'])
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
            tabelaPadrao = pd.read_csv(caminhoPadrao,delim_whitespace=True,header=None,names=["angulos"])
        elif self.verificou2 == True:
            tabelaPadrao = self.dfPicos
        #
        # TESTE
        #

        #print(tabelaPadrao)
        for numeroAba in range(numeroDeAbas):
            #Trazendo o item da lista de dataframes do cif para comparacao
            tabelaAmostra = arrayDeDataFramesCIFs[numeroAba]
            #Criando variável para endereço da linha da amostra que vai ser comparada
            indexLinhaAmostra=0
            #Variável para o número máximo de iterações
            numeroLinhas=tabelaAmostra.iloc[:,0].count() #A função .iloc localiza linhas e colunas pelo seu índice
                                        #numérico que começa no 0, o : é para indicar que todas as linhas devem ser contadas
                                        #e o 0 é para indicar o índice da coluna (Que se espera ser a dos ângulos) a qual deve 
                                        #ser contada todas as linhas que não estão vazias, assim [linha,coluna]
                                        #e a função .count() é responsável pela tarefa de
                                        #contar essas linhas que não estão vazias
        
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
                intensidadePicoAmostra=tabelaAmostra.iloc[indexLinhaAmostra,1] #<--Mudei de 1 para 3 para corresponder a um capricho meu
                #Antes era um capricho, mas após mudanças de fato é bom manter esse índice
                
                #Criando variável para saber quantas linhas há na coluna em questão para servir de quantidade final ao while
                numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
                #Criando variável para o endereço de linha do seu padrão de difração que vai variar no laço while
                indexLinhaPadrao=0
                #Variável que vai guardar o número de rejeições a um dado pico da amostra
                numeroRejeicoes=0
                while indexLinhaPadrao < numeroLinhasPadrao:
                    #Criando variável para selecionar a linha do seu padrão que será comparado com a linha da amostra da vez
                    linhaPico=tabelaPadrao.iloc[indexLinhaPadrao,0]
                    #Criando a variável que vai analisar o quão distante estão os ângulos
                    
                    diferenca=abs(linhaPico-picoDaVez) #A função abs() retorna o valor absoluto de um certo valor, logo mesmo que
                                                    #essa subtração dê um valor negativo, virá o valor absoluto dela
                    if diferenca <= 0.1:
                        muitoBom+=1
                        nota=1
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Muito bom','Não','Não',nota]
                    elif 0.1 < diferenca <= 0.2:
                        bom+=1
                        nota=0.8
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Bom','Não','Não',nota]
                    elif 0.2 < diferenca <= 0.3:
                        medio+=1
                        nota=0.6
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Médio','Não','Não',nota]
                    elif 0.3 < diferenca <= 0.4:
                        poucoBom+=1
                        nota=0.4
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Pouco bom','Não','Não',nota]
                    elif 0.4 < diferenca <= 0.5:
                        menosBom+=1
                        nota=0.2
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Ruim','Não','Não',nota]
                    #Cada loc tem como indície de linha a variável contador que sempre vai somando 1 ao fim de cada linha padrão comparada
                    #com a linha amostra, utilizar o contador como indície de linha no DataFrame é importante pois assim toda vez que um
                    #dos condicionais forem satisfeitos, o índicie utilizado será um indície indisponível no DataFrame o que faz a função
                    #.loc[] adicionar essa linha
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
                        arrayDataFramesComparacao[numeroAba].loc[contador]=['-',picoDaVez,intensidadePicoAmostra,'-','Não','-','Sim','Não',nota]
                    contador+=1
                    indexLinhaPadrao+=1
                indexLinhaAmostra += 1
            #Agora inverte-se a ordem da escolha de picos para poder analisar o quanto de picos faltantes tem:
            #A lógica é: Escolha um pico do padrão, então o compare aos picos do CIF, caso nenhum pico corresponda,
            #isso mostra que que esse pico do padrão falta quando se trata em corresponder aos picos do CIF.
            contador += 1
            indexLinhaPadrao=0
            numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
            while indexLinhaPadrao < numeroLinhasPadrao:
                linhaPico=tabelaPadrao.iloc[indexLinhaPadrao,0]
                indexLinhaAmostra = 0
                numeroLinhas=tabelaAmostra.iloc[:,1].count()
                numeroRejeicoes=0
                while indexLinhaAmostra < numeroLinhas:
                    picoDaVez=tabelaAmostra.iloc[indexLinhaAmostra,0]
                    diferenca=abs(linhaPico-picoDaVez) 
                    if diferenca > 0.5:
                        numeroRejeicoes+=1
                    if numeroRejeicoes == numeroLinhas:
                        picoFaltante+=1
                        nota=0
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,'-','-','-','Não','-','Não','Sim',nota]
                    contador+=1
                    indexLinhaAmostra += 1
                indexLinhaPadrao += 1
            #Variável que armazena a média das notas
            mediaColunaNotas=arrayDataFramesComparacao[numeroAba].iloc[:,8].mean()
            #Comando para adicionar essa média na array de médias
            arrayMedias.append(mediaColunaNotas)
            contador+=1
            #Cada tabela deve ter uma linha com informações no final:
            arrayDataFramesComparacao[numeroAba].loc[contador]=[f'Quantidade\nde Muito bom(s):\n{muitoBom}',f'Quantidade\nde Bom(s):\n{bom}',
                                                        f'Quantidade\nde Médio(s):\n{medio}',f'Quantidade\nde Pouco bom(s):\n{poucoBom}',
                                                        f'Quantidade\nde Ruim(s):\n{menosBom}','------',
                                                        f'Quantidade\nde picos\nexcedentes:\n{picoExcedente}',
                                                        f'Quantidade\nde picos\nfaltantes:\n{picoFaltante}',f'Nota\nfinal\né:{mediaColunaNotas}']
        #ipdb.set_trace() #Um comando para
                            #aquele módulo 
                            #de debug, basicamente um breakpoint,
                            #ponto de parada para analisar o
                            #código e seu comportamento
                            #bem como os valores das variáveis naquele
                            #momento em que o breakpoint se encontra
        
        #Agora vou ordenar todas as arrays criadas usando como critério de ordenação a média aritmética dos dataframes da arrayDataFramesComparacao
        #Para isso vou criar uma array que tem como item tuplas que guardam um conjunto de itens por vez das arrays selecionadas
        arrayMedCompCIFNomes=list(zip(arrayMedias,arrayDataFramesComparacao,arrayDeDataFramesCIFs,arrayNomesCIF)) #O zip() se responsabiliza por criar um iterável (Não pesquisei
        #ao certo o que isso significa, mas por intuição creio que seja uma variável que para acessar seus valores tem que se usar laços de iteração
        #como arrays (listas) ou tuplas) em que cada item é um conjunto de valores, um valor de um item da arrayMedias, um valor de um item da 
        #arrayDataFramesComparacao, um valor de um item da arrayDeDataFramesCIFs e um valor de um item da arrayNomesCIF, 
        #por sua vez o list() transforma isso numa array no todo.

        #Essa array criada é ordenada e alocada para a array seguinte, a ordenação é feita em função do item de arrayMedias da tupla
        array_ordenada_com_medias=sorted(arrayMedCompCIFNomes, key=lambda itemMedia: itemMedia[0], reverse=True)
        #Aqui temos a extração dos itens de DataFrame a partir da array ordenada de tuplas.
        #No caso, as variáveis temporárias representam os 4 itens presentes na tupla.
        #Então primeiro se escolhe quais desses itens será escolhido para array e expõe
        #quais serão os nomes temporários desses itens e por fim se referencia de qual array está se
        #tirando esses itens referenciados.
        #Essa utilização da compreensão de lista é algo poderoso mas que eu não dominei bem. Sinto que pode ser aplicado nas 
        #partes mais a cima do código, por exemplo na criação da alocação de dataFrames. Em algum nível sinto que a criação ddos dataframes
        #pode se dar nos próprios encadeamentos do while com seu append feito nesse próprio array
        arrayDfCompOrden = [itemComparacao for itemMedia, itemComparacao, itemCIF, itemNome in array_ordenada_com_medias]
        #Agora vamos garantir que os arrays que dizem respeito à planilha de CIFs seguem a mesma linha
        arrayDfCIFsOrden = [itemCIF for itemMedia, itemComparacao, itemCIF, itemNome in array_ordenada_com_medias]
        arrayDfNomesOrden = [itemNome for itemMedia,itemComparacao,itemCIF,itemNome in array_ordenada_com_medias]
        # É aqui onde os atributos recebem valores
        # para utilizar no método mostrarPlot()
        self.arrayAs3melhores=arrayDfCIFsOrden
        self.dataFramePadraoNoTodo=dataFramePadraoNoTodo
        self.arrayDfNomesOrden=arrayDfNomesOrden
        self.arrayDfCompOrden=arrayDfCompOrden
        self.numeroDeAbas=numeroDeAbas
        self.arrayDfCIFsOrden=arrayDfCIFsOrden
        self.mostrarResultados()
        #Após o QDialogBox ser fechado, as linhas de comando
        # continuam e colocam o valor padrão dos atributos para
        # não haver problemas
        self.arrayAs3melhores=None
        self.dataFramePadraoNoTodo=None
        self.arrayDfNomesOrden=None
        self.arrayDfCompOrden=None
        self.numeroDeAbas=None
        self.arrayDfCIFsOrden=None
        self.caminhoCIFs=None
        self.caminhoPadrao=None
        self.verificou1=None
        self.verificou2=None
    #Os métodos a seguir são pop-ups como o de método de erro.
    #Por isso vou me abster de explicar esses comandos de novo
    #com a ressalva de um que vou citar no primeiro método
    def mostrarInicio(self):
        inicio=QMessageBox()
        inicio.setIcon(QMessageBox.Information) #O ícone que aparece dentro do pop-up é de informação
        inicio.setText('A comparação vai começar. Isso normalmente demora alguns segundos, mas pode demorar minutos. Clique em OK para continuar.')
        inicio.setWindowTitle("Processo de comparação iniciada")
        inicio.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
        inicio.exec_()
    #Esse método é acionado no fim do método compararPicos em que mostra um gráfico com os três melhores CIFs
    def mostrarResultados(self):
        #Aqui, o atributo antes criado armazena o pop-up do QDialog
        self.dialogo=QDialog()
        self.dialogo.setWindowTitle("Comparação concluída")
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
        botaoMostrarGrafico.clicked.connect(self.mostrarGrafico)
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
    #método para mostrar o gráfico que é engatilhado
    def mostrarGrafico(self):
        # Tal comando evita que o caso o usuário pressione mais uma vez o
        # botão de mostrar gráfico, o que estava já aberto seja fechado e também
        # permite que a correção das intensidades dos CIFs seja efetuada corretamente
        # sem causar uma segundo multiplicação
        plt.close()
        # Pega-se o menor valor de intensidade do dataframe do padrão
        menorValor=self.dataFramePadraoNoTodo['y'].min()
        # Se o padrão tem como menor valor de intensidade até 500
        if menorValor <= 500:
            # Aumente as intensidades dos 3 melhores CIFs em 50 vezes
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*50
        # Caso até 1000...
        elif menorValor <= 1000:
            # Aumente em 100 vezes
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*100
        # Caso em até 2000...
        elif menorValor <= 2000:
            # Aumente em 150 vezes...
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*150
        # Então faça um gráfico de barras para cada CIF tendo como label sua colocação e seu nome,
        # como largura tem-se 0.1 pixels e cor vermelha para o primeiro, verde para o segundo e preto
        # para o terceiro
        plt.bar(self.arrayAs3melhores[0].iloc[:,0],self.arrayAs3melhores[0].iloc[:,1],label=f'Primeiro CIF: {self.arrayDfNomesOrden[0]}',color='red', width=0.1)
        plt.bar(self.arrayAs3melhores[1].iloc[:,0],self.arrayAs3melhores[1].iloc[:,1],label=f'Segundo CIF: {self.arrayDfNomesOrden[1]}',color='green', width=0.1)
        plt.bar(self.arrayAs3melhores[2].iloc[:,0],self.arrayAs3melhores[2].iloc[:,1],label=f'Terceiro CIF: {self.arrayDfNomesOrden[2]}',color='black', width=0.1)
        # Faz o plot do padrão, é importante que ele seja por
        # último para a curva do gráfico não ficar por cima
        # de nehuma barra de CIFs
        plt.plot(self.dataFramePadraoNoTodo['x'],self.dataFramePadraoNoTodo['y'],label='Dados',color='blue')
        plt.xlabel("Ângulo 2theta (°)")
        plt.ylabel("Intensidade (Contagens)")
        plt.legend()
        gerenciador=plt.get_current_fig_manager()
        gerenciador.set_window_title("Os 3 melhores CIFs para o padrão")
        plt.show()
        # Aproveitando-se do parâmetro que ditou o
        # o aumento em até 150 vezes da intensidade dos CIFs
        # utiliza-se o mesmo para diminuir os valores às intensidades
        # anteriores
        if menorValor <= 500:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]/50
        elif menorValor <= 1000:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]/100
        elif menorValor <= 2000:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]/150
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
        nomeArquivo, _ = QFileDialog.getSaveFileName(self, "Salvar planilha dos CIFs", "", filtroDeArquivo, options=opcoes)
        if nomeArquivo:
            if not nomeArquivo.endswith('.xlsx'):
                    nomeArquivo += '.xlsx'
            self.salvarPlanilhaCIF(nomeArquivo)
        else:
            mensagem=QMessageBox()
            mensagem.setIcon(QMessageBox.Information)
            mensagem.setText("A planilha dos CIFs não foi salva")
            mensagem.setWindowTitle("Arquivo não foi salvo")
            mensagem.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
            mensagem.exec_()

    def popUpPlanilhaComparacao(self):
        nomeArquivo=None
        opcoes=QFileDialog.Options()
        filtroDeArquivo = "Excel Files (*.xlsx);;All Files (*)"
        nomeArquivo, _ = QFileDialog.getSaveFileName(self, "Salvar planilhas de comparação", "", filtroDeArquivo, options=opcoes)
        if nomeArquivo:
            if not nomeArquivo.endswith('.xlsx'):
                    nomeArquivo += '.xlsx'
            self.salvarPlanilhaComparacao(nomeArquivo)
        else:
            mensagem=QMessageBox()
            mensagem.setIcon(QMessageBox.Information)
            mensagem.setText("A planilha de comparação não foi salva")
            mensagem.setWindowTitle("Arquivo não foi salvo")
            mensagem.setWindowIcon(QIcon(resource_path(r'icones\icone.ico')))
            mensagem.exec_()

    def salvarPlanilhaCIF(self,parametroNomeArquivo):
        nomeArquivo=parametroNomeArquivo
        with pd.ExcelWriter(nomeArquivo) as writer2:
            for numeroAba in range(self.numeroDeAbas):
                self.arrayDfCIFsOrden[numeroAba].to_excel(writer2,sheet_name=self.arrayDfNomesOrden[numeroAba],index=False)

    def salvarPlanilhaComparacao(self,parametroNomeArquivo):
        nomeArquivo=parametroNomeArquivo
        with pd.ExcelWriter(nomeArquivo) as writer1: #Cria-se um objeto para a planilha saída
        
        #Basicamente, ao fim das análises, os DataFrames criados são alojados na array de DataFrames e
        #cada dataFrame é endereçado a sua aba, garanta que cada aba tenha o nome correto da amostra que foi
        #comparada
            for numeroAba in range(self.numeroDeAbas): #Aqui esse for é para garantir que diferentes dataFrames estão sendo
                                        #sendo adicionados em abas diferentes à planilha saída
                self.arrayDfCompOrden[numeroAba].to_excel(writer1,sheet_name=self.arrayDfNomesOrden[numeroAba],index=False)
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