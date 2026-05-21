from view.vista_principal import VistaPrincipal
from models.modelo_matematico import ModeloMatematico
from controllers.controlador_rut import ControladorRut
from controllers.controlador_conicas import ControladorConicas
from controllers.controlador_limites import ControladorLimites 

class ControladorPrincipal:
    def __init__(self):
        # 1. El Modelo general de la aplicación
        self.modelo = ModeloMatematico()
        
        # 2. La Vista Maestra (Contenedor de ventanas con barra lateral)
        self.vista_principal = VistaPrincipal()
        
        # 3. Los controladores hijos vinculados
        self.ctrl_rut = ControladorRut(self.modelo)
        self.ctrl_conicas = ControladorConicas(self.ctrl_rut)
        self.ctrl_limites = ControladorLimites(self.ctrl_rut)
        
        # 4. Inyectar los sub-widgets de las vistas en el QStackedWidget secuencialmente
        self.vista_principal.agregar_vista(self.ctrl_rut.vista)      # Índice 0
        self.vista_principal.agregar_vista(self.ctrl_conicas.vista)  # Índice 1
        self.vista_principal.agregar_vista(self.ctrl_limites.vista)  # Índice 2

        # 5. Conexión de eventos y sincronización de Pestañas
        
        # Botón RUT (Índice 0): Navegación pura a la zona de ingreso
        self.vista_principal.botones[0].clicked.connect(
            lambda: self.vista_principal.cambiar_pestana(0)
        )
        
        # Botón Cónicas (Índice 1): Ejecuta cálculos algorítmicos y cambia la vista
        self.vista_principal.botones[1].clicked.connect(self.conmutar_modulo_conicas)
        
        # Botón Límites (Índice 2): Ejecuta aproximaciones numéricas, renderiza traza gráfica y cambia la vista
        self.vista_principal.botones[2].clicked.connect(self.conmutar_modulo_limites)

        # Desplegar la aplicación una vez configurada la arquitectura
        self.vista_principal.show()

    def conmutar_modulo_conicas(self):
        self.ctrl_conicas.ejecutar_modulo()
        self.vista_principal.cambiar_pestana(1)

    def conmutar_modulo_limites(self):
        self.ctrl_limites.ejecutar_modulo()
        self.vista_principal.cambiar_pestana(2)