import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from interfaceGerada.design import Ui_MainWindow  # Importa a classe gerada pela interface
"""'from pasta.scriptPy import classe' --- interessante"""

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Configura a interface definida em Ui_MainWindow

        # Conectar sinais e slots
        #Exemplo
        #self.pushButton.clicked.connect(self.botao_clicado)
    
    #def botao_clicado(self):
    #    print("Botão clicado!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())