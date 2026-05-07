from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class VistaRut(QWidget):
    # Señal para avisar al controlador que se hizo clic en validar
    boton_validar_clicado = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # --- TARJETA DE ENTRADA ---
        self.card_input = QFrame()
        self.card_input.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 30px;
                padding: 20px;
            }
        """)
        self.apply_shadow(self.card_input)
        
        card_layout = QVBoxLayout(self.card_input)
        
        # Título Instrucción
        instruccion = QLabel("INGRESA TU IDENTIDAD")
        instruccion.setStyleSheet("color: #64748B; font-weight: 800; font-size: 14px; letter-spacing: 1px;")
        card_layout.addWidget(instruccion, alignment=Qt.AlignmentFlag.AlignCenter)

        # Input del RUT Estilizado
        self.input_rut = QLineEdit()
        self.input_rut.setPlaceholderText("12.345.678-K")
        self.input_rut.setMinimumHeight(80)
        self.input_rut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_rut.setStyleSheet("""
            QLineEdit {
                border: 3px solid #F1F5F9;
                border-radius: 20px;
                font-size: 32px;
                font-weight: 900;
                color: #1E293B;
                background-color: #F8FAFC;
            }
            QLineEdit:focus {
                border: 3px solid #4ECDC4;
                background-color: white;
            }
        """)
        card_layout.addWidget(self.input_rut)

        # Botón de Acción
        self.btn_validar = QPushButton("VERIFICAR SISTEMA")
        self.btn_validar.setMinimumHeight(60)
        self.btn_validar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validar.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7AF;
            }
        """)
        self.btn_validar.clicked.connect(self.emitir_evento_validar)
        card_layout.addWidget(self.btn_validar)

        layout.addWidget(self.card_input)

        # --- ÁREA DE LOG / PROCEDIMIENTO (Consola Creativa) ---
        self.label_titulo_log = QLabel("PROCEDIMIENTO MÓDULO 11")
        self.label_titulo_log.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.label_titulo_log)

        self.log_output = QLabel("Esperando datos de entrada...")
        self.log_output.setWordWrap(True)
        self.log_output.setMinimumHeight(200)
        self.log_output.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_output.setStyleSheet("""
            QLabel {
                background-color: #1E293B;
                color: #A5F3FC;
                font-family: 'Consolas', 'Courier New';
                font-size: 13px;
                padding: 20px;
                border-radius: 20px;
                border-left: 5px solid #4ECDC4;
            }
        """)
        layout.addWidget(self.log_output)
        
        layout.addStretch()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def emitir_evento_validar(self):
        # Envía el texto al controlador
        self.boton_validar_clicado.emit(self.input_rut.text())

    def mostrar_resultado(self, exito, mensaje):
        """Actualiza la consola con el resultado del modelo"""
        self.log_output.setText(mensaje)
        if exito:
            self.log_output.setStyleSheet(self.log_output.styleSheet() + "border-left: 5px solid #4ECDC4; color: #A5F3FC;")
        else:
            self.log_output.setStyleSheet(self.log_output.styleSheet() + "border-left: 5px solid #FF6B6B; color: #FECACA;")