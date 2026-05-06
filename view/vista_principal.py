import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel


class VistaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test")
        self.setGeometry(100, 100, 800, 600)

        # Crear un widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

    
