
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QWheelEvent

class LienzoLimites(QWidget):
    """Lienzo matemático manual mediante QPainter con soporte de Zoom interactivo"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 450)
        self.setStyleSheet("background-color: #FAF8F5; border-radius: 20px; border: 2px solid #E2E8F0;")
        self.modelo_vinculado = None
        
        # Parámetros dinámicos de escala y zoom
        self.escala_base = 25  # Píxeles por unidad en tamaño normal
        self.factor_zoom = 1.0  # Multiplicador inicial (1.0 = 100%)

    def vincular_modelo(self, modelo):
        self.modelo_vinculado = modelo
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        """Captura el desplazamiento de la rueda del mouse para ajustar el zoom"""
        delta = event.angleDelta().y()
        
        if delta > 0:
            # Scroll arriba: Acercar (Máximo 5x de ampliación)
            self.factor_zoom = min(5.0, self.factor_zoom + 0.1)
        else:
            # Scroll abajo: Alejar (Mínimo 0.4x de alejamiento)
            self.factor_zoom = max(0.4, self.factor_zoom - 0.1)
            
        self.update()  # Redibuja el plano cartesiano inmediatamente con la nueva escala

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        ancho = self.width()
        alto = self.height()
        centro_x = ancho // 2
        centro_y = alto // 2
        
        # Calcular la escala ajustada por el nivel de zoom actual
        escala = int(self.escala_base * self.factor_zoom)
        if escala < 5: 
            escala = 5  # Evita errores geométricos por dimensiones ínfimas

        # 1. Dibujar Plano Cartesiano Ejes Principales
        pen_ejes = QPen(QColor("#94A3B8"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y) # Eje X
        painter.drawLine(centro_x, 0, centro_x, alto)  # Eje Y
        
        # Dibujar Cuadrícula de Fondo Adaptativa
        pen_grilla = QPen(QColor("#E2E8F0"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen_grilla)
        
        # El rango se expande dinámicamente para cubrir toda el área visible con zoom
        limite_grilla = max(ancho, alto)
        for i in range(-limite_grilla, limite_grilla, escala):
            if i != 0:
                painter.drawLine(centro_x + i, 0, centro_x + i, alto)
                painter.drawLine(0, centro_y + i, ancho, centro_y + i)

        if not self.modelo_vinculado or not self.modelo_vinculado.dígitos:
            return

        # 2. Trazar la función matemática calculada
        pen_funcion = QPen(QColor("#0EA5E9"), 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen_funcion)
        ultimo_punto_valido = None
        
        for px in range(ancho):
            # Mapeo inverso: de coordenadas de píxel de la pantalla a valores matemáticos 'x'
            cx = (px - centro_x) / escala
            cy = self.modelo_vinculado.evaluar_funcion(cx)
            
            if cy is not None:
                # Mapeo directo: de valor matemático 'y' a coordenada de píxel en la pantalla
                py = centro_y - int(cy * escala)
                if 0 <= py <= alto:
                    punto_actual = QPointF(px, py)
                    if ultimo_punto_valido:
                        # Control de rupturas asintóticas escalables para evitar uniones lineales erróneas
                        umbral_ruptura = 0.08 / self.factor_zoom
                        if self.modelo_vinculado.caso == 2 and abs(cx - self.modelo_vinculado.a) < umbral_ruptura:
                            ultimo_punto_valido = None
                        elif self.modelo_vinculado.caso == 3 and abs(cx - self.modelo_vinculado.a) < (0.1 / self.factor_zoom):
                            ultimo_punto_valido = None
                        else:
                            painter.drawLine(ultimo_punto_valido.toPoint(), punto_actual.toPoint())
                    ultimo_punto_valido = punto_actual
                else:
                    ultimo_punto_valido = None
            else:
                ultimo_punto_valido = None

        # 3. Decoraciones Analíticas e Hitos (Asíntotas y puntos abiertos/cerrados)
        pix_a = centro_x + int(self.modelo_vinculado.a * escala)
        if 0 <= pix_a <= ancho:
            # Dibujar línea de la asíntota/discontinuidad (Línea segmentada roja)
            pen_asintota = QPen(QColor("#EF4444"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_asintota)
            painter.drawLine(pix_a, 0, pix_a, alto)
            
            painter.setPen(QPen(QColor("#EF4444"), 2))
            if self.modelo_vinculado.caso == 1:
                # Caso 1: Punto abierto (evitable)
                lim_teorico = self.modelo_vinculado.a + self.modelo_vinculado.dígitos[0]
                py_a = centro_y - int(lim_teorico * escala)
                painter.setBrush(QBrush(QColor("#FAF8F5"))) # Fondo del lienzo para simular vacío
                painter.drawEllipse(pix_a - 4, py_a - 4, 8, 8)
            elif self.modelo_vinculado.caso == 2:
                # Caso 2: Discontinuidad de salto (Punto abierto y punto cerrado)
                d2 = self.modelo_vinculado.dígitos[1]
                d4 = self.modelo_vinculado.dígitos[3]
                py_izq = centro_y - int((self.modelo_vinculado.a + d2) * escala)
                py_der = centro_y - int((self.modelo_vinculado.a + d4) * escala)
                
                # Extremo izquierdo abierto
                painter.setBrush(QBrush(QColor("#FAF8F5")))
                painter.drawEllipse(pix_a - 4, py_izq - 4, 8, 8)
                
                # Extremo derecho cerrado
                painter.setBrush(QBrush(QColor("#EF4444")))
                painter.drawEllipse(pix_a - 4, py_der - 4, 8, 8)


class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Layout principal estructurado en dos columnas equilibradas (50% - 50%)
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # ================= COLUMNA IZQUIERDA: CÁLCULOS Y ANÁLISIS =================
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(20)

        # Tarjeta 1: Expresión Algebraica Dinámica
        card_funcion = QFrame()
        card_funcion.setStyleSheet("background-color: white; border-radius: 20px; padding: 20px;")
        self.aplicar_sombra(card_funcion)
        
        layout_func = QVBoxLayout(card_funcion)
        self.lbl_caso_titulo = QLabel("MÓDULO DE LÍMITES: ESPERANDO RUT...")
        self.lbl_caso_titulo.setStyleSheet("color: #E2BF30; font-weight: 900; font-size: 15px; letter-spacing: 1px;")
        
        self.lbl_expresion = QLabel("La expresión analítica por tramos se desplegará al validar un RUT en la primera pestaña.")
        self.lbl_expresion.setStyleSheet("color: #475569; font-size: 13px; font-family: 'Consolas', monospace; background-color: #F8FAFC; padding: 12px; border-radius: 10px; border: 1px solid #E2E8F0;")
        self.lbl_expresion.setWordWrap(True)
        
        layout_func.addWidget(self.lbl_caso_titulo)
        layout_func.addWidget(self.lbl_expresion)
        panel_izquierdo.addWidget(card_funcion)

        # Tarjeta 2: Tabla de Evidencia Computacional
        card_tabla = QFrame()
        card_tabla.setStyleSheet("background-color: white; border-radius: 20px; padding: 20px;")
        self.aplicar_sombra(card_tabla)
        
        layout_tab = QVBoxLayout(card_tabla)
        lbl_t_titulo = QLabel("EVIDENCIA COMPUTACIONAL (ENTORNO DE APROXIMACIÓN NUMÉRICA)")
        lbl_t_titulo.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        
        self.tabla_limites = QTableWidget(4, 4)
        self.tabla_limites.setHorizontalHeaderLabels(["x → a⁻", "f(x)", "x → a⁺", "f(x)"])
        self.tabla_limites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_limites.setStyleSheet("""
            QTableWidget { 
                background-color: #F8FAFC; 
                border-radius: 12px; 
                border: 1px solid #E2E8F0;
                font-size: 12px; 
                color: #1E293B;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                padding: 6px;
                font-weight: bold;
                border: none;
                color: #475569;
            }
        """)
        self.tabla_limites.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout_tab.addWidget(lbl_t_titulo)
        layout_tab.addWidget(self.tabla_limites)
        panel_izquierdo.addWidget(card_tabla)
        
        # ================= COLUMNA DERECHA: VISUALIZACIÓN GRÁFICA =================
        panel_grafico = QVBoxLayout()
        panel_grafico.setSpacing(10)
        
        lbl_g_titulo = QLabel("REPRESENTACIÓN GRÁFICA ASOCIADA (MUEVA LA RUEDA DEL MOUSE PARA HACER ZOOM)")
        lbl_g_titulo.setStyleSheet("color: #475569; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;")
        
        self.lienzo_grafico = LienzoLimites()
        self.aplicar_sombra(self.lienzo_grafico)
        
        panel_grafico.addWidget(lbl_g_titulo)
        panel_grafico.addWidget(self.lienzo_grafico)

        # Inyectar ambas columnas al contenedor principal
        layout_principal.addLayout(panel_izquierdo, 1)
        layout_principal.addLayout(panel_grafico, 1)

    def aplicar_sombra(self, widget):
        """Añade un efecto visual difuminado de elevación profesional"""
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(15, 23, 42, 25))
        sombra.setOffset(0, 6)
        widget.setGraphicsEffect(sombra)

    def mostrar_datos_modulo_limites(self, modelo):
        """Actualiza las etiquetas, la tabla y gatilla el re-renderizado del lienzo"""
        self.lbl_caso_titulo.setText(f"MÓDULO DE LÍMITES: {modelo.nombre_caso.upper()}")
        a = modelo.a
        d1, d2, d4, d5 = modelo.dígitos[0], modelo.dígitos[1], modelo.dígitos[3], modelo.dígitos[4]

        if modelo.caso == 1:
            texto_f = f"f(x) = [ (x - {a})(x + {d1}) ] / (x - {a})   |   Si x ≠ {a}"
        elif modelo.caso == 2:
            texto_f = f"f(x) = \n• Tramo 1: x + {d2}   si x < {a}\n• Tramo 2: x + {d4}   si x ≥ {a}"
        else:
            texto_f = f"f(x) = ({d5} + 1) / (x - {a})   |   Punto crítico (asíntota) en x = {a}"

        self.lbl_expresion.setText(texto_f)
        self.tabla_limites.clearContents()

        # Cargar los entornos computacionales numéricos provistos por el modelo
        t_izq, t_der = modelo.generar_tabla_valores()
        for i in range(4):
            self.tabla_limites.setItem(i, 0, QTableWidgetItem(f"{t_izq[i][0]:.4f}"))
            val_y_izq = "Indefinido" if t_izq[i][1] is None else f"{t_izq[i][1]:.4f}"
            self.tabla_limites.setItem(i, 1, QTableWidgetItem(val_y_izq))
            
            self.tabla_limites.setItem(i, 2, QTableWidgetItem(f"{t_der[i][0]:.4f}"))
            val_y_der = "Indefinido" if t_der[i][1] is None else f"{t_der[i][1]:.4f}"
            self.tabla_limites.setItem(i, 3, QTableWidgetItem(val_y_der))

        # Enviar el modelo recalculado al lienzo y forzar la ejecución de paintEvent
        self.lienzo_grafico.vincular_modelo(modelo)