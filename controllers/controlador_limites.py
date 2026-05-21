
from models.modelo_limites import ModeloLimites
from view.vista_limites import VistaLimites

class ControladorLimites:
    def __init__(self, ctrl_rut):
        self.ctrl_rut = ctrl_rut
        self.vista = VistaLimites()  # Instanciada para calzar con self.ctrl_limites.vista en el Principal
        self.modelo_propio = ModeloLimites()

    def ejecutar_modulo(self):
        """Método gatillado al pulsar el botón lateral en la barra de navegación"""
        self.procesar_y_actualizar()

    def procesar_y_actualizar(self):
        cuerpo_rut = None
        
        # Nivel 1: Intentar rescatar desde el modelo interno del Controlador de RUT (Estándar de tu compañero)
        if hasattr(self.ctrl_rut, 'modelo') and self.ctrl_rut.modelo:
            modelo_g = self.ctrl_rut.modelo
            if hasattr(modelo_g, 'rut_limpio') and modelo_g.rut_limpio:
                cuerpo_rut = modelo_g.rut_limpio
            elif hasattr(modelo_g, 'cuerpo') and modelo_g.cuerpo:
                cuerpo_rut = modelo_g.cuerpo
            elif hasattr(modelo_g, 'rut') and modelo_g.rut:
                cuerpo_rut = modelo_g.rut

        # Nivel 2: Buscar en las propiedades raíz del controlador de RUT
        if not cuerpo_rut:
            if hasattr(self.ctrl_rut, 'rut_limpio') and self.ctrl_rut.rut_limpio:
                cuerpo_rut = self.ctrl_rut.rut_limpio
            elif hasattr(self.ctrl_rut, 'cuerpo') and self.ctrl_rut.cuerpo:
                cuerpo_rut = self.ctrl_rut.cuerpo

        # Nivel 3: Fuerza bruta (Ir a la interfaz gráfica a sacar el texto directamente del cuadro de ingreso)
        if not cuerpo_rut:
            if hasattr(self.ctrl_rut, 'vista') and self.ctrl_rut.vista:
                vista_r = self.ctrl_rut.vista
                # Escanea los nombres comunes que tu compañero pudo ponerle al QLineEdit del RUT
                for attr_name in ['input_rut', 'txt_rut', 'rut_input', 'line_edit_rut']:
                    if hasattr(vista_r, attr_name):
                        widget = getattr(vista_r, attr_name)
                        if hasattr(widget, 'text'):
                            cuerpo_rut = widget.text()
                            break

        if cuerpo_rut:
            # 1. Limpiar el RUT por seguridad (quitar puntos, guiones, espacios y la K si existiera)
            rut_numerico = "".join(caracter for caracter in str(cuerpo_rut) if caracter.isdigit())
            
            # Solo procesar si el string resultante contiene números válidos para los límites
            if len(rut_numerico) >= 4:
                # 2. Enviar el RUT limpio al modelo analítico de límites para calcular los tramos
                self.modelo_propio.configurar_desde_rut(rut_numerico)
                
                # 3. Forzar a la vista limpia a poblar la tabla y redibujar el lienzo con QPainter
                self.vista.mostrar_datos_modulo_limites(self.modelo_propio)