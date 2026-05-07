# controllers/controlador_principal.py
from view.vista_principal import VistaPrincipal
from models.modelo_matematico import ModeloMatematico
from controllers.controlador_rut import ControladorRut
# Importa los demás controladores...

class ControladorPrincipal:
    def __init__(self):
        # 1. El Modelo (Motor matemático manual) [cite: 98, 99]
        self.modelo = ModeloMatematico()
        
        # 2. La Vista Maestra (La que diseñamos con colores alegres) 
        self.vista_principal = VistaPrincipal()
        
        # 3. Los controladores hijos
        self.ctrl_rut = ControladorRut(self.modelo)
        # self.ctrl_conicas = ControladorConicas(self.modelo)
        # self.ctrl_limites = ControladorLimites(self.modelo)
        
        # 4. Inyectar las vistas de los hijos en el contenedor [cite: 101, 111]
        self.vista_principal.agregar_vista(self.ctrl_rut.vista)
        # self.vista_principal.agregar_vista(self.ctrl_conicas.vista)
        # self.vista_principal.agregar_vista(self.ctrl_limites.vista)
        
        # 5. ¡ESTA LÍNEA ES LA QUE ABRE LA VENTANA!
        self.vista_principal.show()