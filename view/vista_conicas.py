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

        if ancho <= 0 or alto <= 0 or self.separacion <= 0:
            return

        if self.separacion >= 100:
            paso_grilla = 0.5
            paso_texto = 0.5
        elif self.separacion >= 50:
            paso_grilla = 1
            paso_texto = 1
        elif self.separacion >= 20:
            paso_grilla = 1
            paso_texto = 2
        elif self.separacion >= 10:
            paso_grilla = 1
            paso_texto = 5
        else:
            paso_grilla = 5
            paso_texto = 10

        val_min_x = -centro_x / self.separacion
        val_max_x = (ancho - centro_x) / self.separacion
        val_min_y = (centro_y - alto) / self.separacion
        val_max_y = centro_y / self.separacion

        limite_min = int(min(val_min_x, val_min_y)) - 2
        limite_max = int(max(val_max_x, val_max_y)) + 2

        pen_cuadricula = QPen(QColor(230, 230, 230), 1)
        pen_texto = QPen(QColor(120, 120, 120))
        fuente_numeros = self.font()
        fuente_numeros.setPointSize(8)
        painter.setFont(fuente_numeros)

        for i in range(limite_min * 2, limite_max * 2):
            val = i * 0.5

            # Dibujar líneas solo si calza con el paso_grilla asignado
            if (val * 10) % (paso_grilla * 10) != 0:
                continue

            px = centro_x + int(val * self.separacion)
            py = centro_y - int(val * self.separacion)
            
            # Formatear el número (quita los ceros a la derecha)
            texto_numero = f"{val:g}"

            # Líneas verticales (Eje X)
            if 0 <= px <= ancho:
                painter.setPen(pen_cuadricula)
                painter.drawLine(px, 0, px, alto)
                if val != 0 and (val * 10) % (paso_texto * 10) == 0:
                    painter.setPen(pen_texto)
                    painter.drawText(px - 6, centro_y + 15, texto_numero)

            # Líneas horizontales (Eje Y)
            if 0 <= py <= alto:
                painter.setPen(pen_cuadricula)
                painter.drawLine(0, py, ancho, py)
                if val != 0 and (val * 10) % (paso_texto * 10) == 0:
                    painter.setPen(pen_texto)
                    painter.drawText(centro_x + 5, py + 4, texto_numero)

        # Ejes principales (El 0)
        pen_ejes = QPen(QColor(50, 50, 50), 2)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y)
        painter.drawLine(centro_x, 0, centro_x, alto)

    
        if self.h is not None and self.k is not None:
            px = centro_x + (self.h * self.separacion)
            py = centro_y - (self.k * self.separacion)

            if self.tipo_conica == "Circunferencia" and self.radio is not None:
                radio_px = self.radio * self.separacion
                pen_figura = QPen(QColor(41, 128, 185), 3)
                painter.setPen(pen_figura)
                painter.setBrush(QColor(52, 152, 219, 40))
                painter.drawEllipse(int(px - radio_px), int(py - radio_px), int(radio_px * 2), int(radio_px * 2))

        
            painter.setBrush(QColor("red"))
            painter.setPen(Qt.GlobalColor.transparent)
            painter.drawEllipse(int(px) - 4, int(py) - 4, 8, 8)