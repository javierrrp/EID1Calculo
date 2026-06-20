from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PyQt6.QtCore import Qt

BG        = "#F8F7F4"
SURFACE   = "#FFFFFF"
SURFACE2  = "#F1EFE8"
BORDER    = "#C8C6BE"
BORDER_STR= "#B0AEA8"

TEXT_PRI  = "#1A1917"
TEXT_SEC  = "#5F5E5A"
TEXT_MUT  = "#9B9A95"

RUT       = "#185FA5"
RUT_LIGHT = "#E6F1FB"
RUT_MID   = "#378ADD"

OK        = "#3B6D11"
OK_LIGHT  = "#EAF3DE"

ERR       = "#993C1D"
ERR_LIGHT = "#FAECE7"
ERR_MID   = "#D85A30"

class VistaConicas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Cónicas")
        self.setMinimumSize(850, 550)

        layout_principal = QHBoxLayout(self)

        panel_izquierdo = QWidget()
        panel_izquierdo.setStyleSheet("background: transparent;")
        layout_izquierdo = QVBoxLayout(panel_izquierdo)
        layout_izquierdo.setContentsMargins(0, 0, 0, 0)
        layout_izquierdo.setSpacing(10)

        self.lbl_titulo = QLabel("Analizando Conica...")
        self.lbl_titulo.setWordWrap(True)
        self.lbl_titulo.setStyleSheet(
            "font-size: 15px; font-weight: 800; color: #0F172A; "
            "background: #F1F5F9; border-radius: 10px; padding: 10px 14px;"
        )

        lbl_proc = QLabel("Desarrollo matemático (General → Canónica):")

        lbl_proc.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_MUT};"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        layout_izquierdo.addWidget(lbl_proc)

        self.txt_procedimiento = QTextEdit()
        self.txt_procedimiento.setReadOnly(True)
        self.txt_procedimiento.setStyleSheet(self._estilo_consola(RUT_MID))
        self.txt_procedimiento.setMinimumHeight(160)
        layout_izquierdo.addWidget(self.txt_procedimiento)

        label_inverso = QLabel("Procedimiento Inverso (Canónica -> General):")
        label_inverso.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_MUT};"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        layout_izquierdo.addWidget(label_inverso)

        self.txt_procedimiento_inverso = QTextEdit()
        self.txt_procedimiento_inverso.setReadOnly(True)
        self.txt_procedimiento_inverso.setStyleSheet(self._estilo_consola(RUT_MID))
        self.txt_procedimiento_inverso.setMinimumHeight(160)
        layout_izquierdo.addWidget(self.txt_procedimiento_inverso)

        layout_izquierdo.addStretch() 
        layout_principal.addWidget(panel_izquierdo, stretch=1)

        # Panel derecho: plano con panel flotante 
        panel_derecho = QWidget()
        panel_derecho.setStyleSheet("background: transparent;")
        layout_derecho = QVBoxLayout(panel_derecho)
        layout_derecho.setContentsMargins(0, 0, 0, 0)
        layout_derecho.setSpacing(6)

        label_ayuda = QLabel("🖱 Arrastra para mover · Rueda para zoom · Completa los campos en la gráfica")
        label_ayuda.setStyleSheet(
            "font-size: 10px; color: #94A3B8; font-style: italic; padding-left: 4px;"
        )
        layout_derecho.addWidget(label_ayuda)
        
        self.plano = PlanoCartesiano()
        self.plano.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout_derecho.addWidget(self.plano)        

        layout_principal.addWidget(panel_derecho, stretch=1)
 
        # Alias para que el controlador siga funcionando 
        # El controlador accede a self.vista.input_centro, etc.
        self.input_centro = self.plano.input_centro
        self.input_radio   = self.plano.input_radio
        self.input_focos   = self.plano.input_focos
        self.btn_verificar = self.plano.btn_verificar 
    
    def _estilo_consola(self, color_borde: str) -> str:
        return (
            f"background-color: {BG}; "
            f"color: {TEXT_SEC}; "
            f"font-family: Consolas, 'Courier New', monospace; "
            f"font-size: 12px; "
            f"line-height: 1.7; "
            f"padding: 14px 16px; "
            f"border-radius: 8px; "
            f"border-left: 3px solid {color_borde};"
        )

class PlanoCartesiano(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(420, 440)
        self.setStyleSheet("background-color: white; border: 2px solid #bdc3c7; border-radius: 8px;")

        # Inicializa variables para el centro de la conica
        self.h = None
        self.k = None
        self.tipo_conica = None
        self.radio = None

        self.offset_x = 0
        self.offset_y = 0
        self.last_mouse_pos = None
        self.separacion = 25

        self.panel_inputs = QFrame(self)

        self.panel_inputs.setObjectName("panel_inputs")
        self.panel_inputs.setStyleSheet("""
                                        QFrame#panel_inputs {
                                            background-color: rgba(255, 255, 255, 200)
                                            border: 1px solid #bdc3c7;
                                            border-radius: 12px;
                                        }
                                    """)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(18)
        sombra.setColor(QColor(15,23,42,40))
        sombra.setOffset(0, 4)
        self.panel_inputs.setGraphicsEffect(sombra)

        lay = QVBoxLayout(self.panel_inputs)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        titulo_panel = QLabel("Controles de Visualización")
        titulo_panel.setStyleSheet(
            "font-size: 11px; font-weight: 800; color: #0F172A; "
            "letter-spacing: 0.4px; background: transparent; border: none;"
        )
        lay.addWidget(titulo_panel)

        self.input_centro = self._hacer_campo(lay, "Centro (h, k):", "Ej: (2, -3)")
        self.input_radio   = self._hacer_campo(lay, "Radio / Semieje:", "Ej: 4.5")
        self.input_focos   = self._hacer_campo(lay, "Focos / Vértices:", "Ej: (1,0) y (-1,0)")
 
        self.btn_verificar = QPushButton("Verificar respuestas")
        self.btn_verificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verificar.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; color: white;
                font-weight: 700; font-size: 12px;
                padding: 7px 10px; border-radius: 8px; border: none;
            }
            QPushButton:hover  { background-color: #2563EB; }
            QPushButton:pressed{ background-color: #1D4ED8; }
        """)
        lay.addWidget(self.btn_verificar)
        self.panel_inputs.adjustSize()
    
    def _hacer_campo(self, parent_lay, etiqueta: str, placeholder: str) -> QLineEdit:
        
        fila_widget = QWidget()
        fila_widget.setStyleSheet("background: transparent; border: none;")
        fila = QHBoxLayout(fila_widget)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(6)

        lbl = QLabel(etiqueta)
        lbl.setFixedWidth(120)
        lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #334155; "
                            "background: transparent; border: none;")
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setFixedHeight(28)
        campo.setStyleSheet("""
            QLineEdit {
                            background-color: #F8FAFC; 
                            border: 1px solid #CBD5E1;
                            border-radius: 6px; 
                            padding: 2px 8px;
                            font-size: 12px;
                            color: #1E293B;
            }
            QLineEdit:focus {
                            border: 1.5px solid #3B82F6;
                            background-color: #FFFFFF;
            }
                            """)
        fila.addWidget(lbl)
        fila.addWidget(campo)
        parent_lay.addWidget(fila_widget)

        campo._fila_widget = fila_widget
        return campo
    
    def mostrar_campos_segun_conica(self, tipo: str):
        
        tipo_lower = tipo.lower()

        if "circunferencia" in tipo_lower:
            visibles = {"centro", "radio"}
        elif "elipse" in tipo_lower:
            visibles = {"centro", "focos"}
        elif "hipérbola" in tipo_lower or "hiperbola" in tipo_lower:
            visibles = {"centro", "focos"}
        elif "parábola" in tipo_lower or "parabola" in tipo_lower:
            visibles = {"focos"}
        else:
            visibles = {"centro", "radio", "focos"}
        
        campos = {
            "centro": self.input_centro,
            "radio":  self.input_radio,
            "focos":  self.input_focos,
        }

        for nombre, campo in campos.items():
            campo._fila_widget.setVisible(nombre in visibles)

        self.panel_inputs.adjustSize()
        self._reposicionar_panel()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposicionar_panel()

    def _reposicionar_panel(self):
        self.panel_inputs.adjustSize()
        margen = 14
        w = self.panel_inputs.width()
        h = self.panel_inputs.height()
        self.panel_inputs.move(self.width() - w - margen,
                               self.height() - h - margen)
 
    def actualizar_figura(self, h, k, tipo=None, radio=None):
        self.h = h
        self.k = k
        self.tipo_conica = tipo
        self.radio = radio
        self.update()

    # Movimiento de grafico
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

            # Dibuja líneas solo si calza con el paso_grilla asignado
            if (val * 10) % (paso_grilla * 10) != 0:
                continue

            px = centro_x + int(val * self.separacion)
            py = centro_y - int(val * self.separacion)
            
            # Formatea el número (quita los ceros a la derecha)
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
        painter.setPen(QPen(QColor(50, 50, 50), 2))
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
