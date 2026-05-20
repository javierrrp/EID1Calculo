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
            self.vista.txt_procedimiento.clear()
            return

        A = datos["A"]; B= datos["B"]; C = datos["C"]; D = datos["D"]; E = datos["E"]
        self.modelo_conicas = ModeloConicas(A, B, C, D, E)

        tipo = self.modelo_conicas.clasificar_conica()

        elementos = self.modelo_conicas.obtener_elementos_geometricos()

        h, k, lado_der = self.modelo_conicas.completar_cuadrados()
        c_calc, d_calc, e_calc, procedimiento_inverso_txt = self.modelo_conicas.expandir_general(h, k, lado_der)


        self.vista.lbl_titulo.setText(f"Resultado: {tipo}")
        self.vista.txt_procedimiento.setText(self.modelo_conicas.obtener_pasos_texto())
        self.vista.txt_procedimiento_inverso.setText(procedimiento_inverso_txt)
        self.vista.input_centro.setText(elementos["centro"])
        self.vista.input_radio.setText(elementos["radio"])
        self.vista.input_focos.setText(elementos["focos"])

        self.vista.plano.actualizar_figura(h, k)

        if tipo == "Circunferencia":
            # Si es circunferencia, el lado derecho es el Radio al cuadrado
            self.vista.input_focos.setText(f"Radio al cuadrado = {lado_der}")
        else:
            self.vista.input_focos.setText("Focos por calcular...")