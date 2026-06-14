from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class VistaRut(QWidget):
    boton_validar_clicado = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── Tarjeta de entrada ─────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 26px; padding: 18px; }"
        )
        self._apply_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        instruccion = QLabel("INGRESA TU RUT")
        instruccion.setStyleSheet(
            "color: #64748B; font-weight: 800; font-size: 14px; letter-spacing: 1px;"
        )
        card_layout.addWidget(instruccion, alignment=Qt.AlignmentFlag.AlignCenter)

        self.input_rut = QLineEdit()
        self.input_rut.setPlaceholderText("12.345.678-K")
        self.input_rut.setMinimumHeight(72)
        self.input_rut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_rut.setStyleSheet("""
            QLineEdit {
                border: 3px solid #F1F5F9;
                border-radius: 20px;
                font-size: 30px;
                font-weight: 900;
                color: #1E293B;
                background-color: #F8FAFC;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 3px solid #4ECDC4;
                background-color: white;
            }
        """)
        self.input_rut.returnPressed.connect(self._emitir_validar)
        self.input_rut.textChanged.connect(self._formatear_rut_en_vivo)
        card_layout.addWidget(self.input_rut)

        self.btn_validar = QPushButton("VERIFICAR RUT")
        self.btn_validar.setMinimumHeight(54)
        self.btn_validar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validar.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 18px;
                font-size: 15px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #45B7AF; }
            QPushButton:pressed { background-color: #3AA8A0; }
        """)
        self.btn_validar.clicked.connect(self._emitir_validar)
        card_layout.addWidget(self.btn_validar)

        layout.addWidget(card)

        # ── Botones de pestañas ────────────────────────────────
        tabs_container = QWidget()
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(8)

        self._tabs_btns = {}
        self._tabs_content = {}

        tabs_info = [
            ("validacion",    "① Módulo 11"),
            ("variable_v",    "② Variable v"),
            ("ecuacion",      "③ Ecuación"),
            ("clasificacion", "④ Clasificación"),
            ("canonica",      "⑤ Canónica"),
            ("inverso",       "⑥ Inverso"),
            ("resultado",     "⑦ Resultado"),
        ]


        for key, label in tabs_info:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(38)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #334155;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 14px;
                    border: none;
                }
                QPushButton:checked {
                    background-color: #4ECDC4;
                    color: white;
                }
                QPushButton:hover:!checked {
                    background-color: #E2E8F0;
                }
            """)
            btn.clicked.connect(lambda _, k=key: self._mostrar_tab(k))
            tabs_layout.addWidget(btn)
            self._tabs_btns[key] = btn

        tabs_layout.addStretch()
        layout.addWidget(tabs_container)

        # ── Subtítulo ──────────────────────────────────────────
        self._subtitulos = {
            "validacion":    "Procedimiento de validación del RUT — Algoritmo Módulo 11",
            "variable_v":    "Cálculo de la variable auxiliar v a partir del dígito verificador",
            "ecuacion":      "Construcción paso a paso de los coeficientes A, B, C, D, E y ajustes de cónicas",
            "clasificacion": "Clasificación de la cónica según los criterios de A y B",
            "canonica":      "Transformación de la ecuación general a la forma canónica (completar cuadrado)",
            "inverso":       "Procedimiento inverso: desde la forma canónica se recupera la ecuación general",
            "resultado":     "Clasificación final de la cónica y ecuación resultante",
        }

        self.lbl_subtitulo = QLabel("")
        self.lbl_subtitulo.setWordWrap(True)
        self.lbl_subtitulo.setStyleSheet("""
            color: #64748B;
            font-size: 11px;
            font-style: italic;
            padding: 4px 6px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
        """)
        layout.addWidget(self.lbl_subtitulo)

        # ── Stack principal ────────────────────────────────────
        self._stack = QFrame()
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._stack_layout = QVBoxLayout(self._stack)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)
        self._stack_layout.setSpacing(0)

        for key in ["validacion", "variable_v", "ecuacion", "clasificacion", "canonica", "inverso"]:
            scroll = self._hacer_scroll_consola("Esperando datos de entrada...")
            self._stack_layout.addWidget(scroll)
            self._tabs_content[key] = scroll

        resultado_scroll = self._build_tab_resultado()
        self._stack_layout.addWidget(resultado_scroll)
        self._tabs_content["resultado"] = resultado_scroll

        layout.addWidget(self._stack, 1)

        self._mostrar_tab("validacion")

    # ───────────────────────── constructores ──────────────────
    def _hacer_scroll_consola(self, texto_inicial: str) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                border-radius: 18px;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #E2E8F0;
                border-radius: 4px;
                margin: 6px 0 6px 0;
            }
            QScrollBar::handle:vertical {
                background: #94A3B8;
                border-radius: 4px;
                min-height: 28px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        contenedor = QWidget()
        contenedor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        contenedor.setStyleSheet("background: transparent;")

        inner_layout = QVBoxLayout(contenedor)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        lbl = QLabel(texto_inicial)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        lbl.setMinimumWidth(0)
        lbl.setStyleSheet(self._estilo_consola("#4ECDC4", "#A5F3FC"))

        inner_layout.addWidget(lbl)
        scroll.setWidget(contenedor)
        scroll._label_contenido = lbl
        return scroll

    def _build_tab_resultado(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #E2E8F0;
                border-radius: 4px;
                margin: 6px 0 6px 0;
            }
            QScrollBar::handle:vertical {
                background: #94A3B8;
                border-radius: 4px;
                min-height: 28px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        lay = QVBoxLayout(inner)
        lay.setContentsMargins(4, 4, 4, 16)
        lay.setSpacing(12)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 8px;
            }
        """)
        self._apply_shadow(card)

        card_lay = QVBoxLayout(card)
        card_lay.setSpacing(10)
        card_lay.setContentsMargins(20, 16, 20, 16)

        lbl_sec1 = QLabel("Estado del RUT")
        lbl_sec1.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #94A3B8; letter-spacing: 1px;"
        )
        card_lay.addWidget(lbl_sec1)

        self.lbl_estado = QLabel("—")
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #94A3B8;"
        )
        card_lay.addWidget(self.lbl_estado)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: #E2E8F0; min-height: 1px; margin: 4px 0;")
        card_lay.addWidget(sep1)

        lbl_sec2 = QLabel("Tipo de Cónica")
        lbl_sec2.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #94A3B8; letter-spacing: 1px;"
        )
        card_lay.addWidget(lbl_sec2)

        self.lbl_tipo_conica = QLabel("—")
        self.lbl_tipo_conica.setWordWrap(True)
        self.lbl_tipo_conica.setStyleSheet(
            "font-size: 28px; font-weight: 900; color: #4ECDC4;"
        )
        card_lay.addWidget(self.lbl_tipo_conica)

        self.lbl_explicacion = QLabel("—")
        self.lbl_explicacion.setWordWrap(True)
        self.lbl_explicacion.setStyleSheet("""
            font-size: 13px;
            color: #475569;
            line-height: 1.45;
            padding-bottom: 4px;
        """)
        card_lay.addWidget(self.lbl_explicacion)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #E2E8F0; min-height: 1px; margin: 4px 0;")
        card_lay.addWidget(sep2)

        lbl_sec3 = QLabel("Ecuación General")
        lbl_sec3.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #94A3B8; letter-spacing: 1px;"
        )
        card_lay.addWidget(lbl_sec3)

        self.lbl_ecuacion = QLabel("—")
        self.lbl_ecuacion.setWordWrap(True)
        self.lbl_ecuacion.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_ecuacion.setStyleSheet("""
            font-family: Consolas, 'Courier New';
            font-size: 14px;
            font-weight: bold;
            color: #1E293B;
            background: #F8FAFC;
            border-radius: 10px;
            padding: 12px;
            border: 1px solid #E2E8F0;
        """)
        card_lay.addWidget(self.lbl_ecuacion)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("background-color: #E2E8F0; min-height: 1px; margin: 4px 0;")
        card_lay.addWidget(sep3)

        lbl_nav = QLabel(
            "Para ver el desarrollo completo, usa las pestañas numeradas ① ② ③ ④ ⑤"
        )
        lbl_nav.setWordWrap(True)
        lbl_nav.setStyleSheet("""
            font-size: 11px;
            color: #64748B;
            font-style: italic;
            background: #F0FDF4;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #D1FAE5;
        """)
        card_lay.addWidget(lbl_nav)

        lay.addWidget(card)
        scroll.setWidget(inner)
        return scroll

    # ───────────────────────── slots públicos ─────────────────
    def mostrar_resultado(self, exito: bool, log_validacion: str):
        lbl = self._tabs_content["validacion"]._label_contenido
        color_borde = "#4ECDC4" if exito else "#FF6B6B"
        color_texto = "#A5F3FC" if exito else "#FECACA"
        lbl.setStyleSheet(self._estilo_consola(color_borde, color_texto))
        lbl.setText(log_validacion)

        if exito:
            self.lbl_estado.setText("✓  RUT VÁLIDO")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #22C55E;"
            )
        else:
            self.lbl_estado.setText("✗  RUT INVÁLIDO")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #EF4444;"
            )
            self.lbl_tipo_conica.setText("—")
            self.lbl_ecuacion.setText("—")
            self.lbl_explicacion.setText("—")

        self._mostrar_tab("validacion")

    def mostrar_variable_v(self, log_v: str):
        self._tabs_content["variable_v"]._label_contenido.setText(log_v)

    def mostrar_ecuacion(self, log_ec: str):
        self._tabs_content["ecuacion"]._label_contenido.setText(log_ec)

    def mostrar_canonica(self, log_canon: str):
        self._tabs_content["canonica"]._label_contenido.setText(log_canon)

    def mostrar_inverso(self, log_inv: str):
        self._tabs_content["inverso"]._label_contenido.setText(log_inv)

    def mostrar_conica(self, tipo: str, ecuacion_str: str, explicacion: str):
        self.lbl_tipo_conica.setText(tipo)
        self.lbl_ecuacion.setText(ecuacion_str)
        self.lbl_explicacion.setText(explicacion)
        
    def mostrar_clasificacion(self, log_clas: str):
        self._tabs_content["clasificacion"]._label_contenido.setText(log_clas)
    # ───────────────────────── helpers ────────────────────────
    def _emitir_validar(self):
        self.boton_validar_clicado.emit(self.input_rut.text())

    def _formatear_rut_en_vivo(self, text: str):
        self.input_rut.textChanged.disconnect(self._formatear_rut_en_vivo)

        limpio = "".join(c for c in text.upper() if c.isdigit() or c == "K")
        limpio = limpio[:9]

        resultado = ""
        if len(limpio) > 1:
            cuerpo = limpio[:-1]
            dv = limpio[-1]
            cuerpo_formateado = ""
            for i, digito in enumerate(reversed(cuerpo)):
                if i > 0 and i % 3 == 0:
                    cuerpo_formateado = "." + cuerpo_formateado
                cuerpo_formateado = digito + cuerpo_formateado
            resultado = f"{cuerpo_formateado}-{dv}"
        else:
            resultado = limpio

        self.input_rut.setText(resultado)
        self.input_rut.setCursorPosition(len(resultado))
        self.input_rut.textChanged.connect(self._formatear_rut_en_vivo)

    def _mostrar_tab(self, key: str):
        for k, widget in self._tabs_content.items():
            widget.setVisible(False)
            self._tabs_btns[k].setChecked(False)

        self._tabs_content[key].setVisible(True)
        self._tabs_btns[key].setChecked(True)
        self.lbl_subtitulo.setText(self._subtitulos.get(key, ""))

    def _apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def _estilo_consola(self, borde: str, texto: str) -> str:
        return (
            f"background-color: #0F172A; color: {texto}; "
            f"font-family: Consolas, 'Courier New'; "
            f"font-size: 13px; line-height: 1.45; "
            f"padding: 22px; border-radius: 20px; "
            f"border-left: 5px solid {borde};"
        )