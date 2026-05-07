# controllers/controlador_rut.py
from view.vista_rut import VistaRut
from models.modelo_matematico import ModeloMatematico

class ControladorRut:
    def __init__(self, modelo_compartido):
        self.modelo = modelo_compartido
        self.vista = VistaRut()
        
        # Conectar la señal de la vista con la función de este controlador
        self.vista.boton_validar_clicado.connect(self.procesar_rut)

    def procesar_rut(self, rut_texto):
        # 1. Pedirle al modelo que valide
        exito, log_pasos = self.modelo.validar_rut(rut_texto)
        
        # 2. Decirle a la vista que muestre el resultado
        self.vista.mostrar_resultado(exito, log_pasos)
        
        if exito:
            print("Controlador: RUT Válido, listo para Fases de Cónicas.")
            # Aquí podrías emitir una señal para desbloquear los botones de la VistaPrincipal