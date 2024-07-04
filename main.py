from interfaceGerada.design import Ui_MainWindow  # Importa a classe gerada pela interface
"""'from pasta.scriptPy import classe' --- interessante"""
#!pip install ipdb Esse ponto de exclamação só funciona no collab para instalação em meio ao código
#import ipdb #Esses comandos foram para importar esse módulo
        #que serviu de ferramenta para estudar erros do código
        #usando debug

import logging #módulo para permitir colocar os erros num arquivo de log

import sys #módulo para controlar o sistema/programa para poder fechar ele, por exemplo (Acho, não entrei em detalhes)

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QMainWindow, QTextEdit, QDialogButtonBox, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon

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

from findpeaks import findpeaks

import matplotlib.pyplot as plt 

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
    erro.setWindowIcon(QIcon(r"C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\icones\icone.ico"))
    #E os detalhes do erro, como onde
    #ocorreu nas linhas de código
    erro.setDetailedText(mensagemErro)
    #Comando para quando fechar a caixa, encerrar o programa
    erro.exec_()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        #Chamando o construtor (Método inicializador)
        #da classe pai no método construtor da classe filha.
        #O uso específico desse comando é no construtor da classe filhas
        super().__init__()
        self.setupUi(self)  # Configura a interface definida em Ui_MainWindow

        self.arrayAs3melhores = []

        self.dataFramePadraoNoTodo = None

        self.dialogo=None

        self.diretorioAtual=os.path.dirname(os.path.abspath(__file__))

        self.valorLimite = self.doubleSpinBoxMudarLimite.value()

        self.limitePadrao = None

        self.arquivoXy = None

        self.verificou1=None

        self.verificou2=None

        self.travaLogica=None

        self.diretorioCIFs2=None

        self.diretorioPadrao2=None

        self.diretorioCIFs=None

        self.diretorioPadrao=None

        self.dfPicos=None

        self.arrayPicos=[None, None, None, None,None]

        self.ultimoIndex=None
        #Comando para deixar a janela não redimensionável
        self.setFixedSize(800,800)
        self.setWindowIcon(QIcon(r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\icones\icone.ico'))
        #Criar um gatilho que envolve clicar esse botão
        #Caso clique no botão, o método abrirDirEventCIFs
        #será chamado e iniciado
        self.botaoSelecCIF.clicked.connect(self.abrirDirEventCIFs)
        #Criação de uma caixa de texto que permite scrollar para 
        #textos maiores
        self.caminhoCIFsText = QTextEdit(self.tabComparar)
        #Comando para permitir somente leitura, sem alteração
        #do texto pelo usuário
        self.caminhoCIFsText.setReadOnly(True)
        #Inserir o texto padrão presente nessa caixa de texto
        self.caminhoCIFsText.setText('O caminho aparecerá aqui quando selecionado')
        #Padding cria uma margem interna de 10 px
        self.caminhoCIFsText.setStyleSheet("padding: 10px;")
        #Comando que ajusta a posição x, a posição y, a largura,
        #a altura, respectivamente na caixa de edição de texto
        self.caminhoCIFsText.setGeometry(0,80,800,100)

        self.botaoSelecPadrao.clicked.connect(self.abrirDirEventSeuPadrao)

        #A utilização de uma caixa de texto é um recurso, do ponto de vista de design,
        #estranho. Mas foi a maneira proposta para garantir que caso um caminho seja
        #muito grande, ele não ultrapasse o tamanho proposto da janela, pois a primeira
        #ideia foi utilizar um QLabel seguido de adjustSize().
        self.caminhoPadraoText = QTextEdit(self.tabComparar)
        self.caminhoPadraoText.setReadOnly(True)
        self.caminhoPadraoText.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoPadraoText.setStyleSheet('padding: 10px;')
        self.caminhoPadraoText.setGeometry(0,260,800,100)
        #Comandos para adicionar os dados dos itens da combo
        #Box de radiação que são
        #os valores do parâmetro userData=, a string vazia ""
        #é porque o código .py da interface visual
        #adiciona como esses dados #aparecerão para o usuário
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
        #evidenciando sua posiçaõ
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
        """
        self.caixaRadiacoes.setCurrentIndex(0)
        self.caixaRadiacoes.activated.emit(0)
        self.caixaRadiacoes_2.setCurrentIndex(0)
        self.caixaRadiacoes_2.activated.emit(0)
        #Esse método que será chamado é para verificar se o usuário colocou
        #os caminhos necessários antes de apertar o botão para fazer a comparação
        self.botaoComparar.clicked.connect(self.verificar)
        #pequeno teste para ver se os itens da
        #comboBox foram corretamente adicionados
        """self.botaoComparar.clicked.connect(self.testeComboBox)
        self.label = QLabel(self.tabComparar)
        self.label.move(200,650)"""
    
        self.caminhoArquivoXyText = QTextEdit(self.tabDetectar)
        self.caminhoArquivoXyText.setReadOnly(True)
        self.caminhoArquivoXyText.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoArquivoXyText.setStyleSheet("padding: 10px;")
        self.caminhoArquivoXyText.setGeometry(0,40,800,100)

        self.botaoSelecionarArquivoXy.clicked.connect(self.abrirDirEventXy)

        self.pushButtonDetectar.clicked.connect(self.detectarVisualizarPicos)

        self.pushButtonSalvarFigura.clicked.connect(self.salvarGrafico)

        self.pushButtonImportar.clicked.connect(self.importarAngulos)

        self.botaoSelecPadrao_2.clicked.connect(self.abrirDirEventSeuPadraoAdicionarPicos)
        
        self.caminhoPadraoText_2 = QTextEdit(self.tabCompararPoucosPicos)
        self.caminhoPadraoText_2.setReadOnly(True)
        self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoPadraoText_2.setStyleSheet("padding: 10px;")
        self.caminhoPadraoText_2.setGeometry(0,80,800,100)

        self.comboBoxPico1.activated.connect(self.picoSelecionado1)
        self.comboBoxPico2.activated.connect(self.picoSelecionado2)
        self.comboBoxPico3.activated.connect(self.picoSelecionado3)
        self.comboBoxPico4.activated.connect(self.picoSelecionado4)
        self.comboBoxPico5.activated.connect(self.picoSelecionado5)
        self.emitirSinaisComboBoxPicos()

        #pequeno teste para ver se os itens da
        #comboBox foram corretamente adicionados
        """self.botaoComparar_2.clicked.connect(self.testeComboBox)
        self.label = QLabel(self.tabCompararPoucosPicos)
        self.label.move(200,650)"""

        self.botaoSelecCIF_2.clicked.connect(self.abrirDirEventCIFs2)

        self.caminhoCIFsText_2 = QTextEdit(self.tabCompararPoucosPicos)
        self.caminhoCIFsText_2.setReadOnly(True)
        self.caminhoCIFsText_2.setText('O caminho aparecerá aqui quando selecionado')
        self.caminhoCIFsText_2.setStyleSheet("padding: 10px;")
        self.caminhoCIFsText_2.setGeometry(0,340,800,100)

        self.botaoComparar_2.clicked.connect(self.verificar2)
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
    def removerItens(self):
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
    def picoSelecionado1(self,index):
        self.pico1=self.comboBoxPico1.itemData(index)
        self.arrayPicos[0]=self.pico1
        #Somente para testes
        #print(self.arrayPicos)
    def picoSelecionado2(self,index):
        self.pico2=self.comboBoxPico2.itemData(index)
        self.arrayPicos[1]=self.pico2
        #print(self.arrayPicos)
    def picoSelecionado3(self,index):
        self.pico3=self.comboBoxPico3.itemData(index)
        self.arrayPicos[2]=self.pico3
        #print(self.arrayPicos)
    def picoSelecionado4(self,index):
        self.pico4=self.comboBoxPico4.itemData(index)
        self.arrayPicos[3]=self.pico4
        #print(self.arrayPicos)
    def picoSelecionado5(self,index):
        self.pico5=self.comboBoxPico5.itemData(index)
        self.arrayPicos[4]=self.pico5          
        """self.arrayPicosSemNone=[item for item in self.arrayPicos if item is not None]
        print(self.arrayPicosSemNone)"""
        #print(self.arrayPicos)
    
    def arrayParaDataFrame(self):
        self.arraySemNone = [item for item in self.arrayPicos if item is not None]
        if self.arraySemNone != []:
            self.arraySNoneSRepet=set(self.arraySemNone)
            self.dfPicos=pd.DataFrame(self.arraySNoneSRepet, columns=["angulos"])
            #Para fins de teste e avaliação do valor recebido
            #print(self.dfPicos)
            self.travaLogica=False
        else:
            self.dfPicos=None
            self.travaLogica=True
             
    #O método que tinha sido citado anteriormente que age junto ao caixaRadiacoes
    def itemSelecionado(self,index):
        self.valorSelecionado=self.caixaRadiacoes.itemData(index)
    def itemSelecionado2(self,index):
        self.valorSelecionado2=self.caixaRadiacoes_2.itemData(index)
    #Método para abrir o explorer do computador e selecionar a pasta necessária
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

    def abrirDirEventSeuPadraoAdicionarPicos(self):
        self.diretorioPadrao2=None
        opcoes = QFileDialog.Options()
        opcoes |= QFileDialog.ShowDirsOnly
        diretorioPadrao = QFileDialog.getExistingDirectory(self,'Selecionar Pasta do seu Padrão','',options=opcoes)
        self.diretorioPadrao2=diretorioPadrao
        if diretorioPadrao:
            #Variaveis que vão receber e adicionar os caminhos em string para utilizar mais na frente
            caminhoPadrao=diretorioPadrao
            #Arquivo que vai guardar o caminho do arquivo .xlsx
            buscaPlanilhaPadrao = os.path.join(caminhoPadrao,'*.xlsx')
            ArrayCaminhoPlanilhaPadrao = glob.glob(buscaPlanilhaPadrao)
            if ArrayCaminhoPlanilhaPadrao:
                self.caminhoPadraoText_2.setText(diretorioPadrao)
                #Coleta-se o único item dessa array criada na linha anterior
                if self.ultimoIndex:
                    self.removerItens()
                caminhoPadrao=ArrayCaminhoPlanilhaPadrao[0]
                tabelaPadrao = pd.read_excel(caminhoPadrao)
                numeroLinhasPadrao=tabelaPadrao.iloc[:,0].count()
                for numeroLinha in range(numeroLinhasPadrao):
                    pico=tabelaPadrao.iloc[numeroLinha,0]
                    self.comboBoxPico1.addItem(str(pico))
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
                self.ultimoIndex=self.comboBoxPico1.count()-1
            else:
                self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
                if self.ultimoIndex:
                    self.removerItens()
                raise ValueError("A pasta não tem um arquivo .xlsx.")                  
        else:
            self.caminhoPadraoText_2.setText('O caminho aparecerá aqui quando selecionado')
            if self.ultimoIndex:
                self.removerItens()
                
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

    def abrirDirEventXy(self):
        self.arquivoXy=None
        opcoes = QFileDialog.Options()
        arquivoXy, _ = QFileDialog.getOpenFileName(self, 'Selecionar arquivo .xy', '', 'Arquivos XY (*.xy);;Todos os arquivos (*)', options=opcoes)
        if arquivoXy:
            self.arquivoXy=arquivoXy
            self.caminhoArquivoXyText.setText(arquivoXy)
            dataFramePadrao = pd.read_csv(self.arquivoXy, delim_whitespace=True, header=None, names=['x','y'])
            self.angulos=dataFramePadrao.x.values
            self.intensidades=dataFramePadrao.y.values
            self.X = self.intensidades
            self.limitePadrao=np.min(np.min(self.X))-1
            self.doubleSpinBoxMudarLimite.setValue(self.limitePadrao)
            self.mostrarLimitePadrao()
        else:
            self.arquivoXy=None
            self.limitePadrao=None
            self.mostrarLimitePadrao()
            self.doubleSpinBoxMudarLimite.setValue(0)
            self.valorLimite=self.doubleSpinBoxMudarLimite.value()
            self.caminhoArquivoXyText.setText('O caminho aparecerá aqui quando selecionado')  

    def detectarVisualizarPicos(self):
        #buscaXyPadrao=os.path.join(caminho,'*.xy')
        #ArrayCaminhoXy=glob.glob(buscaXyPadrao)
        if self.arquivoXy:
            self.valorLimite=self.doubleSpinBoxMudarLimite.value()   
            fp = findpeaks(method='topology',limit=self.valorLimite)
            results = fp.fit(self.X)
            #fp.plot()
            # Extract peak positions
            angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()

            # Plotting the results
            #plt.switch_backend('Qt5Agg')
            plt.plot(self.angulos, self.intensidades, label='Dados', color='blue')
            plt.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
            plt.legend()
            #plt.savefig("picosEncontrados.png")

            gerenciador=plt.get_current_fig_manager()
            gerenciador.set_window_title("Picos detectados com o limite "+str(self.valorLimite))

            plt.show()

            # Print peak positions
            #print("Peak positions:", self.angulos[self.angulosPicos])
            #print(len(angulos[peak_positions]))
            #df=pd.DataFrame(results['df'])
            #caminho=r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\df.xlsx'
            #df.to_excel(caminho)
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
        
    def salvarGrafico(self):
        if self.arquivoXy:
            self.valorLimite=self.doubleSpinBoxMudarLimite.value()   
            fp = findpeaks(method='topology',limit=self.valorLimite)
            results = fp.fit(self.X)
            #fp.plot()
            # Extract peak positions
            angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
            # Plotting the results
            #plt.switch_backend('Qt5Agg')
            plt.plot(self.angulos, self.intensidades, label='Dados', color='blue')
            plt.scatter(self.angulos[angulosPicos], self.intensidades[angulosPicos], color='red', label='Picos')
            plt.legend()
            plt.savefig("picosEncontrados.png")
            plt.close()
            self.mostrarConclusao()


            
            # Print peak positions
            #print("Peak positions:", self.angulos[self.angulosPicos])
            #print(len(angulos[peak_positions]))
            #df=pd.DataFrame(results['df'])
            #caminho=r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\df.xlsx'
            #df.to_excel(caminho)
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
            
    def importarAngulos(self):
        if self.arquivoXy:
            self.valorLimite=self.doubleSpinBoxMudarLimite.value()   
            fp = findpeaks(method='topology',limit=self.valorLimite)
            results = fp.fit(self.X)
            angulosPicos = results['df'].index[results['df']['peak'] == True].tolist()
            dataFramePicos=pd.DataFrame(angulosPicos, columns=["Ângulos"])
            dataFramePicos.to_excel(r'picosEncontrados.xlsx')
            self.mostrarConclusao()
        else:
            raise ValueError('O arquivo .xy não foi selecionado.')
        
    def mostrarLimitePadrao(self):
        if self.limitePadrao:
            self.labelValorLimite.setText(str(self.limitePadrao))
        else:
            self.labelValorLimite.setText('-')
    #Método que verifica se os dois últimos atributos do construtor deixaram de ser
    #Nones (vazios)
    def verificar(self):
        #Se os dois atributos estão preenchidos simultaneamente
        #(Não são mais vazios)
        if self.diretorioCIFs and self.diretorioPadrao:
            #Atributos que vão receber e adicionar os caminhos em string para utilizar mais na frente
            self.caminhoCIFs=self.diretorioCIFs
            self.caminhoPadrao=self.diretorioPadrao
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
    def verificar2(self):
        #Se os dois atributos estão preenchidos simultaneamente
        #(Não são mais vazios)
        if self.diretorioCIFs2 and self.diretorioPadrao2:
            self.arrayParaDataFrame()
            if self.travaLogica == False:
                self.caminhoCIFs=self.diretorioCIFs2
                self.caminhoPadrao=self.diretorioPadrao2
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
    def mostrarPlot(self):
        self.dialogo=QDialog()
        self.dialogo.setWindowTitle("Comparação concluída")
        self.dialogo.setWindowIcon(QIcon(r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\icones\icone.ico'))
        layout=QVBoxLayout()
        texto=QLabel("Comparação concluída, resultados salvos em:\n"+self.diretorioAtual+"\nGráfico disponível:")
        layout.addWidget(texto)
        caixaBotoes=QDialogButtonBox()
        botaoMostrarGrafico = QPushButton("Mostrar Gráfico")
        botaoSalvarGrafico = QPushButton("Salvar Gráfico")
        caixaBotoes.addButton(botaoMostrarGrafico, QDialogButtonBox.ActionRole)
        caixaBotoes.addButton(botaoSalvarGrafico, QDialogButtonBox.ActionRole)
        layout.addWidget(caixaBotoes)       
        self.dialogo.setLayout(layout)
        botaoMostrarGrafico.clicked.connect(self.mostrarGrafico)
        botaoSalvarGrafico.clicked.connect(self.salvarGrafico)   
        self.dialogo.open()
    def mostrarGrafico(self):
        menorValor=self.dataFramePadraoNoTodo['y'].min()
        plt.plot(self.dataFramePadraoNoTodo['x'],self.dataFramePadraoNoTodo['y'],label='Dados',color='blue')
        if menorValor <= 500:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*10
        elif menorValor <= 1000:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*50
        elif menorValor <= 2000:
            for i in range(3):
                dataFrameDaVez=self.arrayAs3melhores[i]
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*250
        plt.bar(self.arrayAs3melhores[0].iloc[:,0],self.arrayAs3melhores[0].iloc[:,1],label='Reflexões',color='red', width=0.1)
        plt.bar(self.arrayAs3melhores[1].iloc[:,0],self.arrayAs3melhores[1].iloc[:,1],label='Reflexões',color='green', width=0.1)
        plt.bar(self.arrayAs3melhores[2].iloc[:,0],self.arrayAs3melhores[2].iloc[:,1],label='Reflexões',color='black', width=0.1)
        plt.show()
    def salvarGrafico(self):
        menorValor=self.dataFramePadraoNoTodo['y'].min()
        plt.plot(self.dataFramePadraoNoTodo['x'],self.dataFramePadraoNoTodo['y'],label='Dados',color='blue')
        for i in range(3):
            dataFrameDaVez=self.arrayAs3melhores[i]
            if menorValor <= 500:
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*10
            elif menorValor <= 1000:
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*50
            elif menorValor <= 2000:
                dataFrameDaVez.iloc[:,1]=dataFrameDaVez.iloc[:,1]*250
            plt.bar(dataFrameDaVez.iloc[:,0],dataFrameDaVez.iloc[:,1],label='Reflexões',color='red')
        plt.savefig('graficoMelhoresCIFs.png')
        plt.close()
    #Método para comparar picos
    def compararPicos(self):
        self.mostrarInicio()
        #Variável responsável por armazenar qual tipo de arquivo deve ser buscado
        extensaoArquivo='*.cif'
        if self.verificou1==True:
            #Variável para saber o comprimento de onda utilizado para montar os padrões de difração dos CIFs
            comprimentoOndaAngstron=self.valorSelecionado #Utiliza o valor slecionado na caixaRadiacoes
        elif self.verificou2==True:
            comprimentoOndaAngstron=self.valorSelecionado2
        #Arquivo que vai guardar o caminho do arquivo .xy
        buscaXyPadrao = os.path.join(self.caminhoPadrao,'*.xy')
        #Transforma numa array de strings caminho
        ArrayCaminhoXy=glob.glob(buscaXyPadrao)
        #Arquivo que vai guardar o caminho do arquivo .xlsx
        buscaPlanilhaPadrao = os.path.join(self.caminhoPadrao,'*.xlsx')
        ArrayCaminhoPlanilhaPadrao = glob.glob(buscaPlanilhaPadrao)
        #Coleta-se o único item dessa array criada na linha anterior
        caminhoPadrao=ArrayCaminhoPlanilhaPadrao[0]
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
        
        arrayDataFramesComparacao=[] #Aqui é o array de DataFrames modelo, tal arranjo é importante para haver uma distinção autônoma de cada dataFrame para cada
                            #aba construída na planilha de saída
        
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
        for numeroAba in range(numeroDeAbas):
            #Criando variável que lerá os dados de pico na coluna 2theta da planilha do seu padrão designado
            if self.verificou1 == True:
                tabelaPadrao = pd.read_excel(caminhoPadrao)
            elif self.verificou2 == True:
                tabelaPadrao = self.dfPicos
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
                        arrayDataFramesComparacao[numeroAba].loc[contador]=[linhaPico,picoDaVez,intensidadePicoAmostra,diferenca,'Sim','Menos bom','Não','Não',nota]
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
                                                        f'Quantidade\nde Menos bom(s):\n{menosBom}','------',
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
        with pd.ExcelWriter(f"{self.caminhoCIFs}/comparacao.xlsx") as writer1: #Cria-se um objeto para a planilha saída
        
        #Basicamente, ao fim das análises, os DataFrames criados são alojados na array de DataFrames e
        #cada dataFrame é endereçado a sua aba, garanta que cada aba tenha o nome correto da amostra que foi
        #comparada

            for numeroAba in range(numeroDeAbas): #Aqui esse for é para garantir que diferentes dataFrames estão sendo
                                        #sendo adicionados em abas diferentes à planilha saída
                arrayDfCompOrden[numeroAba].to_excel(writer1,sheet_name=arrayDfNomesOrden[numeroAba],index=False)
        with pd.ExcelWriter(f"{self.caminhoCIFs}/planilhaCIFs.xlsx") as writer2:
            for numeroAba in range(numeroDeAbas):
                arrayDfCIFsOrden[numeroAba].to_excel(writer2,sheet_name=arrayDfNomesOrden[numeroAba],index=False)
        self.arrayAs3melhores=arrayDfCIFsOrden
        self.dataFramePadraoNoTodo=dataFramePadraoNoTodo
        self.mostrarPlot()
    #Os métodos a seguir são pop-ups como o de método de erro.
    #Por isso vou me abster de explicar esses comandos de novo
    #com a ressalva de um que vou citar no primeiro método
    def mostrarInicio(self):
        inicio=QMessageBox()
        inicio.setIcon(QMessageBox.Information) #O ícone que aparece dentro do pop-up é de informação
        inicio.setText('A comparação vai começar. Isso normalmente demora alguns segundos, mas pode demorar minutos. Clique em OK para continuar.')
        inicio.setWindowTitle("Processo de comparação iniciada")
        inicio.setWindowIcon(QIcon(r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\icones\icone.ico'))
        inicio.exec_()

    def mostrarConclusao(self):
        conclusao = QMessageBox()
        conclusao.setIcon(QMessageBox.Information)
        conclusao.setText("A tarefa foi concluída com sucesso.\nO resultado foi colocado em:\n"+self.diretorioAtual)
        conclusao.setWindowTitle("Tarefa concluída!")
        conclusao.setWindowIcon(QIcon(r'C:\Users\aojor\Downloads\CodigosPython\vsCode\projetos\pacoteComparadorPicos\comparadorPicos\icones\icone.ico'))
        conclusao.exec_()
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