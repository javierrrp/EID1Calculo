
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont


class VistaRut(QWidget):
    # Señal que el controlador escucha
    boton_validar_clicado = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    # ──────────────────────────────── UI ──────────────────────────
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(24)

        # ── Tarjeta de entrada ─────────────────────────────────────
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 30px;
                padding: 20px;
            }
        """)
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
                border: 3px solid #F1F5F9;
                border-radius: 20px;
                font-size: 32px;
                font-weight: 900;
                color: #1E293B;
                background-color: #F8FAFC;
            }
            QLineEdit:focus {
                border: 3px solid #4ECDC4;
                background-color: white;
            }
        """)
        self.input_rut.returnPressed.connect(self._emitir_validar)
        card_layout.addWidget(self.input_rut)

        self.btn_validar = QPushButton("VERIFICAR SISTEMA")
        self.btn_validar.setMinimumHeight(60)
        self.btn_validar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validar.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45B7AF; }
            QPushButton:pressed { background-color: #3AA8A0; }
        """)
        self.btn_validar.clicked.connect(self._emitir_validar)
        card_layout.addWidget(self.btn_validar)

        layout.addWidget(card)

        # ── Notebook de pasos (pestañas manuales) ──────────────────
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
                    background-color: #F1F5F9;
                    color: #64748B;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px 16px;
                    border: none;
                }
                QPushButton:checked {
                    background-color: #4ECDC4;
                    color: white;
                }
                QPushButton:hover:!checked { background-color: #E2E8F0; }
            """)
            btn.clicked.connect(lambda _, k=key: self._mostrar_tab(k))
            tabs_row.addWidget(btn)
            self._tabs_btns[key] = btn

        tabs_row.addStretch()
        layout.addLayout(tabs_row)

        # Área de contenido de pestañas
        self._stack = QFrame()
        self._stack.setMinimumHeight(260)
        self._stack_layout = QVBoxLayout(self._stack)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)

        for key in ["validacion", "variable_v", "ecuacion"]:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { border: none; border-radius: 20px; }
                QScrollBar:vertical { width: 6px; background: #F1F5F9; }
                QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 3px; }
            """)
            lbl = QLabel("Esperando datos de entrada...")
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            lbl.setStyleSheet("""
                QLabel {
                    background-color: #1E293B;
                    color: #A5F3FC;
                    font-family: 'Consolas', 'Courier New';
                    font-size: 13px;
                    padding: 20px;
                    border-radius: 20px;
                    border-left: 5px solid #4ECDC4;
                }
            """)
            scroll.setWidget(lbl)
            self._stack_layout.addWidget(scroll)
            self._tabs_content[key] = (scroll, lbl)

        # Pestaña resultado (diseño especial)
        res_frame = QFrame()
        res_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 16px;
            }
        """)
        self._apply_shadow(res_frame)
        res_layout = QVBoxLayout(res_frame)

        self.lbl_estado = QLabel("—")
        self.lbl_estado.setStyleSheet("font-size: 16px; font-weight: bold; color: #94A3B8;")
        res_layout.addWidget(self.lbl_estado)

        self.lbl_tipo_conica = QLabel("—")
        self.lbl_tipo_conica.setStyleSheet(
            "font-size: 28px; font-weight: 900; color: #4ECDC4;"
        )
        res_layout.addWidget(self.lbl_tipo_conica)

        self.lbl_ecuacion = QLabel("—")
        self.lbl_ecuacion.setWordWrap(True)
        self.lbl_ecuacion.setStyleSheet(
            "font-family: 'Consolas'; font-size: 14px; color: #1E293B; "
            "background: #F8FAFC; border-radius: 12px; padding: 12px;"
        )
        res_layout.addWidget(self.lbl_ecuacion)

        self.lbl_explicacion = QLabel("—")
        self.lbl_explicacion.setWordWrap(True)
        self.lbl_explicacion.setStyleSheet("font-size: 12px; color: #64748B;")
        res_layout.addWidget(self.lbl_explicacion)

        self._stack_layout.addWidget(res_frame)
        self._tabs_content["resultado"] = res_frame

        layout.addWidget(self._stack)
        layout.addStretch()

        # Mostrar primera pestaña por defecto
        self._mostrar_tab("validacion")

    # ─────────────────────────────── slots públicos ────────────────
    def mostrar_resultado(self, exito: bool, log_validacion: str):
        """Llamado por el controlador con el resultado de la validación."""
        color_borde = "#4ECDC4" if exito else "#FF6B6B"
        color_texto = "#A5F3FC" if exito else "#FECACA"
        estilo_consola = (
            f"background-color: #1E293B; color: {color_texto}; "
            f"font-family: 'Consolas', 'Courier New'; font-size: 13px; "
            f"padding: 20px; border-radius: 20px; border-left: 5px solid {color_borde};"
        )
        scroll, lbl = self._tabs_content["validacion"]
        lbl.setStyleSheet(estilo_consola)
        lbl.setText(log_validacion)

        if exito:
            self.lbl_estado.setText("✓  RUT VÁLIDO")
            self.lbl_estado.setStyleSheet("font-size: 16px; font-weight: bold; color: #22C55E;")
        else:
            self.lbl_estado.setText("✗  RUT INVÁLIDO")
            self.lbl_estado.setStyleSheet("font-size: 16px; font-weight: bold; color: #EF4444;")
            self.lbl_tipo_conica.setText("—")
            self.lbl_ecuacion.setText("—")
            self.lbl_explicacion.setText("—")

        self._mostrar_tab("validacion")

    def mostrar_variable_v(self, log_v: str):
        """Llamado por el controlador para mostrar el cálculo de v."""
        _, lbl = self._tabs_content["variable_v"]
        lbl.setStyleSheet(lbl.styleSheet())
        lbl.setText(log_v)

    def mostrar_ecuacion(self, log_ec: str):
        """Llamado por el controlador para mostrar la construcción de la ecuación."""
        _, lbl = self._tabs_content["ecuacion"]
        lbl.setText(log_ec)

    def mostrar_conica(self, tipo: str, ecuacion_str: str, explicacion: str):
        """Llamado por el controlador para mostrar la cónica clasificada."""
        self.lbl_tipo_conica.setText(tipo)
        self.lbl_ecuacion.setText(ecuacion_str)
        self.lbl_explicacion.setText(explicacion)

    # ─────────────────────────────── helpers privados ─────────────
    def _emitir_validar(self):
        self.boton_validar_clicado.emit(self.input_rut.text())

    def _mostrar_tab(self, key: str):
        # Ocultar todo
        for k, widget in self._tabs_content.items():
            w = widget[0] if isinstance(widget, tuple) else widget
            w.setVisible(False)
            if k in self._tabs_btns:
                self._tabs_btns[k].setChecked(False)

        # Mostrar seleccionado
        w = self._tabs_content[key]
        (w[0] if isinstance(w, tuple) else w).setVisible(True)
        self._tabs_btns[key].setChecked(True)

    def _apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)
