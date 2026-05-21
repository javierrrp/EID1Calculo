import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

class AnimatedNavButton(QPushButton):
    def __init__(self, text, index, color_hex):
        super().__init__()
        self.index = index
        self.color_hex = color_hex
        self.setCheckable(True)
        self.setMinimumHeight(65)
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 20px;
                color: #475569;
                font-weight: 800;
                font-size: 13px;
                padding: 10px;
                margin: 5px;
            }}
            QPushButton:hover {{
                background-color: {color_hex};
                color: white;
                border: 2px solid {color_hex};
            }}
            QPushButton:checked {{
                background-color: {color_hex};
                color: white;
                border: 2px solid {color_hex};
                font-size: 14px;
            }}
        """)
        
        # Sombra suave para el botón
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class VistaPrincipal(QMainWindow):
    # Señal que mapea la comunicación con el controlador principal
    cambiar_vista_solicitada = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAT1186 | Engine Matemático Creativo")
        self.setMinimumSize(1200, 900)
        
        # Colores de la paleta alegre
        self.clr_rut = "#4ECDC4"   # Turquesa
        self.clr_con = "#FF6B6B"   # Coral
        self.clr_lim = "#FFD93D"   # Amarillo
        
        self.init_ui()

    def init_ui(self):
        # Fondo Principal
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: #F0F9FF;") # Azul nube muy claro
        self.setCentralWidget(self.main_widget)
        
        self.layout_master = QHBoxLayout(self.main_widget)
        self.layout_master.setContentsMargins(20, 20, 20, 20)
        self.layout_master.setSpacing(20)

        # --- PANEL LATERAL (Sidebar Curvo) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 30px;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 40)

        # Branding Alegre
        logo_container = QVBoxLayout()
        self.lbl_logo = QLabel("UCT")
        self.lbl_logo.setStyleSheet("color: #3B82F6; font-size: 40px; font-weight: 900; margin-bottom: -10px;")
        
        self.lbl_sub = QLabel("MATEMÁTICA CREATIVA")
        self.lbl_sub.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: bold; letter-spacing: 2px;")
        
        logo_container.addWidget(self.lbl_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        logo_container.addWidget(self.lbl_sub, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addLayout(logo_container)
        
        sidebar_layout.addSpacing(60)

        # Botones de Navegación
        self.btn_rut = AnimatedNavButton("VALIDACIÓN DE IDENTIDAD", 0, self.clr_rut)
        self.btn_conicas = AnimatedNavButton("GEOMETRÍA DE CÓNICAS", 1, self.clr_con)
        self.btn_limites = AnimatedNavButton("CÁLCULO DE LÍMITES", 2, self.clr_lim)
        
        self.botones = [self.btn_rut, self.btn_conicas, self.btn_limites]
        for btn in self.botones:
            # Vincula el clic del botón con el método de navegación
            btn.clicked.connect(lambda checked, b=btn: self.cambiar_pestana(b.index))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        
        # Etiqueta de Grupo
        self.lbl_grupo = QLabel("Diseñado por Grupo 03")
        self.lbl_grupo.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: bold;")
        sidebar_layout.addWidget(self.lbl_grupo, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout_master.addWidget(self.sidebar)

        # --- ÁREA DE TRABAJO (Glassmorphism) ---
        self.content_area = QVBoxLayout()
        
        # Cabecera Dinámica
        self.header_card = QFrame()
        self.header_card.setFixedHeight(80)
        self.header_card.setStyleSheet("background-color: white; border-radius: 20px;")
        h_header = QHBoxLayout(self.header_card)
        
        self.lbl_seccion = QLabel("BIENVENIDO AL SISTEMA")
        self.lbl_seccion.setStyleSheet("color: #1E293B; font-size: 22px; font-weight: 800; margin-left: 20px;")
        h_header.addWidget(self.lbl_seccion)
        
        self.content_area.addWidget(self.header_card)

        # Contenedor de Vistas Principal
        self.view_container = QFrame()
        self.view_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.6);
                border: 2px solid white;
                border-radius: 40px;
            }
        """)
        
        # Sombra de profundidad
        view_shadow = QGraphicsDropShadowEffect()
        view_shadow.setBlurRadius(30)
        view_shadow.setColor(QColor(0, 100, 200, 20))
        self.view_container.setGraphicsEffect(view_shadow)
        
        self.layout_stack = QVBoxLayout(self.view_container)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")
        self.layout_stack.addWidget(self.stacked_widget)
        
        self.content_area.addWidget(self.view_container)
        self.layout_master.addLayout(self.content_area)

        # Inicializar en la pestaña del RUT por defecto
        self.cambiar_pestana(0)

    def cambiar_pestana(self, index):
        """
        SOLUCIÓN AL CRASH: Método mediador requerido explícitamente por el controlador.
        Gestiona el cambio de índices en el QStackedWidget y actualiza la UI.
        """
        # Validar rango para evitar fallos de índice si una vista no se ha inyectado aún
        if index < 0 or index >= len(self.botones):
            return

        # Sincronizar estados visuales de los botones laterales
        for i, btn in enumerate(self.botones):
            btn.setChecked(i == index)
        
        titulos = ["Validación de Identidad", "Geometría de Cónicas", "Cálculo de Límites"]
        colores = [self.clr_rut, self.clr_con, self.clr_lim]
        
        # Actualizar dinámicamente el estilo y texto de la cabecera superior
        self.lbl_seccion.setText(titulos[index].upper())
        self.lbl_seccion.setStyleSheet(f"color: {colores[index]}; font-size: 22px; font-weight: 800; margin-left: 20px;")
        
        # Conmutar la pantalla activa en el Stacked Widget
        self.stacked_widget.setCurrentIndex(index)
        
        # Notificar al controlador principal en caso de que requiera refrescar datos del modelo
        self.cambiar_vista_solicitada.emit(index)

    def navegar(self, index):
        """Mantener compatibilidad por si otros submódulos llaman al antiguo nombre"""
        self.cambiar_pestana(index)

    def agregar_vista(self, widget_vista):
        """Inyecta los sub-widgets (RUT, Cónicas, Límites) enviados desde el Main/Controlador"""
        widget_vista.setStyleSheet("background: transparent;")
        self.stacked_widget.addWidget(widget_vista)