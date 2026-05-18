from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QGraphicsDropShadowEffect,
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
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(24)

        # ── Tarjeta de entrada ─────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 30px; padding: 20px; }"
        )
        self._apply_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        instruccion = QLabel("INGRESA TU IDENTIDAD")
        instruccion.setStyleSheet(
            "color: #64748B; font-weight: 800; font-size: 14px; letter-spacing: 1px;"
        )
        card_layout.addWidget(instruccion, alignment=Qt.AlignmentFlag.AlignCenter)

        self.input_rut = QLineEdit()
        self.input_rut.setPlaceholderText("12.345.678-K")
        self.input_rut.setMinimumHeight(80)
        self.input_rut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_rut.setStyleSheet("""
            QLineEdit {
                border: 3px solid #F1F5F9; border-radius: 20px;
                font-size: 32px; font-weight: 900;
                color: #1E293B; background-color: #F8FAFC;
            }
            QLineEdit:focus { border: 3px solid #4ECDC4; background-color: white; }
        """)
        self.input_rut.returnPressed.connect(self._emitir_validar)
        card_layout.addWidget(self.input_rut)

        self.btn_validar = QPushButton("VERIFICAR SISTEMA")
        self.btn_validar.setMinimumHeight(60)
        self.btn_validar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validar.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4; color: white;
                border-radius: 20px; font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45B7AF; }
            QPushButton:pressed { background-color: #3AA8A0; }
        """)
        self.btn_validar.clicked.connect(self._emitir_validar)
        card_layout.addWidget(self.btn_validar)
        layout.addWidget(card)

        # ── Botones de pestañas ────────────────────────────────
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(8)
        self._tabs_btns = {}
        self._tabs_content = {}

        for key, label in [
            ("validacion", "Módulo 11"),
            ("variable_v", "Variable v"),
            ("ecuacion",   "Ecuación"),
            ("resultado",  "Resultado"),
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9; color: #64748B;
                    border-radius: 12px; font-size: 12px; font-weight: bold;
                    padding: 8px 16px; border: none;
                }
                QPushButton:checked { background-color: #4ECDC4; color: white; }
                QPushButton:hover:!checked { background-color: #E2E8F0; }
            """)
            btn.clicked.connect(lambda _, k=key: self._mostrar_tab(k))
            tabs_row.addWidget(btn)
            self._tabs_btns[key] = btn

        tabs_row.addStretch()
        layout.addLayout(tabs_row)

        # ── Stack ──────────────────────────────────────────────
        self._stack = QFrame()
        self._stack.setMinimumHeight(380)
        self._stack_layout = QVBoxLayout(self._stack)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)

        for key in ["validacion", "variable_v", "ecuacion"]:
            scroll = self._hacer_scroll_consola("Esperando datos de entrada...")
            self._stack_layout.addWidget(scroll)
            self._tabs_content[key] = scroll

        resultado_scroll = self._build_tab_resultado()
        self._stack_layout.addWidget(resultado_scroll)
        self._tabs_content["resultado"] = resultado_scroll

        layout.addWidget(self._stack)
        layout.addStretch()

        self._mostrar_tab("validacion")

    # ──────────────────────────── constructores de widgets ─────
    def _hacer_scroll_consola(self, texto_inicial: str) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; border-radius: 20px; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #F1F5F9; }
            QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 3px; }
        """)
        lbl = QLabel(texto_inicial)
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lbl.setStyleSheet(self._estilo_consola("#4ECDC4", "#A5F3FC"))
        scroll.setWidget(lbl)
        return scroll

    def _build_tab_resultado(self) -> QScrollArea:
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(12)

        # ── Tarjeta principal ──────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 20px; padding: 8px; }"
        )
        self._apply_shadow(card)
        card_lay = QVBoxLayout(card)
        card_lay.setSpacing(10)
        card_lay.setContentsMargins(20, 16, 20, 16)

        self.lbl_estado = QLabel("—")
        self.lbl_estado.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #94A3B8;"
        )
        card_lay.addWidget(self.lbl_estado)

        self.lbl_tipo_conica = QLabel("—")
        self.lbl_tipo_conica.setStyleSheet(
            "font-size: 28px; font-weight: 900; color: #4ECDC4;"
        )
        card_lay.addWidget(self.lbl_tipo_conica)

        self.lbl_ecuacion = QLabel("—")
        self.lbl_ecuacion.setWordWrap(True)
        self.lbl_ecuacion.setStyleSheet(
            "font-family: Consolas; font-size: 13px; color: #1E293B; "
            "background: #F8FAFC; border-radius: 10px; padding: 10px;"
        )
        card_lay.addWidget(self.lbl_ecuacion)

        self.lbl_explicacion = QLabel("—")
        self.lbl_explicacion.setWordWrap(True)
        self.lbl_explicacion.setStyleSheet("font-size: 12px; color: #64748B;")
        card_lay.addWidget(self.lbl_explicacion)

        lay.addWidget(card)

        # ── Tarjeta caso límite (Fase 6) ───────────────────────
        card_caso = QFrame()
        card_caso.setStyleSheet(
            "QFrame { background-color: white; border-radius: 20px; padding: 8px; }"
        )
        self._apply_shadow(card_caso)
        caso_lay = QVBoxLayout(card_caso)
        caso_lay.setContentsMargins(20, 14, 20, 14)
        caso_lay.setSpacing(8)

        lbl_titulo_caso = QLabel("MÓDULO DE LÍMITES — CASO SELECCIONADO")
        lbl_titulo_caso.setStyleSheet(
            "color: #94A3B8; font-weight: 800; font-size: 11px; letter-spacing: 1px;"
        )
        caso_lay.addWidget(lbl_titulo_caso)

        self.lbl_caso_limite = QLabel("—")
        self.lbl_caso_limite.setWordWrap(True)
        self.lbl_caso_limite.setStyleSheet(
            "font-family: Consolas; font-size: 12px; color: #065F46; "
            "background: #ECFDF5; border-radius: 10px; padding: 10px; "
            "border-left: 4px solid #4ECDC4;"
        )
        caso_lay.addWidget(self.lbl_caso_limite)
        lay.addWidget(card_caso)

        # ── Tarjeta elementos geométricos (Fase 4 del PDF) ─────
        card_defensa = QFrame()
        card_defensa.setStyleSheet(
            "QFrame { background-color: white; border-radius: 20px; padding: 8px; }"
        )
        self._apply_shadow(card_defensa)
        defensa_lay = QVBoxLayout(card_defensa)
        defensa_lay.setContentsMargins(20, 14, 20, 16)
        defensa_lay.setSpacing(8)

        lbl_defensa = QLabel("ELEMENTOS DE LA CÓNICA (PARA COMPLETAR EN DEFENSA)")
        lbl_defensa.setStyleSheet(
            "color: #94A3B8; font-weight: 800; font-size: 11px; letter-spacing: 1px;"
        )
        defensa_lay.addWidget(lbl_defensa)

        estilo_input = """
            QLineEdit {
                border: 2px solid #E2E8F0; border-radius: 10px;
                font-size: 13px; color: #1E293B;
                background: #F8FAFC; padding: 8px 12px;
            }
            QLineEdit:focus { border: 2px solid #4ECDC4; background: white; }
        """

        # Elementos exactos según Fase 4 del PDF
        elementos = [
            ("campo_centro",   "Centro (h, k)"),
            ("campo_vertices", "Vértices"),
            ("campo_focos",    "Focos"),
            ("campo_eje_may",  "Eje Mayor / Transverso"),
            ("campo_eje_men",  "Eje Menor / Conjugado"),
            ("campo_direc",    "Directriz (si corresponde)"),
        ]

        for attr, label_text in elementos:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600;")
            defensa_lay.addWidget(lbl)
            campo = QLineEdit()
            campo.setPlaceholderText(f"Ingrese {label_text}...")
            campo.setStyleSheet(estilo_input)
            campo.setMinimumHeight(34)
            defensa_lay.addWidget(campo)
            setattr(self, attr, campo)

        lay.addWidget(card_defensa)
        lay.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #F1F5F9; }
            QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 3px; }
        """)
        scroll.setWidget(inner)
        return scroll

    # ─────────────────────────── slots públicos ────────────────
    def mostrar_resultado(self, exito: bool, log_validacion: str):
        lbl = self._tabs_content["validacion"].widget()
        color_borde = "#4ECDC4" if exito else "#FF6B6B"
        color_texto = "#A5F3FC" if exito else "#FECACA"
        lbl.setStyleSheet(self._estilo_consola(color_borde, color_texto))
        lbl.setText(log_validacion)
        if exito:
            self.lbl_estado.setText("✓  RUT VÁLIDO")
            self.lbl_estado.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #22C55E;"
            )
        else:
            self.lbl_estado.setText("✗  RUT INVÁLIDO")
            self.lbl_estado.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #EF4444;"
            )
            self.lbl_tipo_conica.setText("—")
            self.lbl_ecuacion.setText("—")
            self.lbl_explicacion.setText("—")
        self._mostrar_tab("validacion")

    def mostrar_variable_v(self, log_v: str):
        self._tabs_content["variable_v"].widget().setText(log_v)

    def mostrar_ecuacion(self, log_ec: str):
        self._tabs_content["ecuacion"].widget().setText(log_ec)

    def mostrar_conica(self, tipo: str, ecuacion_str: str, explicacion: str):
        self.lbl_tipo_conica.setText(tipo)
        self.lbl_ecuacion.setText(ecuacion_str)
        self.lbl_explicacion.setText(explicacion)

    def mostrar_caso_limite(self, caso: dict | None):
        self.lbl_caso_limite.setText(caso["explicacion"] if caso else "—")

    # ─────────────────────────── helpers ───────────────────────
    def _emitir_validar(self):
        self.boton_validar_clicado.emit(self.input_rut.text())

    def _mostrar_tab(self, key: str):
        for k, widget in self._tabs_content.items():
            widget.setVisible(False)
            self._tabs_btns[k].setChecked(False)
        self._tabs_content[key].setVisible(True)
        self._tabs_btns[key].setChecked(True)

    def _apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def _estilo_consola(self, borde: str, texto: str) -> str:
        return (
            f"background-color: #1E293B; color: {texto}; "
            f"font-family: Consolas, Courier New; font-size: 13px; "
            f"padding: 20px; border-radius: 20px; border-left: 5px solid {borde};"
        )