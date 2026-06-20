from view.vista_conicas import VistaConicas
from models.modelo_conicas import ModeloConicas, ErrorConicas
from controllers.controlador_rut import ControladorRut
from PyQt6.QtWidgets import QMessageBox

class ControladorConicas:
    def __init__(self, controlador_rut):
        self.vista = VistaConicas()
        self.controlador_rut = controlador_rut
        self.modelo_conicas = None
        self.elementos_correctos = None

        self.vista.btn_verificar.clicked.connect(self.verificar)


    def ejecutar_modulo(self):
        
        # Obtiene y valida datos del RUT 
        datos = self.controlador_rut.datos_ecuacion

        llaves_requeridas = ["A", "B", "C", "D", "E"]
        if datos is None or not all(k in datos for k in llaves_requeridas):
            self.vista.lbl_titulo.setText("Error: Faltan datos matemáticos para procesar la cónica.")            
            self.vista.txt_procedimiento.clear()
            self.vista.txt_procedimiento_inverso.clear()
            return

        A = datos["A"]; B= datos["B"]; C = datos["C"]; D = datos["D"]; E = datos["E"]

        # Crea el modelo con validación interna 
        try:
            self.modelo_conicas = ModeloConicas(A, B, C, D, E)
        except ErrorConicas as exc:
            self._limpiar_vista(f"Error al crear el modelo de conica:\n{exc}")
            return
        except Exception as exc:
            self._limpiar_vista(f"Error inesperado al inicializar conicas:\n{exc}")
            return
        
        # Clasifica la cónica 
        try:
            tipo = self.modelo_conicas.clasificar_conica()
        except ErrorConicas as exc:
            self._limpiar_vista(f"Error al clasificar la cónica:\n{exc}")
            return
        
        # Obtiene los elementos geométricos
        try: 
            self.elementos_correctos = self.modelo_conicas.obtener_elementos_geometricos()
        except ErrorConicas as exc:
            self.elementos_correctos = None
            self._mostrar_advertencia(
                "Advertencia en elementos geométricos",
                f"Se pudo clasificar la cónica como «{tipo}», pero ocurrió un error "
                f"al calcular los elementos geométricos:\n\n{exc}\n\n"
                f"El procedimiento de completar el cuadrado se mostrará de todas formas."
            )

        # Completa los cuadrados para llevar a forma canónica
       
        try:
            h, k, lado_der = self.modelo_conicas.completar_cuadrados()
        except ErrorConicas as exc:
            self._limpiar_vista(f"Error al completar los cuadrados:\n{exc}")
            return


        # Expansión inversa para mostrar el procedimiento inverso  
        try: 
            c_calc, d_calc, e_calc, procedimiento_inverso_txt = self.modelo_conicas.expandir_general(h, k, lado_der)
        except ErrorConicas as exc:
            procedimiento_inverso_txt = (f"No se pudo generar el procedimiento inverso.\nDetalle: {exc}")

        # Actualiza la vista con toda la información obtenida
        self.vista.lbl_titulo.setText(f"Resultado: {tipo}")
        self.vista.txt_procedimiento.setText(self.modelo_conicas.obtener_pasos_texto())
        self.vista.txt_procedimiento_inverso.setText(procedimiento_inverso_txt)

        # Muestra solo campos del tipo actual
        self.vista.plano.mostrar_campos_segun_conica(tipo)

        # Vacia los campos para llenarlos
        self.vista.input_centro.clear()
        self.vista.input_radio.clear()
        self.vista.input_focos.clear()


        # Dibuja en el plano cartesiano 
        try: 
            if tipo == "Circunferencia":
            # Si es circunferencia, el lado derecho es el Radio al cuadrado
                radio_float = lado_der ** 0.5 if lado_der > 0 else 0
                self.vista.plano.actualizar_figura(h, k, tipo, radio_float)
            else:
                self.vista.plano.actualizar_figura(h, k, tipo)
        except Exception as exc:
            self._mostrar_advertencia(
                "Error al dibujar la figura",
                f"Los cálculos son correctos, pero no se pudo renderizar la figura:\n{exc}"
            )

    # Verifiación de respuestas del usuario contra la verdad del modelo
    def verificar(self):
        if not self.elementos_correctos:
            msg = QMessageBox(self.vista)
            msg.setWindowTitle("Aviso")
            msg.setText("Primero evalua un rut para tener un caso activo")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
                QMessageBox { background-color: white; }
                QLabel { color: #000000; font-size: 14px; font-weight: bold; }
                QPushButton {
                    background-color: #3B82F6; color: white;
                    padding: 6px 15px; border-radius: 5px; min-width: 80px;
                }
            """)
            msg.exec()
            return
 
        # Leemos lo que el usuario ingresó en los campos
        resp_centro = self.vista.input_centro.text().strip()
        resp_radio  = self.vista.input_radio.text().strip()


        # Verifica si hay campos vacios
        campos_vacios = []
        if self.vista.input_centro.isVisible() and not resp_centro:
            campos_vacios.append("• Centro (h, k)")
        if self.vista.input_radio.isVisible() and not resp_radio:
            campos_vacios.append("• Radio")

        if campos_vacios:
            msg = QMessageBox(self.vista)
            msg.setWindowTitle("Campos incompletos")
            msg.setText("Por favor, completa los siguientes campos antes de verificar:\n\n" + "\n".join(campos_vacios))
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
                QMessageBox { background-color: white; }
                QLabel { color: #1E293B; font-size: 13px; font-weight: bold; }
                QPushButton {
                    background-color: #F59E0B; color: white;
                    padding: 6px 15px; border-radius: 5px; min-width: 80px;
                }
                QPushButton:hover { background-color: #D97706; }
            """)
            msg.exec()
            return    
 
        # Leemos la verdad absoluta calculada por el modelo
        real_centro = self.elementos_correctos["centro"]
        real_radio  = self.elementos_correctos["radio"]
 
        mensaje = "--- PANEL --- \n\n"
 
        # Verificamos el centro
        coords_resp = self.extraer_coordenadas(resp_centro)
        coords_real = self.extraer_coordenadas(real_centro)
 
        if coords_resp and coords_real:
            if abs(coords_resp[0] - coords_real[0]) < 0.05 and abs(coords_resp[1] - coords_real[1]) < 0.05:
                mensaje += "✅ Centro: Correcto!\n"
            else:
                mensaje += f"❌ Centro: Incorrecto. Respuesta correcta: {real_centro}\n"
        else:
            mensaje += f"❌ Centro: Incorrecto. Respuesta correcta: {real_centro}\n"
 
        if self.elementos_correctos["tipo"] == "Circunferencia":
            if not resp_radio:
                mensaje += "⚠️ Radio: El campo está vacío.\n"
            else:
                try:
                    num_resp_radio = float(resp_radio)
                    num_real_radio = float(real_radio)
                    if abs(num_resp_radio - num_real_radio) < 0.05:
                        mensaje += "✅ Radio: Correcto!\n"
                    else:
                        mensaje += f"❌ Radio: Incorrecto. Respuesta correcta: {real_radio}\n"
                except ValueError:
                    mensaje += f"❌ Radio: Incorrecto. Respuesta correcta: {real_radio}\n"
 
        self._mostrar_resultado(mensaje)
    
    # Herramienta para extraer coordenadas de un string con formato "(x, y)"
    @staticmethod
    def extraer_coordenadas(texto):
        if not texto:
            return None
        try:
            texto_limpio = texto.replace("(", "").replace(")", "")
            partes = texto_limpio.split(",")
            if len(partes) != 2:
                return None
            return float(partes[0]), float(partes[1])
        except (ValueError, AttributeError):
            return None
            
    def _limpiar_vista(self, mensaje_error: str):
        self.elementos_correctos = None
        self.modelo_conicas = None
        self.vista.lbl_titulo.setText(f"⚠️ {mensaje_error}")
        self.vista.txt_procedimiento.clear()
        self.vista.txt_procedimiento_inverso.clear()
        self.vista.input_centro.clear()
        self.vista.input_radio.clear()
        self.vista.input_focos.clear()

    def _mostrar_advertencia(self, titulo: str, mensaje: str):        
        msg = QMessageBox(self.vista)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox { background-color: white; }
            QLabel { color: #1E293B; font-size: 13px; }
            QPushButton {
                background-color: #3B82F6; color: white;
                padding: 6px 15px; border-radius: 5px; min-width: 80px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        msg.exec()

    def _mostrar_resultado(self, mensaje: str):
        msg_box = QMessageBox(self.vista)
        msg_box.setWindowTitle("Resultados de la verificación")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: white; }
            QLabel { color: #1E293B; font-size: 13px; font-weight: bold; }
            QPushButton {
                background-color: #3B82F6; color: white;
                padding: 6px 15px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2563EB; }
            QPushButton:pressed { background-color: #1D4ED8; }
        """)
        msg_box.exec()
        

    @staticmethod
    def _datos_son_validos(datos: dict | None, llaves: list[str]) -> bool:            
        if datos is None:
            return False
        return all(k in datos for k in llaves)
            