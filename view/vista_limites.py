from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Módulo de Análisis de Límites Listo"))