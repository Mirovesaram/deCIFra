import sys
import io
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Integração Matplotlib com PyQt5")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout()

        # QLabel para exibir o gráfico
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # Botão para plotar o gráfico
        self.plot_button = QPushButton("Plotar Gráfico", self)
        self.plot_button.clicked.connect(self.plot_graph)
        layout.addWidget(self.plot_button)

        # Configuração do layout principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def plot_graph(self):
        # Criar uma figura do Matplotlib
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot([0, 1, 2, 3], [10, 1, 20, 3], marker='o', linestyle='-', color='b')
        ax.set_title("Exemplo de Gráfico")
        ax.set_xlabel("Eixo X")
        ax.set_ylabel("Eixo Y")

        # Renderizar a figura como uma imagem em um objeto BytesIO
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)

        # Criar um QPixmap a partir da imagem em BytesIO
        image = QPixmap()
        image.loadFromData(buf.getvalue(), 'PNG')

        # Definir a imagem na QLabel
        self.label.setPixmap(image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
