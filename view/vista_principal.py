import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame,
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont


# ─────────────────────────────────────────────────────────────
#  Paleta (extraída del HTML de referencia)
# ─────────────────────────────────────────────────────────────
BG        = "#F8F7F4"
SURFACE   = "#FFFFFF"
SURFACE2  = "#F1EFE8"
BORDER    = "rgba(0,0,0,0.10)"
TEXT_PRI  = "#1A1917"
TEXT_SEC  = "#5F5E5A"
TEXT_MUT  = "#9B9A95"

RUT       = "#185FA5"
RUT_LIGHT = "#E6F1FB"
RUT_MID   = "#378ADD"

CON       = "#993C1D"
CON_LIGHT = "#FAECE7"
CON_MID   = "#D85A30"

LIM       = "#854F0B"
LIM_LIGHT = "#FAEEDA"
LIM_MID   = "#BA7517"


class NavButton(QPushButton):
    """Botón de navegación lateral con colores de acento según módulo."""

    def __init__(self, text: str, index: int, accent: str, accent_light: str, accent_mid: str):
        super().__init__()
        self.index = index
        self._accent       = accent
        self._accent_light = accent_light
        self._accent_mid   = accent_mid
        self.setCheckable(True)
        self.setMinimumHeight(42)
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_style(False)

    def _refresh_style(self, checked: bool):
        if checked:
            bg    = self._accent_light
            color = self._accent
        else:
            bg    = "transparent"
            color = TEXT_SEC

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: none;
                border-radius: 8px;
                color: {color};
                font-weight: 500;
                font-size: 12px;
                padding: 9px 10px;
                text-align: left;
                margin-bottom: 2px;
            }}
            QPushButton:hover {{
                background-color: {self._accent_light if not checked else bg};
                color: {self._accent};
            }}
            QPushButton:checked {{
                background-color: {self._accent_light};
                color: {self._accent};
            }}
        """)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._refresh_style(checked)


class VistaPrincipal(QMainWindow):
    cambiar_vista_solicitada = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAT1186 | Engine Matemático Creativo")
        self.setMinimumSize(1200, 760)

        self.clr_rut = RUT
        self.clr_con = CON
        self.clr_lim = LIM
        self._modulos_habilitados = False

        self.init_ui()

    # ── construcción de la UI ──────────────────────────────────
    def init_ui(self):
        # Fondo general (--bg)
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet(f"background-color: {BG};")
        self.setCentralWidget(self.main_widget)

        self.layout_master = QHBoxLayout(self.main_widget)
        self.layout_master.setContentsMargins(20, 20, 20, 20)
        self.layout_master.setSpacing(20)

        # ── SIDEBAR ──────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: #FAFAF8;
                border: 0.5px solid #D0CECC;
                border-radius: 14px;
            }}
        """)
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(18)
        sidebar_shadow.setColor(QColor(0, 0, 0, 18))
        sidebar_shadow.setOffset(0, 4)
        self.sidebar.setGraphicsEffect(sidebar_shadow)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Branding
        brand_frame = QFrame()
        brand_frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 0.5px solid #D0CECC;
                padding: 0px;
            }}
        """)
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(18, 20, 18, 16)
        brand_layout.setSpacing(2)

        self.lbl_logo = QLabel("UCT · EID1")
        self.lbl_logo.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 17px; font-weight: 500; letter-spacing: -0.3px;"
            " border: none;"
        )

        self.lbl_sub = QLabel("CÁLCULO · GRUPO 03")
        self.lbl_sub.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 400;"
            " letter-spacing: 1.5px; border: none;"
        )

        brand_layout.addWidget(self.lbl_logo)
        brand_layout.addWidget(self.lbl_sub)
        sidebar_layout.addWidget(brand_frame)

        # Sección de navegación
        nav_section = QFrame()
        nav_section.setStyleSheet("QFrame { background: transparent; border: none; }")
        nav_sec_layout = QVBoxLayout(nav_section)
        nav_sec_layout.setContentsMargins(12, 14, 12, 8)
        nav_sec_layout.setSpacing(2)

        nav_label = QLabel("MÓDULOS")
        nav_label.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; letter-spacing: 1.5px;"
            " padding: 0px 6px 6px 6px; border: none;"
        )
        nav_sec_layout.addWidget(nav_label)

        self.btn_rut = NavButton("Validación de RUT",    0, RUT, RUT_LIGHT, RUT_MID)
        self.btn_conicas = NavButton("Geometría de cónicas", 1, CON, CON_LIGHT, CON_MID)
        self.btn_limites = NavButton("Cálculo de límites",   2, LIM, LIM_LIGHT, LIM_MID)

        self.botones = [self.btn_rut, self.btn_conicas, self.btn_limites]
        for btn in self.botones:
            btn.clicked.connect(lambda checked, b=btn: self.cambiar_pestana(b.index))
            nav_sec_layout.addWidget(btn)

        sidebar_layout.addWidget(nav_section)
        sidebar_layout.addStretch()

        # Pie del sidebar
        foot_frame = QFrame()
        foot_frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-top: 0.5px solid #D0CECC;
            }}
        """)
        foot_layout = QVBoxLayout(foot_frame)
        foot_layout.setContentsMargins(18, 14, 18, 14)

        self.lbl_grupo = QLabel("MAT1186 · 2025")
        self.lbl_grupo.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; border: none;"
        )
        foot_layout.addWidget(self.lbl_grupo)
        sidebar_layout.addWidget(foot_frame)

        self.layout_master.addWidget(self.sidebar)

        # ── ÁREA PRINCIPAL ──────────────────────────────────
        self.content_area = QVBoxLayout()
        self.content_area.setSpacing(12)

        # Cabecera (topbar)
        self.header_card = QFrame()
        self.header_card.setFixedHeight(50)
        self.header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE2};
                border: 0.5px solid #D0CECC;
                border-radius: 10px;
            }}
        """)
        h_header = QHBoxLayout(self.header_card)
        h_header.setContentsMargins(14, 0, 14, 0)
        h_header.setSpacing(12)

        # Acento vertical azul
        self._topbar_accent = QFrame()
        self._topbar_accent.setFixedSize(3, 22)
        self._topbar_accent.setStyleSheet(f"background-color: {RUT_MID}; border-radius: 2px;")
        h_header.addWidget(self._topbar_accent)

        self.lbl_seccion = QLabel("BIENVENIDO AL SISTEMA")
        self.lbl_seccion.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 13px; font-weight: 500;"
        )
        h_header.addWidget(self.lbl_seccion)
        h_header.addStretch()

        # Badge de módulo
        self._badge = QLabel("Módulo 11")
        self._badge.setStyleSheet(f"""
            color: {RUT};
            background-color: {RUT_LIGHT};
            font-size: 10px; font-weight: 500;
            padding: 3px 8px; border-radius: 5px;
        """)
        h_header.addWidget(self._badge)

        self.content_area.addWidget(self.header_card)

        # Contenedor de vistas (stacked)
        self.view_container = QFrame()
        self.view_container.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE};
                border: 0.5px solid #C8C6BE;
                border-radius: 14px;
            }}
        """)
        view_shadow = QGraphicsDropShadowEffect()
        view_shadow.setBlurRadius(22)
        view_shadow.setColor(QColor(0, 0, 0, 16))
        view_shadow.setOffset(0, 4)
        self.view_container.setGraphicsEffect(view_shadow)

        self.layout_stack = QVBoxLayout(self.view_container)
        self.layout_stack.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")
        self.layout_stack.addWidget(self.stacked_widget)

        self.content_area.addWidget(self.view_container)
        self.layout_master.addLayout(self.content_area)

        self.cambiar_pestana(0)

    # ── lógica de navegación ───────────────────────────────────
    def cambiar_pestana(self, index: int):
        if index < 0 or index >= len(self.botones):
            return

        if index in (1, 2) and not self._modulos_habilitados:
            self.botones[index].setChecked(False)
            msg = QMessageBox(self)
            msg.setWindowTitle("Acceso bloqueado")
            msg.setText("⚠️  Primero debes validar un RUT.")
            msg.setInformativeText(
                "Ingresa un RUT válido en el módulo de Validación "
                "antes de acceder a Cónicas o Límites."
            )
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
            return

        for i, btn in enumerate(self.botones):
            btn.setChecked(i == index)

        titulos  = ["Validación de Identidad", "Geometría de Cónicas", "Cálculo de Límites"]
        accents  = [RUT_MID, CON_MID, LIM_MID]
        badges   = ["Módulo 11", "Módulo Cónicas", "Módulo Límites"]
        badge_bg = [RUT_LIGHT, CON_LIGHT, LIM_LIGHT]
        badge_fg = [RUT, CON, LIM]

        self.lbl_seccion.setText(titulos[index])
        self.lbl_seccion.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 13px; font-weight: 500;"
        )
        self._topbar_accent.setStyleSheet(
            f"background-color: {accents[index]}; border-radius: 2px;"
        )
        self._badge.setText(badges[index])
        self._badge.setStyleSheet(f"""
            color: {badge_fg[index]};
            background-color: {badge_bg[index]};
            font-size: 10px; font-weight: 500;
            padding: 3px 8px; border-radius: 5px;
        """)

        self.stacked_widget.setCurrentIndex(index)
        self.cambiar_vista_solicitada.emit(index)

    def navegar(self, index: int):
        """Compatibilidad con código antiguo."""
        self.cambiar_pestana(index)

    def agregar_vista(self, widget_vista):
        """Inyecta sub-widgets enviados desde el controlador."""
        widget_vista.setStyleSheet("background: transparent;")
        self.stacked_widget.addWidget(widget_vista)

    def habilitar_modulos(self, habilitar: bool):
        self._modulos_habilitados = habilitar
