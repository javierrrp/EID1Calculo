from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


# ─────────────────────────────────────────────────────────────
#  Paleta (tema claro, consistente con vista_principal.py)
# ─────────────────────────────────────────────────────────────
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


class VistaRut(QWidget):
    boton_validar_clicado = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        # ── Tarjeta de entrada ────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE};
                border: 0.5px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        self._apply_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(16, 14, 16, 14)

        # Etiqueta de campo
        instruccion = QLabel("INGRESA EL RUT")
        instruccion.setStyleSheet(
            f"color: {TEXT_MUT}; font-weight: 500; font-size: 10px;"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        card_layout.addWidget(instruccion)

        # Input principal
        self.input_rut = QLineEdit()
        self.input_rut.setPlaceholderText("12.345.678-K")
        self.input_rut.setMinimumHeight(52)
        self.input_rut.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input_rut.setStyleSheet(f"""
            QLineEdit {{
                border: 0.5px solid {BORDER};
                border-radius: 8px;
                font-size: 22px;
                font-weight: 500;
                color: {TEXT_PRI};
                background-color: {SURFACE};
                padding: 8px 14px;
                letter-spacing: 2px;
                font-family: Consolas, "Courier New", monospace;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {RUT_MID};
                background-color: {SURFACE};
            }}
        """)
        self.input_rut.returnPressed.connect(self._emitir_validar)
        self.input_rut.textChanged.connect(self._formatear_rut_en_vivo)
        card_layout.addWidget(self.input_rut)

        # Fila botón + hint
        row_btn = QHBoxLayout()
        row_btn.setSpacing(10)

        self.btn_validar = QPushButton("Verificar RUT")
        self.btn_validar.setMinimumHeight(42)
        self.btn_validar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validar.setStyleSheet(f"""
            QPushButton {{
                background-color: {RUT};
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 18px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {RUT_MID};
            }}
            QPushButton:pressed {{
                background-color: #124a84;
            }}
        """)
        self.btn_validar.clicked.connect(self._emitir_validar)
        row_btn.addWidget(self.btn_validar)

        hint = QLabel("↩  o presiona Enter")
        hint.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; border: none; background: transparent;"
        )
        row_btn.addWidget(hint)
        row_btn.addStretch()
        card_layout.addLayout(row_btn)
        layout.addWidget(card)

        # ── Pestañas ──────────────────────────────────────────
        tabs_container = QWidget()
        tabs_container.setStyleSheet("background: transparent;")
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(4)

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
            btn.setMinimumHeight(34)
            btn.setStyleSheet(self._estilo_tab(False))
            btn.clicked.connect(lambda checked, k=key: self._mostrar_tab(k))
            tabs_layout.addWidget(btn)
            self._tabs_btns[key] = btn

        tabs_layout.addStretch()
        layout.addWidget(tabs_container)

        # ── Subtítulo ─────────────────────────────────────────
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
        self.lbl_subtitulo.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-style: italic;
            padding: 5px 10px;
            background: {SURFACE2};
            border: 0.5px solid {BORDER};
            border-radius: 0px 6px 6px 6px;
        """)
        layout.addWidget(self.lbl_subtitulo)

        # ── Stack de contenido ────────────────────────────────
        self._stack = QFrame()
        self._stack.setStyleSheet("background: transparent; border: none;")
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

    # ── constructores internos ─────────────────────────────────
    def _hacer_scroll_consola(self, texto_inicial: str) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 0.5px solid {BORDER};
                border-radius: 8px;
                background: {BG};
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: {SURFACE2};
                border-radius: 4px;
                margin: 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        contenedor = QWidget()
        contenedor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        contenedor.setStyleSheet(f"background: {BG};")

        inner_layout = QVBoxLayout(contenedor)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        lbl = QLabel(texto_inicial)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        lbl.setMinimumWidth(0)
        lbl.setStyleSheet(self._estilo_consola(RUT_MID))

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
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 0.5px solid {BORDER};
                border-radius: 10px;
                background: {SURFACE};
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: {SURFACE2};
                border-radius: 4px;
                margin: 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background: {SURFACE};")
        inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        lay = QVBoxLayout(inner)
        lay.setContentsMargins(14, 14, 14, 18)
        lay.setSpacing(10)

        # ── Fila Estado + Cónica ──────────────────────────────
        row_top = QHBoxLayout()
        row_top.setSpacing(16)

        col_estado = QVBoxLayout()
        col_estado.setSpacing(4)
        lbl_sec1 = QLabel("ESTADO")
        lbl_sec1.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_MUT};"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        col_estado.addWidget(lbl_sec1)
        self.lbl_estado = QLabel("—")
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setStyleSheet(
            f"font-size: 18px; font-weight: 500; color: {TEXT_MUT};"
            f" border: none; background: transparent;"
        )
        col_estado.addWidget(self.lbl_estado)
        row_top.addLayout(col_estado)

        col_conica = QVBoxLayout()
        col_conica.setSpacing(4)
        lbl_sec2 = QLabel("TIPO DE CÓNICA ASIGNADA")
        lbl_sec2.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_MUT};"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        col_conica.addWidget(lbl_sec2)
        self.lbl_tipo_conica = QLabel("—")
        self.lbl_tipo_conica.setWordWrap(True)
        self.lbl_tipo_conica.setStyleSheet(
            f"font-size: 24px; font-weight: 500; color: {RUT};"
            f" border: none; background: transparent;"
        )
        col_conica.addWidget(self.lbl_tipo_conica)
        row_top.addLayout(col_conica)

        lay.addLayout(row_top)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {BORDER}; background: {BORDER}; border: none; max-height: 1px;")
        lay.addWidget(sep)

        # ── Explicación ───────────────────────────────────────
        self.lbl_explicacion = QLabel("—")
        self.lbl_explicacion.setWordWrap(True)
        self.lbl_explicacion.setStyleSheet(
            f"font-size: 12px; color: {TEXT_SEC}; line-height: 1.45;"
            f" border: none; background: transparent;"
        )
        lay.addWidget(self.lbl_explicacion)

        # ── Ecuación general ──────────────────────────────────
        lbl_sec3 = QLabel("ECUACIÓN GENERAL")
        lbl_sec3.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_MUT};"
            f" letter-spacing: 1px; border: none; background: transparent;"
        )
        lay.addWidget(lbl_sec3)

        self.lbl_ecuacion = QLabel("—")
        self.lbl_ecuacion.setWordWrap(True)
        self.lbl_ecuacion.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_ecuacion.setStyleSheet(f"""
            font-family: Consolas, "Courier New", monospace;
            font-size: 13px;
            font-weight: 500;
            color: {ERR};
            background: {BG};
            border-radius: 8px;
            padding: 10px 14px;
            border-left: 3px solid {ERR_MID};
            border-top: 0.5px solid {BORDER};
            border-right: 0.5px solid {BORDER};
            border-bottom: 0.5px solid {BORDER};
        """)
        lay.addWidget(self.lbl_ecuacion)

        # ── Hint de navegación ────────────────────────────────
        lbl_nav = QLabel(
            "Para ver el desarrollo completo, usa las pestañas numeradas ① ② ③ ④ ⑤"
        )
        lbl_nav.setWordWrap(True)
        lbl_nav.setStyleSheet(f"""
            font-size: 11px;
            color: {OK};
            font-style: italic;
            background: {OK_LIGHT};
            border-radius: 7px;
            padding: 8px 10px;
            border: 0.5px solid #C8DFB8;
        """)
        lay.addWidget(lbl_nav)

        scroll.setWidget(inner)
        return scroll

    # ── slots públicos (compatibles con el controlador) ────────
    def mostrar_resultado(self, exito: bool, log_validacion: str):
        lbl = self._tabs_content["validacion"]._label_contenido
        if exito:
            lbl.setStyleSheet(self._estilo_consola(RUT_MID))
        else:
            lbl.setStyleSheet(self._estilo_consola(ERR_MID))
        lbl.setText(log_validacion)

        if exito:
            self.lbl_estado.setText("✓  RUT VÁLIDO")
            self.lbl_estado.setStyleSheet(
                f"font-size: 18px; font-weight: 500; color: {OK};"
                f" border: none; background: transparent;"
            )
        else:
            self.lbl_estado.setText("✗  RUT INVÁLIDO")
            self.lbl_estado.setStyleSheet(
                f"font-size: 18px; font-weight: 500; color: {ERR};"
                f" border: none; background: transparent;"
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

    # ── helpers ────────────────────────────────────────────────
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
            self._tabs_btns[k].setStyleSheet(self._estilo_tab(False))

        self._tabs_content[key].setVisible(True)
        self._tabs_btns[key].setChecked(True)
        self._tabs_btns[key].setStyleSheet(self._estilo_tab(True))
        self.lbl_subtitulo.setText(self._subtitulos.get(key, ""))

    def _apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 6)
        widget.setGraphicsEffect(shadow)

    def _estilo_tab(self, activo: bool) -> str:
        if activo:
            return f"""
                QPushButton {{
                    background-color: {SURFACE};
                    color: {TEXT_PRI};
                    border-radius: 8px 8px 0px 0px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 6px 12px;
                    border: 0.5px solid {BORDER_STR};
                    border-bottom: none;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {SURFACE2};
                    color: {TEXT_SEC};
                    border-radius: 8px 8px 0px 0px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 6px 12px;
                    border: 0.5px solid {BORDER};
                    border-bottom: none;
                }}
                QPushButton:hover {{
                    background-color: #E8E6DF;
                    color: {TEXT_PRI};
                }}
            """

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
