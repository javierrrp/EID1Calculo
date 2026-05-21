from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QGraphicsDropShadowEffect, QLineEdit, QComboBox)
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

        # 1. Dibujar Plano Cartesiano Ejes Principales
        pen_ejes = QPen(QColor("#94A3B8"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_ejes)
        painter.drawLine(0, centro_y, ancho, centro_y)
        painter.drawLine(centro_x, 0, centro_x, alto)
        
        # Dibujar Cuadrícula de Fondo Adaptativa
        pen_grilla = QPen(QColor("#E2E8F0"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen_grilla)
        
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
            cx = (px - centro_x) / escala
            cy = self.modelo_vinculado.evaluar_funcion(cx)
            
            if cy is not None:
                py = centro_y - int(cy * escala)
                if 0 <= py <= alto:
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

        # 3. Decoraciones Analíticas e Hitos
        pix_a = centro_x + int(self.modelo_vinculado.a * escala)
        if 0 <= pix_a <= ancho:
            pen_asintota = QPen(QColor("#EF4444"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_asintota)
            painter.drawLine(pix_a, 0, pix_a, alto)
            
            painter.setPen(QPen(QColor("#EF4444"), 2))
            if self.modelo_vinculado.caso == 1:
                lim_teorico = self.modelo_vinculado.a + self.modelo_vinculado.dígitos[0]
                py_a = centro_y - int(lim_teorico * escala)
                painter.setBrush(QBrush(QColor("#FAF8F5")))
                painter.drawEllipse(pix_a - 4, py_a - 4, 8, 8)
            elif self.modelo_vinculado.caso == 2:
                d2 = self.modelo_vinculado.dígitos[1]
                d4 = self.modelo_vinculado.dígitos[3]
                py_izq = centro_y - int((self.modelo_vinculado.a + d2) * escala)
                py_der = centro_y - int((self.modelo_vinculado.a + d4) * escala)
                
                painter.setBrush(QBrush(QColor("#FAF8F5")))
                painter.drawEllipse(pix_a - 4, py_izq - 4, 8, 8)
                
                painter.setBrush(QBrush(QColor("#EF4444")))
                painter.drawEllipse(pix_a - 4, py_der - 4, 8, 8)


class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.modelo_actual = None # Almacenará la referencia del modelo activo para validar
        self.init_ui()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(25)

        # ================= COLUMNA IZQUIERDA: CÁLCULOS Y ANÁLISIS =================
        panel_izquierdo = QVBoxLayout()
        panel_izquierdo.setSpacing(15)

        # Tarjeta 1: Expresión Algebraica Dinámica
        card_funcion = QFrame()
        card_funcion.setStyleSheet("background-color: white; border-radius: 20px; padding: 15px;")
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
        card_tabla.setStyleSheet("background-color: white; border-radius: 20px; padding: 15px;")
        self.aplicar_sombra(card_tabla)
        
        layout_tab = QVBoxLayout(card_tabla)
        lbl_t_titulo = QLabel("EVIDENCIA COMPUTACIONAL (ENTORNO DE APROXIMACIÓN NUMÉRICA)")
        lbl_t_titulo.setStyleSheet("color: #64748B; font-weight: bold; font-size: 11px; margin-bottom: 5px;")
        
        self.tabla_limites = QTableWidget(4, 4)
        self.tabla_limites.setHorizontalHeaderLabels(["x → a⁻", "f(x)", "x → a⁺", "f(x)"])
        self.tabla_limites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_limites.setStyleSheet("""
            QTableWidget { 
                background-color: #F8FAFC; 
                border-radius: 12px; 
                border: 1px solid #E2E8F0;
                font-size: 11px; 
                color: #1E293B;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                padding: 4px;
                font-weight: bold;
                border: none;
                color: #475569;
            }
        """)
        self.tabla_limites.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_limites.setMaximumHeight(130)
        
        layout_tab.addWidget(lbl_t_titulo)
        layout_tab.addWidget(self.tabla_limites)
        panel_izquierdo.addWidget(card_tabla)

        # Tarjeta 3: Zona Interactiva con Autovalidación en Tiempo Real
        card_defensa = QFrame()
        card_defensa.setStyleSheet("background-color: white; border-radius: 20px; padding: 15px;")
        self.aplicar_sombra(card_defensa)
        
        layout_defensa = QVBoxLayout(card_defensa)
        lbl_defensa_titulo = QLabel("CONCLUSIONES PARA LA DEFENSA (CAMPOS PARA EVALUACIÓN ORAL)")
        lbl_defensa_titulo.setStyleSheet("color: #0F172A; font-weight: 800; font-size: 11px; letter-spacing: 0.5px; margin-bottom: 5px;")
        layout_defensa.addWidget(lbl_defensa_titulo)

        # Fila: Límite L
        layout_limite = QHBoxLayout()
        lbl_res_limite = QLabel("Valor del Límite (L):")
        lbl_res_limite.setStyleSheet("font-size: 12px; color: #475569; font-weight: bold;")
        self.input_limite_defensa = QLineEdit()
        self.input_limite_defensa.setPlaceholderText("Ej: 8  ó  No existe")
        self.input_limite_defensa.setStyleSheet("""
            QLineEdit {
                background-color: #F8FAFC; border: 1px solid #CBD5E1; 
                padding: 6px; border-radius: 8px; font-size: 12px; color: #1E293B;
            }
            QLineEdit:focus { border: 1px solid #0EA5E9; }
        """)
        layout_limite.addWidget(lbl_res_limite)
        layout_limite.addWidget(self.input_limite_defensa)
        layout_defensa.addLayout(layout_limite)

        # Fila: Clasificación
        layout_concl = QHBoxLayout()
        lbl_res_concl = QLabel("Conclusión Analítica:")
        lbl_res_concl.setStyleSheet("font-size: 12px; color: #475569; font-weight: bold;")
        self.combo_continuidad = QComboBox()
        self.combo_continuidad.addItems([
            "[ Seleccionar conclusión ]", 
            "La función es Continua en x = a", 
            "Discontinuidad Evitable / Removible (REI)", 
            "Discontinuidad Esencial de Salto Finito", 
            "Discontinuidad Asintótica / Infinita"
        ])
        self.combo_continuidad.setStyleSheet("""
            QComboBox {
                background-color: #F8FAFC; border: 1px solid #CBD5E1; 
                padding: 5px; border-radius: 8px; font-size: 12px; color: #1E293B;
            }
        """)
        layout_concl.addWidget(lbl_res_concl)
        layout_concl.addWidget(self.combo_continuidad)
        layout_defensa.addLayout(layout_concl)

        # NUEVO: Etiqueta dinámica de respuesta interactiva (Feedback)
        self.lbl_validacion = QLabel("Esperando respuestas...")
        self.lbl_validacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_validacion.setStyleSheet("""
            background-color: #F1F5F9; color: #64748B; 
            font-weight: bold; font-size: 12px; 
            padding: 8px; border-radius: 8px; margin-top: 5px;
        """)
        layout_defensa.addWidget(self.lbl_validacion)

        # Conexión instantánea de señales (triggers)
        self.input_limite_defensa.textChanged.connect(self.ejecutar_autovalidacion)
        self.combo_continuidad.currentIndexChanged.connect(self.ejecutar_autovalidacion)

        panel_izquierdo.addWidget(card_defensa)
        
        # ================= COLUMNA DERECHA: VISUALIZACIÓN GRÁFICA =================
        panel_grafico = QVBoxLayout()
        panel_grafico.setSpacing(10)
        
        lbl_g_titulo = QLabel("REPRESENTACIÓN GRÁFICA ASOCIADA (MUEVA LA RUEDA DEL MOUSE PARA HACER ZOOM)")
        lbl_g_titulo.setStyleSheet("color: #475569; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;")
        
        self.lienzo_grafico = LienzoLimites()
        self.aplicar_sombra(self.lienzo_grafico)
        
        panel_grafico.addWidget(lbl_g_titulo)
        panel_grafico.addWidget(self.lienzo_grafico)

        layout_principal.addLayout(panel_izquierdo, 1)
        layout_principal.addLayout(panel_grafico, 1)

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(15, 23, 42, 25))
        sombra.setOffset(0, 6)
        widget.setGraphicsEffect(sombra)

    def mostrar_datos_modulo_limites(self, modelo):
        """Actualiza las etiquetas, guarda el modelo y limpia los campos"""
        self.modelo_actual = modelo  # Guardamos el estado matemático
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
        
        # Resetear los campos para el nuevo ejercicio
        self.input_limite_defensa.clear()
        self.combo_continuidad.setCurrentIndex(0)
        self.lbl_validacion.setText("Esperando respuestas para el nuevo caso...")
        self.lbl_validacion.setStyleSheet("background-color: #F1F5F9; color: #64748B; font-weight: bold; font-size: 12px; padding: 8px; border-radius: 8px;")
        
        self.tabla_limites.clearContents()

        # Rellenar tabla analítica
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
        """Compara la entrada del usuario con los valores analíticos exactos del modelo"""
        if not self.modelo_actual:
            return

        texto_limite = self.input_limite_defensa.text().strip().lower()
        indice_combobox = self.combo_continuidad.currentIndex()

        # Si no ha completado ambos campos, se queda en estado de espera
        if not texto_limite or indice_combobox == 0:
            self.lbl_validacion.setText("Por favor, completa ambos campos para verificar.")
            self.lbl_validacion.setStyleSheet("background-color: #FFFBEB; color: #B45309; font-weight: bold; font-size: 12px; padding: 8px; border-radius: 8px;")
            return

        # 1. Determinar valores esperados según las reglas del modelo matemático
        limite_esperado_correcto = False
        caso_esperado_correcto = False

        if self.modelo_actual.caso == 1:
            # Removible: El límite existe y es igual a (a + d1)
            valor_real_l = self.modelo_actual.a + self.modelo_actual.dígitos[0]
            caso_esperado_correcto = (indice_combobox == 2) # Discontinuidad Evitable / Removible
            try:
                limite_esperado_correcto = abs(float(texto_limite) - valor_real_l) < 0.01
            except ValueError:
                limite_esperado_correcto = False

        elif self.modelo_actual.caso == 2:
            # Salto Finito: Los límites laterales son distintos, por ende el límite global NO EXISTE
            caso_esperado_correcto = (indice_combobox == 3) # Discontinuidad Esencial de Salto Finito
            limite_esperado_correcto = ("no existe" in texto_limite or "no" in texto_limite)

        elif self.modelo_actual.caso == 3:
            # Infinita: Tiende a infinito, el límite global NO EXISTE (o es infinito)
            caso_esperado_correcto = (indice_combobox == 4) # Discontinuidad Asintótica / Infinita
            limite_esperado_correcto = ("no existe" in texto_limite or "infinito" in texto_limite or "no" in texto_limite)

        # 2. Desplegar el veredicto visual en la interfaz
        if limite_esperado_correcto and caso_esperado_correcto:
            self.lbl_validacion.setText("✓ ANÁLISIS CORRECTO: ¡Excelente defensa matemática!")
            self.lbl_validacion.setStyleSheet("background-color: #DCFCE7; color: #15803D; font-weight: bold; font-size: 12px; padding: 8px; border-radius: 8px; border: 1px solid #BBF7D0;")
        else:
            self.lbl_validacion.setText("✗ ANÁLISIS INCORRECTO: Revisa el comportamiento de los límites laterales.")
            self.lbl_validacion.setStyleSheet("background-color: #FEE2E2; color: #B91C1C; font-weight: bold; font-size: 12px; padding: 8px; border-radius: 8px; border: 1px solid #FCA5A5;")