from view.vista_conicas import VistaConicas
from models.modelo_conicas import ModeloConicas
from controllers.controlador_rut import ControladorRut
from PyQt6.QtWidgets import QMessageBox

class ControladorConicas:
    def __init__(self, controlador_rut):
        self.vista = VistaConicas()
        self.controlador_rut = controlador_rut
        self.elementos_correctos = None

        self.vista.btn_verificar.clicked.connect(self.verificar)


    def ejecutar_modulo(self):
        
        datos = self.controlador_rut.datos_ecuacion

        llaves_requeridas = ["A", "B", "C", "D", "E"    ]
        if datos is None or not all(k in datos for k in llaves_requeridas):
            self.vista.lbl_titulo.setText("Error: Faltan datos matemáticos para procesar la cónica.")            
            self.vista.txt_procedimiento.clear()
            self.vista.txt_procedimiento_inverso.clear()
            return

        A = datos["A"]; B= datos["B"]; C = datos["C"]; D = datos["D"]; E = datos["E"]
        self.modelo_conicas = ModeloConicas(A, B, C, D, E)

        tipo = self.modelo_conicas.clasificar_conica()

        self.elementos_correctos = self.modelo_conicas.obtener_elementos_geometricos()

        h, k, lado_der = self.modelo_conicas.completar_cuadrados()
        c_calc, d_calc, e_calc, procedimiento_inverso_txt = self.modelo_conicas.expandir_general(h, k, lado_der)


        self.vista.lbl_titulo.setText(f"Resultado: {tipo}")
        self.vista.txt_procedimiento.setText(self.modelo_conicas.obtener_pasos_texto())
        self.vista.txt_procedimiento_inverso.setText(procedimiento_inverso_txt)

        #Vaciar campos para llenarlos
        self.vista.input_centro.clear()
        self.vista.input_radio.clear()
        self.vista.input_focos.clear()


        if tipo == "Circunferencia":
            # Si es circunferencia, el lado derecho es el Radio al cuadrado
            radio_float = lado_der ** 0.5 if lado_der > 0 else 0
            self.vista.plano.actualizar_figura(h, k, tipo, radio_float)
        else:
            self.vista.plano.actualizar_figura(h, k, tipo)
    
    def verificar(self):
        if not self.elementos_correctos:
            msg = QMessageBox(self.vista)
            msg.setWindowTitle("Aviso")
            msg.setText("Primero evalua un rut para tener un caso activo")
            msg.setIcon(QMessageBox.Icon.Warning)

            msg.setStyleSheet("""
                                QMessageBox {
                                    background-color: white;
                                }
                                QLabel {
                                    color: #000000;
                                    font-size: 14px;
                                    font-weight: bold;
                                }

                                QPushButton {
                                    background-color: #3B82F6;
                                    color: white;
                                    padding: 6px 15px;
                                    border-radius: 5px;
                                    min-width: 80px;
                                }
                            """)
            
            msg.exec()
            return
    
        #leemos lo que el usuario ingreso en los campos
        resp_centro = self.vista.input_centro.text().strip()
        resp_radio = self.vista.input_radio.text().strip()

        #leemos la verdad absoluta calculada por el modelo
        real_centro = self.elementos_correctos["centro"]
        real_radio = self.elementos_correctos["radio"]

        mensaje = "--- PANEL --- \n\n"

        def extraer_coordenadas(texto):

            try:
                texto_limpio = texto.replace("(", "").replace(")", "")
                partes = texto_limpio.split(",")
                if len(partes) == 2:
                    return float(partes[0]), float(partes[1])
            except ValueError:
                pass
            return None
        
        coords_resp = extraer_coordenadas(resp_centro)
        coords_real = extraer_coordenadas(real_centro)

        if coords_resp and coords_real:
            if abs(coords_resp[0] - coords_real[0]) < 0.05 and abs(coords_resp[1] - coords_real[1]) < 0.05:
                mensaje += "✅Centro: Correcto! \n"
            else:
                mensaje += f"Centro: Incorrecto. Respuesta correcta: {real_centro} \n"
        else:
            mensaje += f"Centro: Incorrecto. Respuesta correcta: {real_centro} \n"
       
        if self.elementos_correctos["tipo"] == "Circunferencia":
            if not resp_radio:
                mensaje += "⚠️ Radio: El campo está vacío.\n"
            else:
                try:
                    num_resp_radio = float(resp_radio)
                    num_real_radio = float(real_radio)
                    if abs(num_resp_radio - num_real_radio) < 0.05:
                        mensaje += "✅Radio: Correcto! \n"
                    else:
                        mensaje += f"Radio: Incorrecto. Respuesta correcta: {real_radio} \n"
                except ValueError:
                    mensaje += f"Radio: Incorrecto. Respuesta correcta: {real_radio} \n"
                
        msg_box = QMessageBox(self.vista)
        msg_box.setWindowTitle("Resultados")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Le inyectamos CSS puro para evitar que herede la ventana negra
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #1E293B;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 6px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        msg_box.exec()