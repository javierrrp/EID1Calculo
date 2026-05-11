from PyQt6.QtWidgets import *

class VistaConicas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Cónicas")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        self.lbl_titulo = QLabel("Analizando Conica...")
        layout.addWidget(self.lbl_titulo)

        layout.addWidget(QLabel("Desarrollo matematico:"))
        self.txt_procedimiento = QTextEdit()
        self.txt_procedimiento.setReadOnly(True)
        layout.addWidget(self.txt_procedimiento)


        layout.addWidget(QLabel("Elementos geometricos:"))

        layout.addWidget(QLabel("Centro (h, k):"))
        self.input_centro = QLineEdit()
        layout.addWidget(self.input_centro)

        layout.addWidget(QLabel("Focos / Vertices:"))
        self.input_focos = QLineEdit()
        layout.addWidget(self.input_focos)