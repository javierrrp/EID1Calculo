from view.vista_conicas import VistaConicas
from models.modelo_conicas import ModeloConicas
from controllers.controlador_rut import ControladorRut

class ControladorConicas:
    def __init__(self, controlador_rut):
        self.vista = VistaConicas()
        self.controlador_rut = controlador_rut


    def ejecutar_modulo(self):
        
        datos = self.controlador_rut.datos_ecuacion

        if datos is None:
            self.vista.lbl_titulo.setText("Ingrese un RUT válido en la pestaña RUT para analizar la cónica.")
            return

        A = datos["A"]; B= datos["B"]; C = datos["C"]; D = datos["D"]; E = datos["E"]

        self.modelo_conicas = ModeloConicas(A, B, C, D, E)

        tipo = self.modelo_conicas.clasificar_conica()

        h, k, lado_der = self.modelo_conicas.completar_cuadrados()

        self.vista.lbl_titulo.setText(f"Resultado: {tipo}")
        self.vista.txt_procedimiento.setText(self.modelo_conicas.obtener_pasos_texto())
        self.vista.input_centro.setText(f"({h}, {k})")
    
        if tipo == "Circunferencia":
            # Si es circunferencia, el lado derecho es el Radio al cuadrado
            self.vista.input_focos.setText(f"Radio al cuadrado = {lado_der}")
        else:
            self.vista.input_focos.setText("Focos por calcular...")