# view/vista_limites.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QGridLayout, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QFont

class LienzoLimites(QWidget):
    """Lienzo matemático manual mediante QPainter para funciones por tramos"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(450, 400)
        # Fondo claro y bordes suaves acorde a la paleta alegre del grupo
        self.setStyleSheet("background-color: #FAF8F5; border-radius: 20px; border: 2px solid #E2E8F0;")
        self.modelo_vinculado = None

    def vincular_modelo(self, modelo):
        self.modelo_vinculado = modelo
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        ancho = self.width()
        alto = self.height()
        centro_x = ancho // 2
        centro_y = alto // 2
        
        # 1. Dibujar Plano Cartesiano (Ejes coordenados)
        pen_ejes = QPen(QColor("#94A3B8"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y) # Eje X
        painter.drawLine(centro_x, 0, centro_x, alto) # Eje Y
        
        # Grilla milimétrica sutil y alegre
        pen_grilla = QPen(QColor("#E2E8F0"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen_grilla)
        escala = 25 # 25 píxeles representan 1 unidad matemática
        
        for i in range(-500, 501, escala):
            if i != 0:
                painter.drawLine(centro_x + i, 0, centro_x + i, alto)
                painter.drawLine(0, centro_y + i, ancho, centro_y + i)

        if not self.modelo_vinculado or not self.modelo_vinculado.dígitos:
            return

        # 2. Trazar la función matemática evaluando píxel por píxel (Algoritmo nativo)
        # Color Amarillo/Celeste alegre para el trazo
        pen_funcion = QPen(QColor("#0EA5E9"), 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen_funcion)
        
        ultimo_punto_valido = None
        
        for px in range(ancho):
            # Convertir posición de píxel a coordenada matemática X
            cx = (px - centro_x) / escala
            cy = self.modelo_vinculado.evaluar_funcion(cx)
            
            if cy is not None:
                # Convertir resultado matemático Y a píxel en pantalla
                py = centro_y - int(cy * escala)
                
                if 0 <= py <= alto:
                    punto_actual = QPointF(px, py)
                    
                    # Romper la línea en el punto crítico 'a' para reflejar saltos o asíntotas
                    if ultimo_punto_valido and abs(cx - self.modelo_vinculado.a) > 0.05:
                        painter.drawLine(ultimo_punto_valido.toPoint(), punto_actual.toPoint())
                    elif ultimo_punto_valido and self.modelo_vinculado.caso == 1:
                        # En caso removible es continuo salvo el vacío
                        painter.drawLine(ultimo_punto_valido.toPoint(), punto_actual.toPoint())
                        
                    ultimo_punto_valido = punto_actual
                else:
                    ultimo_punto_valido = None
            else:
                ultimo_punto_valido = None

        # 3. Decoraciones de límites sobre el punto crítico x = a (Fase 6)
        pix_a = centro_x + int(self.modelo_vinculado.a * escala)
        if 0 <= pix_a <= ancho:
            # Línea segmentada roja de advertencia en el punto de análisis
            pen_asintota = QPen(QColor("#EF4444"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_asintota)
            painter.drawLine(pix_a, 0, pix_a, alto)
            
            painter.setPen(QPen(QColor("#EF4444"), 2))
            if self.modelo_vinculado.caso == 1:
                # Círculo vacío en la discontinuidad removible
                lim_teorico = self.modelo_vinculado.a + self.modelo_vinculado.dígitos[0]
                py_a = centro_y - int(lim_teorico * escala)
                painter.setBrush(QColor("#FAF8F5"))
                painter.drawEllipse(pix_a - 4, py_a - 4, 8, 8)


class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(25)

        # ================= COLUMNA IZQUIERDA: Ecuaciones y Evidencia Numérica =================
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(20)

        # Tarjeta 1: Estructura analítica de la función
        card_funcion = QFrame()
        card_funcion.setStyleSheet("background-color: white; border-radius: 20px; padding: 15px;")
        self.aplicar_sombra(card_funcion)
        
        layout_func = QVBoxLayout(card_funcion)
        self.lbl_caso_titulo = QLabel("MÓDULO DE LÍMITES: ESPERANDO RUT...")
        self.lbl_caso_titulo.setStyleSheet("color: #FFD93D; font-weight: 900; font-size: 14px; letter-spacing: 0.5px;")
        layout_func.addWidget(self.lbl_caso_titulo)
        
        self.lbl_expresion = QLabel("La expresión matemática por tramos aparecerá aquí al validar el RUT.")
        self.lbl_expresion.setStyleSheet("color: #334155; font-size: 13px; font-family: 'Consolas', monospace;")
        self.lbl_expresion.setWordWrap(True)
        layout_func.addWidget(self.lbl_expresion)
        
        panel_izquierdo.addWidget(card_funcion)

        # Tarjeta 2: Tablas de aproximación (Evidencia Computacional)
        card_tabla = QFrame()
        card_tabla.setStyleSheet("background-color: white; border-radius: 20px; padding: 15px;")
        self.aplicar_sombra(card_tabla)
        
        layout_tab = QVBoxLayout(card_tabla)
        lbl_t_titulo = QLabel("EVIDENCIA COMPUTACIONAL (ENTORNO DE APROXIMACIÓN)")
        lbl_t_titulo.setStyleSheet("color: #64748B; font-weight: bold; font-size: 11px;")
        layout_tab.addWidget(lbl_t_titulo)

        self.tabla_limites = QTableWidget(4, 4)
        self.tabla_limites.setHorizontalHeaderLabels(["x → a⁻", "f(x)", "x → a⁺", "f(x)"])
        self.tabla_limites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_limites.setStyleSheet("QTableWidget { background-color: #F8FAFC; border-radius: 10px; font-size: 11px; }")
        layout_tab.addWidget(self.tabla_limites)
        
        panel_izquierdo.addWidget(card_tabla)

        # ================= COLUMNA CENTRAL: Campos Vacíos Obligatorios para Defensa =================
        card_defensa = QFrame()
        card_defensa.setStyleSheet("background-color: white; border-radius: 20px; padding: 20px;")
        self.aplicar_sombra(card_defensa)
        
        layout_def = QVBoxLayout(card_defensa)
        lbl_d_titulo = QLabel("PANEL DE EVALUACIÓN ORAL (COMPLETAR EN EL EXAMEN)")
        lbl_d_titulo.setStyleSheet("color: #64748B; font-weight: 800; font-size: 11px; letter-spacing: 0.5px;")
        layout_def.addWidget(lbl_d_titulo)

        grid_inputs = QGridLayout()
        grid_inputs.setSpacing(12)

        # Entradas inicialmente vacías según exige la rúbrica del PDF
        self.input_lim_izq = self.crear_campo_vacio("Límite por izquierda")
        self.input_lim_der = self.crear_campo_vacio("Límite por derecha")
        self.input_existencia = self.crear_campo_vacio("¿Existe el límite? (Sí/No)")
        self.input_imagen = self.crear_campo_vacio("Valor de f(a)")
        self.input_continuidad = self.crear_campo_vacio("¿Es continua en x=a? (Sí/No)")
        self.input_tipo_disc = self.crear_campo_vacio("Tipo de discontinuidad")
        self.input_justificacion = self.crear_campo_vacio("Justificación formal")

        grid_inputs.addWidget(QLabel("<b>Límite Izquierdo:</b>"), 0, 0)
        grid_inputs.addWidget(self.input_lim_izq, 0, 1)
        grid_inputs.addWidget(QLabel("<b>Límite Derecho:</b>"), 1, 0)
        grid_inputs.addWidget(self.input_lim_der, 1, 1)
        grid_inputs.addWidget(QLabel("<b>Conclusión Límite:</b>"), 2, 0)
        grid_inputs.addWidget(self.input_existencia, 2, 1)
        grid_inputs.addWidget(QLabel("<b>Imagen f(a):</b>"), 3, 0)
        grid_inputs.addWidget(self.input_imagen, 3, 1)
        grid_inputs.addWidget(QLabel("<b>Continuidad:</b>"), 4, 0)
        grid_inputs.addWidget(self.input_continuidad, 4, 1)
        grid_inputs.addWidget(QLabel("<b>Discontinuidad:</b>"), 5, 0)
        grid_inputs.addWidget(self.input_tipo_disc, 5, 1)
        grid_inputs.addWidget(QLabel("<b>Justificación:</b>"), 6, 0)
        grid_inputs.addWidget(self.input_justificacion, 6, 1)

        layout_def.addLayout(grid_inputs)

        self.btn_validar_respuestas = QPushButton("VERIFICAR RESPUESTAS DE LA DEFENSA")
        self.btn_validar_respuestas.setMinimumHeight(40)
        self.btn_validar_respuestas.setStyleSheet("""
            QPushButton { background-color: #FFD93D; color: #1E293B; border-radius: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #E2BF30; }
        """)
        self.btn_validar_respuestas.clicked.connect(self.evaluar_respuestas_estudiante)
        layout_def.addWidget(self.btn_validar_respuestas)

        # ================= COLUMNA DERECHA: Gráfico de Traza =================
        panel_grafico = QVBoxLayout()
        lbl_g_titulo = QLabel("REPRESENTACIÓN GRÁFICA ASOCIADA (TRAZA MATEMÁTICA)")
        lbl_g_titulo.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11px;")
        panel_grafico.addWidget(lbl_g_titulo)
        
        self.lienzo_grafico = LienzoLimites()
        panel_grafico.addWidget(self.lienzo_grafico)

        # Integrar las tres columnas en la interfaz dinámica
        layout_principal.addLayout(panel_izquierdo, 3)
        layout_principal.addLayout(layout_def, 4)
        layout_principal.addLayout(panel_grafico, 4)

    def crear_campo_vacio(self, placeholder):
        txt = QLineEdit()
        txt.setPlaceholderText(placeholder)
        txt.setMinimumHeight(32)
        txt.setStyleSheet("""
            QLineEdit { border: 2px solid #F1F5F9; border-radius: 8px; padding-left: 8px; color: #1E293B; background-color: #F8FAFC; }
            QLineEdit:focus { border: 2px solid #FFD93D; background-color: white; }
        """)
        return txt

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(0, 0, 0, 12))
        sombra.setOffset(0, 6)
        widget.setGraphicsEffect(sombra)

    def mostrar_datos_modulo_limites(self, modelo):
        """Método de inyección para el controlador. Actualiza textos, tabla y gatilla redibujo."""
        self.lbl_caso_titulo.setText(f"MÓDULO DE LÍMITES: {modelo.nombre_caso.upper()}")
        
        a = modelo.a
        d1, d2, d4, d5 = modelo.dígitos[0], modelo.dígitos[1], modelo.dígitos[3], modelo.dígitos[4]

        if modelo.caso == 1:
            texto_f = f"f(x) = [ (x - {a})(x + {d1}) ] / (x - {a})  |  Si x ≠ {a}"
        elif modelo.caso == 2:
            texto_f = f"f(x) = \n Tramo 1: x + {d2}  si x < {a}\n Tramo 2: x + {d4}  si x ≥ {a}"
        else:
            texto_f = f"f(x) = ({d5} + 1) / (x - {a})  |  Punto crítico en x = {a}"

        self.lbl_expresion.setText(texto_f)

        # Poblar tabla de aproximación con los cálculos del modelo
        t_izq, t_der = modelo.generar_tabla_valores()
        for i in range(4):
            self.tabla_limites.setItem(i, 0, QTableWidgetItem(f"{t_izq[i][0]:.3f}"))
            val_y_izq = "Indef" if t_izq[i][1] is None else f"{t_izq[i][1]:.3f}"
            self.tabla_limites.setItem(i, 1, QTableWidgetItem(val_y_izq))
            
            self.tabla_limites.setItem(i, 2, QTableWidgetItem(f"{t_der[i][0]:.3f}"))
            val_y_der = "Indef" if t_der[i][1] is None else f"{t_der[i][1]:.3f}"
            self.tabla_limites.setItem(i, 3, QTableWidgetItem(val_y_der))

        # Limpiar obligatoriamente las entradas para la evaluación en vivo
        self.input_lim_izq.clear()
        self.input_lim_der.clear()
        self.input_existencia.clear()
        self.input_imagen.clear()
        self.input_continuidad.clear()
        self.input_tipo_disc.clear()
        self.input_justificacion.clear()

        # Gatillar actualización del gráfico personalizado
        self.lienzo_grafico.vincular_modelo(modelo)

    def evaluar_respuestas_estudiante(self):
        if not self.lienzo_grafico.modelo_vinculado:
            return