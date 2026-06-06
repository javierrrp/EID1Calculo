import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QComboBox, QScrollArea, QTextEdit, QPushButton, QListView)
from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QWheelEvent, QMouseEvent, QFont

class LienzoLimites(QWidget):
    """Lienzo matemático manual mediante QPainter con soporte de Zoom y Arrastre Interactivo (Pan & Zoom)"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 510) 
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
        self.modelo_vinculado = None
        self.escala_base = 34  
        self.factor_zoom = 1.0  
        
        self.desfase_x = 0
        self.desfase_y = 0
        self.en_arrastre = False
        self.ultima_posicion_mouse = QPoint()

    def vincular_modelo(self, modelo):
        self.modelo_vinculado = modelo
        self.desfase_x = 0
        self.desfase_y = 0
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.en_arrastre = True
            self.ultima_posicion_mouse = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.en_arrastre:
            posicion_actual = event.position().toPoint()
            delta = posicion_actual - self.ultima_posicion_mouse
            self.desfase_x += delta.x()
            self.desfase_y += delta.y()
            self.ultima_posicion_mouse = posicion_actual
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.en_arrastre = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

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
        centro_x = (ancho // 2) + self.desfase_x
        centro_y = (alto // 2) + self.desfase_y
        
        escala = int(self.escala_base * self.factor_zoom)
        if escala < 5: escala = 5

        fuente_ejes = QFont("Segoe UI", 9)
        painter.setFont(fuente_ejes)

        pen_grilla = QPen(QColor("#F1F5F9"), 1, Qt.PenStyle.SolidLine)
        pen_texto = QPen(QColor("#94A3B8")) 
        painter.setPen(pen_grilla)
        
        inicio_x = (centro_x % escala) - escala
        for px in range(inicio_x, ancho + escala, escala):
            painter.drawLine(px, 0, px, alto)
            
        inicio_y = (centro_y % escala) - escala
        for py in range(inicio_y, alto + escala, escala):
            painter.drawLine(0, py, ancho, py)

        pen_ejes = QPen(QColor("#0F172A"), 1.5, Qt.PenStyle.SolidLine)
        painter.setPen(pen_ejes)
        if 0 <= centro_y <= alto:
            painter.drawLine(0, centro_y, ancho, centro_y)
        if 0 <= centro_x <= ancho:
            painter.drawLine(centro_x, 0, centro_x, alto)

        painter.setPen(pen_texto)
        paso_unidades = 1
        if escala < 12: paso_unidades = 5
        elif escala < 20: paso_unidades = 2

        unidades_izq = (centro_x // escala) + 2
        unidades_der = ((ancho - centro_x) // escala) + 2
        for u in range(-unidades_izq, unidades_der):
            if u == 0: continue
            if u % paso_unidades == 0:
                pos_x = centro_x + (u * escala)
                if 0 <= pos_x <= ancho:
                    y_num = max(16, min(alto - 6, centro_y + 16))
                    painter.drawLine(pos_x, centro_y - 3, pos_x, centro_y + 3)
                    painter.drawText(pos_x - 12, y_num, f"{u}")

        unidades_abajo = ((alto - centro_y) // escala) + 2
        unidades_arriba = (centro_y // escala) + 2
        for u in range(-unidades_abajo, unidades_arriba):
            if u == 0: continue
            if u % paso_unidades == 0:
                pos_y = centro_y - (u * escala)
                if 0 <= pos_y <= alto:
                    x_num = max(4, min(ancho - 24, centro_x - 22))
                    painter.drawLine(centro_x - 3, pos_y, centro_x + 3, pos_y)
                    painter.drawText(x_num, pos_y + 4, f"{u}")
                
        if not self.modelo_vinculado or not self.modelo_vinculado.dígitos:
            return

        pen_funcion = QPen(QColor("#0284C7"), 3, Qt.PenStyle.SolidLine)
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

        pix_a = centro_x + int(self.modelo_vinculado.a * escala)
        if 0 <= pix_a <= ancho:
            pen_asintota = QPen(QColor("#FDA4AF"), 1.2, Qt.PenStyle.DashLine)
            painter.setPen(pen_asintota)
            painter.drawLine(pix_a, 0, pix_a, alto)
            
            painter.setPen(QPen(QColor("#EF4444"), 2.5))
            if self.modelo_vinculado.caso == 1:
                lim_teorico = self.modelo_vinculado.a + self.modelo_vinculado.dígitos[0]
                py_a = centro_y - int(lim_teorico * escala)
                if 0 <= py_a <= alto:
                    painter.setBrush(QBrush(QColor("#FFFFFF")))
                    painter.drawEllipse(pix_a - 4, py_a - 4, 8, 8)
                
            elif self.modelo_vinculado.caso == 2:
                d2 = self.modelo_vinculado.dígitos[1]
                d4 = self.modelo_vinculado.dígitos[3]
                py_izq = centro_y - int((self.modelo_vinculado.a + d2) * escala)
                py_der = centro_y - int((self.modelo_vinculado.a + d4) * escala)
                
                if 0 <= py_izq <= alto:
                    painter.setBrush(QBrush(QColor("#FFFFFF")))
                    painter.drawEllipse(pix_a - 4, py_izq - 4, 8, 8)
                if 0 <= py_der <= alto:
                    painter.setBrush(QBrush(QColor("#EF4444")))
                    painter.drawEllipse(pix_a - 4, py_der - 4, 8, 8)


class VistaLimites(QWidget):
    def __init__(self):
        super().__init__()
        self.modelo_actual = None
        self.init_ui()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(24, 16, 24, 24)
        layout_principal.setSpacing(24)

        # ================= COLUMNA IZQUIERDA: PLANTEAMIENTO PEDAGÓGICO =================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #F1F5F9; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #CBD5E1; min-height: 30px; border-radius: 4px; }
        """)
        
        contenedor_izquierdo = QWidget()
        contenedor_izquierdo.setObjectName("ContenedorIzquierdo")
        contenedor_izquierdo.setStyleSheet("#ContenedorIzquierdo { background-color: transparent; }")
        
        panel_izquierdo = QVBoxLayout(contenedor_izquierdo)
        panel_izquierdo.setContentsMargins(0, 0, 8, 0)
        panel_izquierdo.setSpacing(18)

        self.lbl_caso_titulo = QLabel("ANÁLISIS MATEMÁTICO DE TRABAJO")
        self.lbl_caso_titulo.setStyleSheet("color: #1E293B; font-weight: 800; font-size: 13px; letter-spacing: 0.5px;")
        panel_izquierdo.addWidget(self.lbl_caso_titulo)

        lbl_titulo_origen = QLabel("Origen Algorítmico (Derivación por RUT):")
        lbl_titulo_origen.setStyleSheet("font-weight: 700; color: #334155; font-size: 12px;")
        panel_izquierdo.addWidget(lbl_titulo_origen)
        
        self.txt_origen_rut = QTextEdit()
        self.txt_origen_rut.setReadOnly(True)
        self.txt_origen_rut.setMinimumHeight(120)
        self.estilar_consola(self.txt_origen_rut)
        panel_izquierdo.addWidget(self.txt_origen_rut)

        lbl_titulo_marco = QLabel("Marco de Apoyo Analítico y Reglas del Caso:")
        lbl_titulo_marco.setStyleSheet("font-weight: 700; color: #334155; font-size: 12px;")
        panel_izquierdo.addWidget(lbl_titulo_marco)
        
        self.txt_marco_teorico = QTextEdit()
        self.txt_marco_teorico.setReadOnly(True)
        self.txt_marco_teorico.setMinimumHeight(180)
        self.estilar_consola(self.txt_marco_teorico)
        panel_izquierdo.addWidget(self.txt_marco_teorico)

        card_tabla = QFrame()
        card_tabla.setStyleSheet("background-color: #1E293B; border-radius: 12px; border: 1px solid #334155;")
        
        layout_tab = QVBoxLayout(card_tabla)
        layout_tab.setContentsMargins(16, 16, 16, 16)
        
        lbl_t_titulo = QLabel("EVIDENCIA COMPUTACIONAL LATERAL (ENTORNO DE x → a)")
        lbl_t_titulo.setStyleSheet("color: #94A3B8; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; margin-bottom: 6px;")
        
        self.tabla_limites = QTableWidget(4, 4)
        self.tabla_limites.setHorizontalHeaderLabels(["x → a⁻", "f(x) Izq", "x → a⁺", "f(x) Der"])
        self.tabla_limites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_limites.setStyleSheet("""
            QTableWidget { 
                background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; 
                font-family: 'Consolas', 'Courier New', monospace; font-size: 11px; color: #93C5FD;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A; padding: 6px; font-weight: 700; font-size: 11px;
                border: 1px solid #334155; color: #38BDF8;
            }
        """)
        self.tabla_limites.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_limites.setFixedHeight(165) 
        
        layout_tab.addWidget(lbl_t_titulo)
        layout_tab.addWidget(self.tabla_limites)
        panel_izquierdo.addWidget(card_tabla)

        scroll_area.setWidget(contenedor_izquierdo)
        
        # ================= COLUMNA DERECHA: SECCIÓN GRÁFICA Y EVALUACIÓN =================
        panel_grafico = QVBoxLayout()
        panel_grafico.setContentsMargins(0, 0, 0, 0)
        panel_grafico.setSpacing(12)
        panel_grafico.setAlignment(Qt.AlignmentFlag.AlignTop) 
        
        lbl_g_titulo = QLabel("📌 Analiza los datos de soporte e ingresa tus deducciones analíticas abajo:")
        lbl_g_titulo.setStyleSheet("color: #94A3B8; font-style: italic; font-size: 11px; padding-bottom: 2px;")
        panel_grafico.addWidget(lbl_g_titulo)
        
        self.lienzo_grafico = LienzoLimites()
        panel_grafico.addWidget(self.lienzo_grafico)

        self.card_defensa = QFrame()
        self.card_defensa.setObjectName("CardDefensa")
        self.card_defensa.setStyleSheet("#CardDefensa { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; }")
        
        layout_defensa = QVBoxLayout(self.card_defensa)
        layout_defensa.setContentsMargins(20, 16, 20, 16)
        layout_defensa.setSpacing(12)
        
        lbl_defensa_titulo = QLabel("Zona de Evaluación: Controles de Verificación")
        lbl_defensa_titulo.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;")
        layout_defensa.addWidget(lbl_defensa_titulo)

        grid_inputs = QGridLayout()
        grid_inputs.setHorizontalSpacing(20)
        grid_inputs.setVerticalSpacing(10)

        # Campo: Límite por izquierda
        lbl_lim_izq = QLabel("Lim (x→a⁻):")
        lbl_lim_izq.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600;")
        self.input_lim_izq = QLineEdit()
        self.input_lim_izq.setPlaceholderText("Ej: 5, inf o -inf")
        self.estilar_input(self.input_lim_izq)
        grid_inputs.addWidget(lbl_lim_izq, 0, 0)
        grid_inputs.addWidget(self.input_lim_izq, 0, 1)
        
        # Campo: Existencia del límite global
        lbl_existe = QLabel("¿Existe lim?:")
        lbl_existe.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600;")
        self.combo_existe = QComboBox()
        self.combo_existe.addItems(["[ Seleccione ]", "Sí", "No"])
        self.estilar_combo(self.combo_existe)
        grid_inputs.addWidget(lbl_existe, 1, 0)
        grid_inputs.addWidget(self.combo_existe, 1, 1)

        # Campo: Límite por derecha
        lbl_lim_der = QLabel("Lim (x→a⁺):")
        lbl_lim_der.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600;")
        self.input_lim_der = QLineEdit()
        self.input_lim_der.setPlaceholderText("Ej: 5, inf o -inf")
        self.estilar_input(self.input_lim_der)
        grid_inputs.addWidget(lbl_lim_der, 0, 2)
        grid_inputs.addWidget(self.input_lim_der, 0, 3)

        # Campo: Valor real en el punto crítico
        lbl_fa = QLabel("Valor f(a):")
        lbl_fa.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600;")
        self.input_fa = QLineEdit()
        self.input_fa.setPlaceholderText("Ej: 4 o No existe")
        self.estilar_input(self.input_fa)
        grid_inputs.addWidget(lbl_fa, 1, 2)
        grid_inputs.addWidget(self.input_fa, 1, 3)

        # Campo: Tipo de Continuidad / Discontinuidad
        lbl_res_concl = QLabel("Tipo Discont:")
        lbl_res_concl.setStyleSheet("font-size: 11px; color: #475569; font-weight: 600;")
        self.combo_continuidad = QComboBox()
        self.combo_continuidad.addItems([
            "[ Seleccione clasificación ]", 
            "Continua en x = a", 
            "Evitable / Removible", 
            "Esencial de Salto Finito", 
            "Asintótica / Infinita"
        ])
        self.estilar_combo(self.combo_continuidad)
        grid_inputs.addWidget(lbl_res_concl, 2, 0)
        grid_inputs.addWidget(self.combo_continuidad, 2, 1, 1, 3) 
        
        layout_defensa.addLayout(grid_inputs)

        layout_accion = QHBoxLayout()
        layout_accion.setSpacing(14)
        
        self.btn_validar = QPushButton("Verificar respuestas")
        self.btn_validar.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; color: #FFFFFF; font-weight: 700; font-size: 12px;
                padding: 10px 20px; border-radius: 6px; border: none; min-width: 160px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        self.btn_validar.clicked.connect(self.procesar_verificacion)
        
        self.lbl_validacion = QLabel("Esperando respuestas...")
        self.lbl_validacion.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        
        layout_accion.addWidget(self.btn_validar)
        layout_accion.addWidget(self.lbl_validacion, 1)
        layout_defensa.addLayout(layout_accion)

        panel_grafico.addWidget(self.card_defensa)

        layout_principal.addWidget(scroll_area, 43)
        layout_principal.addLayout(panel_grafico, 57)

    def estilar_consola(self, text_edit):
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E293B; color: #93C5FD;
                font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;
                border-radius: 12px; padding: 14px; border: 1px solid #334155;
            }
        """)

    def estilar_input(self, qlineedit):
        qlineedit.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF; border: 1px solid #CBD5E1; 
                padding: 6px 10px; border-radius: 6px; font-size: 11px; color: #1E293B;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; }
        """)

    def estilar_combo(self, qcombobox):
        qcombobox.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF; 
                border: 1px solid #CBD5E1; 
                padding: 6px 12px; 
                border-radius: 6px; 
                font-family: 'Segoe UI';
                font-size: 11px; 
                color: #1E293B;
            }
            QComboBox:focus { 
                border: 1px solid #3B82F6; 
            }
            QComboBox::drop-down { 
                border: none; 
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI';
                font-size: 11px;
                color: #1E293B;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
            }
        """)
        qcombobox.setView(QListView(self))

    def mostrar_datos_modulo_limites(self, modelo):
        """Muestra el planteamiento del problema utilizando los datos del modelo."""
        self.modelo_actual = modelo  
        self.lbl_caso_titulo.setText("MÓDULO DE LÍMITES · EJERCICIO ASIGNADO")
        
        a = modelo.a
        d1, d2, d4, d5 = modelo.dígitos[0], modelo.dígitos[1], modelo.dígitos[3], modelo.dígitos[4]

        texto_origen = (
            f"• Entrada del Sistema (RUT Evaluado): {getattr(modelo, 'rut_origen', 'Activo')}\n"
            f"• Punto Crítico Asignado (a): x = {a}\n"
            f"• Algoritmo de Selección Utilizado:\n"
            f"  La función por tramos condicionales se ha estructurado utilizando los\n"
            f"  dígitos específicos del RUT para parametrizar pendientes y desplazamientos.\n"
            f"  Regla del Caso actual: Caso de estudio Tipo {modelo.caso} configurado."
        )
        self.txt_origen_rut.setPlainText(texto_origen)

        if modelo.caso == 1:
            texto_marco = (
                f"Función matemática propuesta por tramos:\n"
                f"  f(x) = [ (x - {a}) * (x + {d1}) ] / (x - {a})    si x != {a}\n\n"
                f"Instrucciones de análisis analítico:\n"
                f"1. Observe la tendencia gráfica en el entorno del punto crítico x = {a}.\n"
                f"2. Utilice la tabla de evidencia lateral computacional para registrar\n"
                f"   valores numéricos a medida que 'x' se aproxima por la izquierda y derecha.\n"
                f"3. Evalúe analíticamente si la indeterminación puede simplificarse.\n"
                f"4. Determine si f({a}) está definida o no en el campo real."
            )
        elif modelo.caso == 2:
            texto_marco = (
                f"Función matemática propuesta por tramos condicionales:\n"
                f"  Tramo Izquierdo: f(x) = x + {d2}   si x < {a}\n"
                f"  Tramo Derecho:   f(x) = x + {d4}   si x >= {a}\n\n"
                f"Instrucciones de análisis analítico:\n"
                f"1. Evalúe el comportamiento de f(x) cuando se acerca a x = {a} desde valores menores.\n"
                f"2. Evalúe el comportamiento en el tramo derecho desde valores mayores.\n"
                f"3. Compare si ambas trayectorias convergen al mismo número real.\n"
                f"4. Verifique a cuál de los dos tramos pertenece legalmente el punto exacto x = {a}."
            )
        else:
            texto_marco = (
                f"Función racional propuesta para estudio de asíntotas:\n"
                f"  f(x) = {d5 + 1} / (x - {a})\n\n"
                f"Instrucciones de análisis analítico:\n"
                f"1. Analice qué ocurre con el denominador cuando x → {a}⁻ y cuando x → {a}⁺.\n"
                f"2. Recuerde las propiedades de una constante dividida por un número infinitesimal.\n"
                f"3. Defina si el límite crece sin cota o si se estabiliza en algún valor.\n"
                f"4. Determine la existencia de la función en la coordenada exacta de la asíntota."
            )
        self.txt_marco_teorico.setPlainText(texto_marco)
        
        self.input_lim_izq.clear()
        self.input_lim_der.clear()
        self.input_fa.clear()
        self.combo_existe.setCurrentIndex(0)
        self.combo_continuidad.setCurrentIndex(0)
        self.lbl_validacion.setText("Esperando respuestas...")
        
        self.tabla_limites.clearContents()
        t_izq, t_der = modelo.generar_tabla_valores()
        for i in range(4):
            item_x_izq = QTableWidgetItem(f"{t_izq[i][0]:.4f}")
            item_x_izq.setForeground(QColor("#38BDF8")) 
            self.tabla_limites.setItem(i, 0, item_x_izq)
            
            val_y_izq = "Indefinido" if t_izq[i][1] is None else f"{t_izq[i][1]:.4f}"
            item_y_izq = QTableWidgetItem(val_y_izq)
            self.tabla_limites.setItem(i, 1, item_y_izq)
            
            item_x_der = QTableWidgetItem(f"{t_der[i][0]:.4f}")
            item_x_der.setForeground(QColor("#38BDF8"))
            self.tabla_limites.setItem(i, 2, item_x_der)
            
            val_y_der = "Indefinido" if t_der[i][1] is None else f"{t_der[i][1]:.4f}"
            item_y_der = QTableWidgetItem(val_y_der)
            self.tabla_limites.setItem(i, 3, item_y_der)

        self.lienzo_grafico.vincular_modelo(modelo)

    def procesar_verificacion(self):
        """Lógica de verificación desacoplada y limpia de tipos de datos nativos de Qt."""
        try:
            if not hasattr(self, 'modelo_actual') or self.modelo_actual is None:
                self.lbl_validacion.setStyleSheet("color: #EF4444; font-weight: 700;")
                self.lbl_validacion.setText("❌ Error: Modelo matemático no inicializado.")
                return

            # Captura de textos de la UI de forma segura
            txt_izq = str(self.input_lim_izq.text()).strip().lower()
            txt_der = str(self.input_lim_der.text()).strip().lower()
            txt_fa = str(self.input_fa.text()).strip().lower()
            
            txt_existe = str(self.combo_existe.currentText()).strip().lower()
            txt_cont = str(self.combo_continuidad.currentText()).strip().lower()

            # Forzar validación de campos obligatorios
            if not txt_izq or not txt_der or not txt_fa or "[ seleccione" in txt_existe or "[ seleccione" in txt_cont:
                self.lbl_validacion.setStyleSheet("color: #EA580C; font-weight: 700;")
                self.lbl_validacion.setText("⚠️ Completa todas las opciones de la zona de evaluación.")
                return

            # Normalizador universal de Strings (compara exclusivamente textos)
            def normalizar_valor(val):
                s = str(val).strip().lower()
                if s in ["inf", "infinity", "+inf", "infinito", "float('inf')"]: return "inf"
                if s in ["-inf", "-infinity", "-infinito", "float('-inf')"]: return "-inf"
                if s in ["no existe", "indefinido", "indeterminado", "none", "null"]: return "no existe"
                try:
                    return str(round(float(s), 2))
                except (ValueError, TypeError):
                    return s

            user_izq = normalizar_valor(txt_izq)
            user_der = normalizar_valor(txt_der)
            user_fa = normalizar_valor(txt_fa)

            # Extraer respuestas de soporte de forma segura
            sol_izq, sol_der, sol_existe, sol_fa, sol_caso_idx = self.modelo_actual.obtener_respuestas_correctas()
            
            correct_izq = normalizar_valor(sol_izq)
            correct_der = normalizar_valor(sol_der)
            correct_fa = normalizar_valor(sol_fa)
            
            # Evaluar textos de ComboBoxes de forma explícita
            correct_existe = "sí" if int(sol_existe) == 1 else "no"
            
            mapeo_casos = {
                1: "continua en x = a",
                2: "evitable / removible",
                3: "esencial de salto finito",
                4: "asintótica / infinita"
            }
            correct_cont = mapeo_casos.get(int(sol_caso_idx), "")

            # Comparativa libre de punteros numéricos de C++
            errores = []
            if user_izq != correct_izq: errores.append("Límite Izquierdo")
            if user_der != correct_der: errores.append("Límite Derecho")
            if user_fa != correct_fa: errores.append("Valor f(a)")
            if txt_existe != correct_existe: errores.append("¿Existe Límite?")
            if txt_cont != correct_cont: errores.append("Clasificación de Continuidad")

            if not errores:
                self.lbl_validacion.setStyleSheet("color: #16A34A; font-weight: 700; font-size: 12px;")
                self.lbl_validacion.setText("🎉 ¡Perfecto! El análisis analítico es completamente correcto.")
            else:
                self.lbl_validacion.setStyleSheet("color: #DC2626; font-weight: 700;")
                self.lbl_validacion.setText(f"❌ Incorrecto en: {', '.join(errores)}.")

        except Exception as e:
            self.lbl_validacion.setStyleSheet("color: #7F1D1D; background-color: #FEE2E2; font-weight: bold;")
            self.lbl_validacion.setText(f"⚠️ Error controlado en validación: {str(e)}")


class SimuladorModeloMatematico:
    def __init__(self, caso=1):
        self.caso = caso  
        self.a = 2        
        self.dígitos = [3, 1, 4, 5, 2] 

    def evaluar_funcion(self, x):
        if abs(x - self.a) < 1e-5:
            if self.caso == 1: return None
            if self.caso == 2: return x + self.dígitos[3] 
            if self.caso == 3: return None

        if self.caso == 1:
            return ((x - self.a) * (x + self.dígitos[0])) / (x - self.a)
        elif self.caso == 2:
            if x < self.a:
                return x + self.dígitos[1]
            else:
                return x + self.dígitos[3]
        else:
            return (self.dígitos[4] + 1) / (x - self.a)

    def generar_tabla_valores(self):
        t_izq = [(self.a - delta, self.evaluar_funcion(self.a - delta)) for delta in [0.1, 0.01, 0.001, 0.0001]]
        t_der = [(self.a + delta, self.evaluar_funcion(self.a + delta)) for delta in [0.1, 0.01, 0.001, 0.0001]]
        return t_izq, t_der

    def obtener_respuestas_correctas(self):
        """Retorna las soluciones estructuradas de forma consistente como tipos nativos estándar"""
        if self.caso == 1:
            val_lim = round(float(self.a + self.dígitos[0]), 2)
            return val_lim, val_lim, 1, "no existe", 2  # 1=Sí existe, 2=Evitable
        elif self.caso == 2:
            val_izq = round(float(self.a + self.dígitos[1]), 2)
            val_der = round(float(self.a + self.dígitos[3]), 2)
            return val_izq, val_der, 2, val_der, 3      # 2=No existe, 3=Salto Finito
        else:
            return "-inf", "inf", 2, "no existe", 4     # 2=No existe, 4=Asintótica


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VistaLimites()
    
    # Prueba cambiando a caso=1, caso=2 o caso=3
    modelo_prueba = SimuladorModeloMatematico(caso=1)
    ventana.mostrar_datos_modulo_limites(modelo_prueba)
    
    ventana.setWindowTitle("Plataforma de Evaluación de Límites Analíticos")
    ventana.resize(1024, 700)
    ventana.show()
    sys.exit(app.exec())