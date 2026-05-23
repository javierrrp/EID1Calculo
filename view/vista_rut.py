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
        
        # AGREGAR ESTA LÍNEA AQUÍ:
        self.input_rut.textChanged.connect(self._formatear_rut_en_vivo)
        
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

    # ─────────────────────────── helpers ───────────────────────
    def _emitir_validar(self):
        self.boton_validar_clicado.emit(self.input_rut.text())

    def _formatear_rut_en_vivo(self, text: str):
        # Desconectar temporalmente para evitar un bucle infinito
        self.input_rut.textChanged.disconnect(self._formatear_rut_en_vivo)

        # 1. Limpiar el texto: dejar solo números y la letra 'K' (mayúscula)
        limpio = "".join(c for c in text.upper() if c.isdigit() or c == 'K')
        
        # 2. Limitar a 9 caracteres máximo (8 de cuerpo + 1 verificador)
        limpio = limpio[:9]

        # 3. Aplicar formato: XX.XXX.XXX-X
        resultado = ""
        if len(limpio) > 1:
            cuerpo = limpio[:-1]
            dv = limpio[-1]
            
            # Poner puntos al cuerpo de derecha a izquierda
            cuerpo_formateado = ""
            for i, digito in enumerate(reversed(cuerpo)):
                if i > 0 and i % 3 == 0:
                    cuerpo_formateado = "." + cuerpo_formateado
                cuerpo_formateado = digito + cuerpo_formateado
                
            resultado = f"{cuerpo_formateado}-{dv}"
        else:
            resultado = limpio

        # 4. Asignar el texto formateado y devolver el cursor al final
        self.input_rut.setText(resultado)
        self.input_rut.setCursorPosition(len(resultado))

        # Volver a conectar la señal
        self.input_rut.textChanged.connect(self._formatear_rut_en_vivo)

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