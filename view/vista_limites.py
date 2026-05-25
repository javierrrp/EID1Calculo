# view/vista_limites.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGraphicsDropShadowEffect, QLineEdit, QComboBox, QScrollArea)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QWheelEvent, QFont

class LienzoLimites(QWidget):
    """Lienzo matemático manual mediante QPainter con soporte de Zoom interactivo y números en los ejes"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(550, 500)
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 2px solid #E2E8F0;")
        self.modelo_vinculado = None
        self.escala_base = 28  
        self.factor_zoom = 1.0  

    def vincular_modelo(self, modelo):
        self.modelo_vinculado = modelo
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.factor_zoom = min(5.0, self.factor_zoom + 0.1)
        else:
            self.factor_zoom = max(0.4, self.factor_zoom - 0.1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        ancho = self.width()
        alto = self.height()
        centro_x = ancho // 2
        centro_y = alto // 2
        
        escala = int(self.escala_base * self.factor_zoom)
        if escala < 5: 
            escala = 5

        # Configurar fuente estilizada para los números de los ejes
        fuente_ejes = QFont("Segoe UI", 8)
        painter.setFont(fuente_ejes)

        # 1. Cuadrícula de Fondo de Ingeniería e Inicialización de Números
        pen_grilla = QPen(QColor("#F1F5F9"), 1, Qt.PenStyle.SolidLine)
        pen_texto = QPen(QColor("#94A3B8")) # Color gris elegante para los números
        
        painter.setPen(pen_grilla)
        limite_grilla = max(ancho, alto)
        
        # Saltos dinámicos en los números según el nivel de zoom (para que no se amontonen)
        paso_unidades = 1
        if escala < 12:
            paso_unidades = 5
        elif escala < 20:
            paso_unidades = 2

        # Dibujar líneas horizontales y verticales de la cuadrícula
        for i in range(-limite_grilla, limite_grilla, escala):
            if i != 0:
                painter.setPen(pen_grilla)
                painter.drawLine(centro_x + i, 0, centro_x + i, alto)
                painter.drawLine(0, centro_y + i, ancho, centro_y + i)

        # 2. Ejes Cartesianos Principales
        pen_ejes = QPen(QColor("#CBD5E1"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y)
        painter.drawLine(centro_x, 0, centro_x, alto)

        # 3. Renderizar los números en el eje X y eje Y de manera adaptativa
        painter.setPen(pen_texto)
        
        # Números Eje X
        max_unidades_x = centro_x // escala + 1
        for u in range(-max_unidades_x, max_unidades_x + 1):
            if u == 0:
                continue
            if u % paso_unidades == 0:
                pos_x = centro_x + (u * escala)
                # Pequeña marca visual (tick) en el eje
                painter.drawLine(pos_x, centro_y - 3, pos_x, centro_y + 3)
                # Dibujar el texto numérico centrado debajo del eje
                painter.drawText(pos_x - 12, centro_y + 16, f"{u}")

        # Números Eje Y
        max_unidades_y = centro_y // escala + 1
        for u in range(-max_unidades_y, max_unidades_y + 1):
            if u == 0:
                continue
            if u % paso_unidades == 0:
                pos_y = centro_y - (u * escala)
                # Pequeña marca visual (tick) en el eje
                painter.drawLine(centro_x - 3, pos_y, centro_x + 3, pos_y)
                # Dibujar el texto numérico a la izquierda del eje
                painter.drawText(centro_x - 22, pos_y + 4, f"{u}")
                
        if not self.modelo_vinculado or not self.modelo_vinculado.dígitos:
            return

        # 4. Trazado de la Función Matemática (Sky Blue Premium)
        pen_funcion = QPen(QColor("#0EA5E9"), 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen_funcion)
        ultimo_punto_valido = None
        margen_renderizado = alto * 2
        
        for px in range(ancho):
            cx = (px - centro_x) / escala
            cy = self.modelo_vinculado.evaluar_funcion(cx)
            
            if cy is not None:
                py = centro_y - int(cy * escala)
                if -margen_renderizado <= py <= alto + margen_renderizado:
                    punto_actual = QPointF(px, py)
                    if ultimo_punto_valido:
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

        # 5. Línea de Punto Crítico y Nodos Estilizados (Rose/Red Soft)
        pix_a = centro_x + int(self.modelo_vinculado.a * escala)
        if 0 <= pix_a <= ancho:
            pen_asintota = QPen(QColor("#FDA4AF"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_asintota)
            painter.drawLine(pix_a, 0, pix_a, alto)
            
            painter.setPen(QPen(QColor("#F43F5E"), 2))
            if self.modelo_vinculado.caso == 1:
                lim_teorico = self.modelo_vinculado.a + self.modelo_vinculado.dígitos[0]
                py_a = centro_y - int(lim_teorico * escala)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawEllipse(pix_a - 5, py_a - 5, 10, 10)
                
            elif self.modelo_vinculado.caso == 2:
                d2 = self.modelo_vinculado.dígitos[1]
                d4 = self.modelo_vinculado.dígitos[3]
                py_izq = centro_y - int((self.modelo_vinculado.a + d2) * escala)
                py_der = centro_y - int((self.modelo_vinculado.a + d4) * escala)
                
                if 0 <= py_izq <= alto:
                    painter.setBrush(QBrush(QColor("#FFFFFF")))
                    painter.drawEllipse(pix_a - 5, py_izq - 5, 10, 10)
                if 0 <= py_der <= alto:
                    painter.setBrush(QBrush(QColor("#F43F5E")))
                    painter.drawEllipse(pix_a - 5, py_der - 5, 10, 10)


class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.modelo_actual = None
        self.init_ui()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(24, 24, 24, 24)
        layout_principal.setSpacing(30)

        # ================= COLUMNA IZQUIERDA: ÁREA CON SCROLL ADAPTATIVO =================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenedor_izquierdo = QWidget()
        contenedor_izquierdo.setStyleSheet("background: transparent;")
        panel_izquierdo = QVBoxLayout(contenedor_izquierdo)
        panel_izquierdo.setContentsMargins(0, 0, 12, 0)
        panel_izquierdo.setSpacing(20)

        # Tarjeta 1: Expresión Algebraica Dinámica
        card_funcion = QFrame()
        card_funcion.setStyleSheet("background-color: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0;")
        self.aplicar_sombra(card_funcion)
        
        layout_func = QVBoxLayout(card_funcion)
        layout_func.setContentsMargins(20, 20, 20, 20)
        layout_func.setSpacing(12)
        
        self.lbl_caso_titulo = QLabel("MÓDULO DE LÍMITES: ESPERANDO RUT")
        self.lbl_caso_titulo.setStyleSheet("color: #0F172A; font-weight: 800; font-size: 14px; letter-spacing: 0.5px;")
        
        self.lbl_expresion = QLabel("Ingrese un RUT válido en la pestaña inicial para cargar el modelo matemático por tramos.")
        self.lbl_expresion.setMinimumHeight(75)
        self.lbl_expresion.setStyleSheet("""
            QLabel {
                color: #334155; 
                font-size: 13px; 
                font-family: 'Consolas', monospace; 
                background-color: #F8FAFC; 
                padding: 16px; 
                border-radius: 10px; 
                border: 1px solid #F1F5F9;
            }
        """)
        self.lbl_expresion.setWordWrap(True)
        
        layout_func.addWidget(self.lbl_caso_titulo)
        layout_func.addWidget(self.lbl_expresion)
        panel_izquierdo.addWidget(card_funcion)

        # Tarjeta 2: Tabla de Evidencia Computacional
        card_tabla = QFrame()
        card_tabla.setStyleSheet("background-color: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0;")
        self.aplicar_sombra(card_tabla)
        
        layout_tab = QVBoxLayout(card_tabla)
        layout_tab.setContentsMargins(20, 20, 20, 20)
        layout_tab.setSpacing(12)
        
        lbl_t_titulo = QLabel("EVIDENCIA COMPUTACIONAL LATERAL")
        lbl_t_titulo.setStyleSheet("color: #64748B; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;")
        
        self.tabla_limites = QTableWidget(4, 4)
        self.tabla_limites.setHorizontalHeaderLabels(["x → a⁻", "f(x) Izq", "x → a⁺", "f(x) Der"])
        self.tabla_limites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_limites.setStyleSheet("""
            QTableWidget { 
                background-color: #FFFFFF; 
                border-radius: 8px; 
                border: 1px solid #E2E8F0;
                font-size: 12px; 
                color: #334155;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                padding: 8px;
                font-weight: 700;
                border-bottom: 1px solid #E2E8F0;
                border-right: none;
                color: #475569;
            }
        """)
        self.tabla_limites.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_limites.setFixedHeight(150)
        
        layout_tab.addWidget(lbl_t_titulo)
        layout_tab.addWidget(self.tabla_limites)
        panel_izquierdo.addWidget(card_tabla)

        # Tarjeta 3: Zona Interactiva (Defensa de Evaluación Oral)
        card_defensa = QFrame()
        card_defensa.setStyleSheet("background-color: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0;")
        self.aplicar_sombra(card_defensa)
        
        layout_defensa = QVBoxLayout(card_defensa)
        layout_defensa.setContentsMargins(20, 20, 20, 20)
        layout_defensa.setSpacing(14)
        
        lbl_defensa_titulo = QLabel("ZONA DE DEFENSA EVALUATIVA")
        lbl_defensa_titulo.setStyleSheet("color: #0F172A; font-weight: 800; font-size: 11px; letter-spacing: 0.5px;")
        layout_defensa.addWidget(lbl_defensa_titulo)

        # Input de Límite L
        layout_limite = QHBoxLayout()
        lbl_res_limite = QLabel("Valor Límite (L):")
        lbl_res_limite.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")
        self.input_limite_defensa = QLineEdit()
        self.input_limite_defensa.setPlaceholderText("Ej: 8  o  No existe")
        self.input_limite_defensa.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC; border: 1px solid #E2E8F0; 
                padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #1E293B;
            }
            QLineEdit:focus { border: 1px solid #0EA5E9; background-color: #FFFFFF; }
        """)
        layout_limite.addWidget(lbl_res_limite)
        layout_limite.addWidget(self.input_limite_defensa)
        layout_defensa.addLayout(layout_limite)

        # ComboBox de Continuidad Analítica
        layout_concl = QHBoxLayout()
        lbl_res_concl = QLabel("Clasificación:")
        lbl_res_concl.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")
        self.combo_continuidad = QComboBox()
        self.combo_continuidad.addItems([
            "[ Seleccione su conclusión ]", 
            "La función es Continua en x = a", 
            "Discontinuidad Evitable / Removible (REI)", 
            "Discontinuidad Esencial de Salto Finito", 
            "Discontinuidad Asintótica / Infinita"
        ])
        self.combo_continuidad.setStyleSheet("""
            QComboBox {
                background-color: #F8FAFC; border: 1px solid #E2E8F0; 
                padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #1E293B;
            }
            QComboBox::drop-down { border: none; }
            QComboBox:focus { border: 1px solid #0EA5E9; background-color: #FFFFFF; }
        """)
        layout_concl.addWidget(lbl_res_concl)
        layout_concl.addWidget(self.combo_continuidad)
        layout_defensa.addLayout(layout_concl)

        # Barra de Feedback Premium de Autovalidación
        self.lbl_validacion = QLabel("Esperando respuestas...")
        self.lbl_validacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_validacion.setStyleSheet("""
            background-color: #F1F5F9; color: #475569; 
            font-weight: 700; font-size: 13px; 
            padding: 12px; border-radius: 10px; margin-top: 5px;
        """)
        layout_defensa.addWidget(self.lbl_validacion)

        self.input_limite_defensa.textChanged.connect(self.ejecutar_autovalidacion)
        self.combo_continuidad.currentIndexChanged.connect(self.ejecutar_autovalidacion)

        panel_izquierdo.addWidget(card_defensa)
        scroll_area.setWidget(contenedor_izquierdo)
        
        # ================= COLUMNA DERECHA: VISUALIZACIÓN GRÁFICA INTERACTIVA =================
        panel_grafico = QVBoxLayout()
        panel_grafico.setSpacing(12)
        
        lbl_g_titulo = QLabel("REPRESENTACIÓN GRÁFICA INTERACTIVA (ZOOM CON RUEDA DEL MOUSE)")
        lbl_g_titulo.setStyleSheet("color: #475569; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;")
        
        self.lienzo_grafico = LienzoLimites()
        self.aplicar_sombra(self.lienzo_grafico)
        
        panel_grafico.addWidget(lbl_g_titulo)
        panel_grafico.addWidget(self.lienzo_grafico)

        layout_principal.addWidget(scroll_area, 4)
        layout_principal.addLayout(panel_grafico, 6)

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(16)
        sombra.setColor(QColor(15, 23, 42, 18))  
        sombra.setOffset(0, 4)
        widget.setGraphicsEffect(sombra)

    def mostrar_datos_modulo_limites(self, modelo):
        self.modelo_actual = modelo  
        self.lbl_caso_titulo.setText(f"MÓDULO DE LÍMITES: {modelo.nombre_caso.upper()}")
        a = modelo.a
        d1, d2, d4, d5 = modelo.dígitos[0], modelo.dígitos[1], modelo.dígitos[3], modelo.dígitos[4]

        if modelo.caso == 1:
            texto_f = f"f(x) = [ (x - {a})(x + {d1}) ] / (x - {a})   |   Si x ≠ {a}"
        elif modelo.caso == 2:
            texto_f = f"f(x) =\n• Tramo 1: x + {d2}   si x < {a}\n• Tramo 2: x + {d4}   si x ≥ {a}"
        else:
            texto_f = f"f(x) = ({d5} + 1) / (x - {a})   |   Asíntota vertical en x = {a}"

        self.lbl_expresion.setText(texto_f)
        
        self.input_limite_defensa.clear()
        self.combo_continuidad.setCurrentIndex(0)
        self.lbl_validacion.setText("Esperando respuestas para el nuevo caso...")
        self.lbl_validacion.setStyleSheet("background-color: #F1F5F9; color: #475569; font-weight: bold; font-size: 13px; padding: 12px; border-radius: 10px;")
        
        self.tabla_limites.clearContents()

        t_izq, t_der = modelo.generar_tabla_valores()
        for i in range(4):
            self.tabla_limites.setItem(i, 0, QTableWidgetItem(f"{t_izq[i][0]:.4f}"))
            val_y_izq = "Indefinido" if t_izq[i][1] is None else f"{t_izq[i][1]:.4f}"
            self.tabla_limites.setItem(i, 1, QTableWidgetItem(val_y_izq))
            
            self.tabla_limites.setItem(i, 2, QTableWidgetItem(f"{t_der[i][0]:.4f}"))
            val_y_der = "Indefinido" if t_der[i][1] is None else f"{t_der[i][1]:.4f}"
            self.tabla_limites.setItem(i, 3, QTableWidgetItem(val_y_der))

        self.lienzo_grafico.vincular_modelo(modelo)

    def ejecutar_autovalidacion(self):
        if not self.modelo_actual:
            return

        texto_limite = self.input_limite_defensa.text().strip().lower()
        indice_combobox = self.combo_continuidad.currentIndex()

        if not texto_limite or indice_combobox == 0:
            self.lbl_validacion.setText("Por favor, completa ambos campos para verificar.")
            self.lbl_validacion.setStyleSheet("background-color: #FEF3C7; color: #D97706; font-weight: bold; font-size: 13px; padding: 12px; border-radius: 10px;")
            return

        limite_esperado_correcto = False
        caso_esperado_correcto = False

        if self.modelo_actual.caso == 1:
            valor_real_l = self.modelo_actual.a + self.modelo_actual.dígitos[0]
            caso_esperado_correcto = (indice_combobox == 2)
            try:
                limite_esperado_correcto = abs(float(texto_limite) - valor_real_l) < 0.01
            except ValueError:
                limite_esperado_correcto = False

        elif self.modelo_actual.caso == 2:
            caso_esperado_correcto = (indice_combobox == 3)
            limite_esperado_correcto = ("no existe" in texto_limite or "no" in texto_limite)

        elif self.modelo_actual.caso == 3:
            caso_esperado_correcto = (indice_combobox == 4)
            limite_esperado_correcto = ("no existe" in texto_limite or "infinito" in texto_limite or "no" in texto_limite)

        if limite_esperado_correcto and caso_esperado_correcto:
            self.lbl_validacion.setText("✓ ANÁLISIS CORRECTO: ¡Excelente defensa matemática!")
            self.lbl_validacion.setStyleSheet("background-color: #DCFCE7; color: #166534; font-weight: bold; font-size: 13px; padding: 12px; border-radius: 10px; border: 1px solid #BBF7D0;")
        else:
            self.lbl_validacion.setText("✗ ANÁLISIS INCORRECTO: Revisa la gráfica o las aproximaciones.")
            self.lbl_validacion.setStyleSheet("background-color: #FEE2E2; color: #991B1B; font-weight: bold; font-size: 13px; padding: 12px; border-radius: 10px; border: 1px solid #FCA5A5;")