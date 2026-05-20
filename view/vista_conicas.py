from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class VistaConicas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Cónicas")
        self.setMinimumSize(850, 550)

        layout_principal = QHBoxLayout(self)

        panel_izquierdo = QWidget()
        layout_izquierdo = QVBoxLayout(panel_izquierdo)

        self.lbl_titulo = QLabel("Analizando Conica...")
        self.lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_izquierdo.addWidget(self.lbl_titulo)

        layout_izquierdo.addWidget(QLabel("Desarrollo matematico:"))
        self.txt_procedimiento = QTextEdit()
        self.txt_procedimiento.setReadOnly(True)
        layout_izquierdo.addWidget(self.txt_procedimiento)

        layout_izquierdo.addWidget(QLabel("Procedimiento Inverso (Canónica -> General):"))
        self.txt_procedimiento_inverso = QTextEdit()
        self.txt_procedimiento_inverso.setReadOnly(True)
        layout_izquierdo.addWidget(self.txt_procedimiento_inverso)
        

        layout_izquierdo.addWidget(QLabel("Elementos geometricos:"))

        layout_izquierdo.addWidget(QLabel("Centro (h, k):"))
        self.input_centro = QLineEdit()
        layout_izquierdo.addWidget(self.input_centro)

        layout_izquierdo.addWidget(QLabel("Radio:"))
        self.input_radio = QLineEdit()
        layout_izquierdo.addWidget(self.input_radio)

        layout_izquierdo.addWidget(QLabel("Focos / Vertices:"))
        self.input_focos = QLineEdit()
        layout_izquierdo.addWidget(self.input_focos)
        
        #boton para verificar
        self.btn_verificar = QPushButton("Verificar Respuestas")
        self.btn_verificar.setStyleSheet("background-color: #3B82F6; color: white; font-weight: bold; padding: 8px;")
        layout_izquierdo.addWidget(self.btn_verificar)

        layout_principal.addWidget(panel_izquierdo, stretch=1)

        self.plano = PlanoCartesiano()
        layout_principal.addWidget(self.plano, stretch=1) 




class PlanoCartesiano(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        # Fondo blanco para que parezca hoja de cuaderno
        self.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 8px;")

        #inicializar variables para el centro de la conica
        self.h = None
        self.k = None
        self.tipo_conica = None
        self.radio = None

        self.offset_x = 0
        self.offset_y = 0
        self.last_mouse_pos = None
        self.separacion = 25

    def actualizar_figura(self, h, k, tipo=None, radio=None):
        self.h = h
        self.k = k
        self.tipo_conica = tipo
        self.radio = radio
        self.update()


    #mover grafico
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor) # Cambia el cursor a mano cerrada

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor) # Cambia el cursor a flecha normal

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.separacion += 5
        else:
            self.separacion = max(5, self.separacion - 5)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ancho = self.width()
        alto = self.height()
        centro_x = (ancho // 2) + int(self.offset_x)
        centro_y = (alto // 2) + int(self.offset_y)

        pen_cuadricula = QPen(QColor(220, 220, 220), 1)
        pen_texto = QPen(QColor(120, 120, 120))
        painter.setPen(pen_cuadricula)
        fuente_numeros = self.font()
        fuente_numeros.setPointSize(8)
        painter.setFont(fuente_numeros)

        rango = 100

        for i in range(-rango, rango + 1):
            px = centro_x + (i * self.separacion)
            py = centro_y - (i * self.separacion)

            if 0 <= px <= ancho:
                painter.setPen(pen_cuadricula)
                painter.drawLine(px, 0, px, alto)
                if i != 0 and i % 2 == 0:
                    painter.setPen(pen_texto)
                    painter.drawText(px - 6, centro_y + 15, str(i))

            if 0 <= py <= alto:
                painter.setPen(pen_cuadricula)
                painter.drawLine(0, py, ancho, py)
                if i != 0 and i % 2 == 0:
                    painter.setPen(pen_texto)
                    painter.drawText(centro_x + 5, py + 4, str(i))

        pen_ejes = QPen(QColor(50, 50, 50), 2)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y)
        painter.drawLine(centro_x, 0, centro_x, alto)

        # Dibujar el centro si tenemos los datos proporcionados
        if self.h is not None and self.k is not None:
            px = centro_x + (self.h * self.separacion)
            py = centro_y - (self.k * self.separacion)

            painter.setBrush(QColor("red"))
            painter.setPen(Qt.GlobalColor.transparent)
            painter.drawEllipse(int(px) - 4, int(py) - 4, 8, 8)
