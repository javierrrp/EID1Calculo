from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class VistaConicas(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Módulo de Secciones Cónicas Listo"))