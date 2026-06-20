from models.modelo_limites import ModeloLimites
from view.vista_limites import VistaLimites
from PyQt6.QtWidgets import QMessageBox

class ControladorLimites:
    def __init__(self, ctrl_rut):
        self.ctrl_rut = ctrl_rut
        self.vista = VistaLimites() 
        self.modelo_propio = ModeloLimites()
        
        # Escucha el clic del botón de verificación
        self.vista.btn_validar.clicked.connect(self.procesar_evaluacion_estudiante)

    def ejecutar_modulo(self):
        # Método gatillado al pulsar el botón lateral en la barra de navegación
        self.procesar_y_actualizar()

    def procesar_y_actualizar(self):
        cuerpo_rut = None
        
        # Rescata desde el modelo interno del Controlador de RUT
        if hasattr(self.ctrl_rut, 'modelo') and self.ctrl_rut.modelo:
            modelo_g = self.ctrl_rut.modelo
            if hasattr(modelo_g, 'rut_limpio') and modelo_g.rut_limpio:
                cuerpo_rut = modelo_g.rut_limpio
            elif hasattr(modelo_g, 'cuerpo') and modelo_g.cuerpo:
                cuerpo_rut = modelo_g.cuerpo
            elif hasattr(modelo_g, 'rut') and modelo_g.rut:
                cuerpo_rut = modelo_g.rut

        # Busca en las propiedades raíz del controlador de RUT
        if not cuerpo_rut:
            if hasattr(self.ctrl_rut, 'rut_limpio') and self.ctrl_rut.rut_limpio:
                cuerpo_rut = self.ctrl_rut.rut_limpio
            elif hasattr(self.ctrl_rut, 'cuerpo') and self.ctrl_rut.cuerpo:
                cuerpo_rut = self.ctrl_rut.cuerpo

        # Va a la interfaz gráfica a sacar el texto del campo
        if not cuerpo_rut:
            if hasattr(self.ctrl_rut, 'vista') and self.ctrl_rut.vista:
                vista_r = self.ctrl_rut.vista
                for attr_name in ['input_rut', 'txt_rut', 'rut_input', 'line_edit_rut']:
                    if hasattr(vista_r, attr_name):
                        widget = getattr(vista_r, attr_name)
                        if hasattr(widget, 'text'):
                            cuerpo_rut = widget.text()
                            break

        if cuerpo_rut:
            # Limpia el RUT por seguridad
            rut_numerico = "".join(caracter for caracter in str(cuerpo_rut) if caracter.isdigit())
            
            if len(rut_numerico) >= 4:
                # Sincroniza y configura el modelo analítico de límites con el RUT real
                self.modelo_propio.configurar_desde_rut(rut_numerico)
                
                # Sincroniza la vista guardando el modelo activo tanto en la vista como en el controlador
                self.vista.modelo_actual = self.modelo_propio
                
                # Forza a la vista a poblar la tabla y redibujar el lienzo interactivo
                self.vista.mostrar_datos_modulo_limites(self.modelo_propio)

    def procesar_evaluacion_estudiante(self):
        # Garantiza que usamos el modelo que actualmente generó los datos en pantalla
        if hasattr(self.vista, 'modelo_actual') and self.vista.modelo_actual is not None:
            modelo_evaluacion = self.vista.modelo_actual
        else:
            modelo_evaluacion = self.modelo_propio

        # Captura entradas reales de la interfaz (normalizadas a minúsculas y tolerantes a comas)
        ans_izq = self.vista.input_lim_izq.text().strip().lower().replace(",", ".")
        ans_der = self.vista.input_lim_der.text().strip().lower().replace(",", ".")
        ans_existe = self.vista.combo_existe.currentText().strip()
        ans_fa = self.vista.input_fa.text().strip().lower().replace(",", ".")
        ans_clasificacion_idx = self.vista.combo_continuidad.currentIndex()

        # Control estricto de campos vacíos o sin seleccionar
        if (not ans_izq or not ans_der or ans_existe in ["[ Seleccione ]", ""] or 
            not ans_fa or ans_clasificacion_idx <= 0):
            
            self.actualizar_barra_feedback("✗ ERROR: Debes completar todos los casilleros de verificación.", "#FEE2E2", "#991B1B", "#FCA5A5")
            
            # Advertencia de campos vacíos estilizada de forma rápida
            msg_campos = QMessageBox(self.vista)
            msg_campos.setWindowTitle("Campos Incompletos")
            msg_campos.setText("<h3 style='color: #B45309;'>Campos Faltantes</h3>Por favor, responda todas las preguntas del formulario antes de verificar.")
            msg_campos.setStyleSheet("QMessageBox { background-color: #FFFFFF; } QPushButton { background-color: #D97706; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold; }")
            msg_campos.exec()
            return

        # Obtiene los límites analíticos exactos desde el modelo sincronizado
        lim_izq_teorico, lim_der_teorico, existe_teorico = modelo_evaluacion.obtener_limites_teoricos()
        
        errores = []

        # Valida Límite por la izquierda 
        try:
            if lim_izq_teorico in [float('-inf'), "-inf"]:
                if '-inf' not in ans_izq and 'infinito' not in ans_izq and '-' not in ans_izq:
                    errores.append("- El límite por izquierda debe tender a -infinito (-inf).")
            else:
                if abs(float(ans_izq) - float(lim_izq_teorico)) > 0.05:
                    errores.append("- El valor numérico del límite por izquierda es incorrecto.")
        except ValueError:
            errores.append("- Formato inválido en 'Lim (x→a⁻)'. Debe ser un número o '-inf'.")

        # Valida Límite por la derecha
        try:
            if lim_der_teorico in [float('inf'), "inf"]:
                if 'inf' not in ans_der or '-inf' in ans_der:
                    errores.append("- El límite por derecha debe tender a +infinito (inf).")
            else:
                if abs(float(ans_der) - float(lim_der_teorico)) > 0.05:
                    errores.append("- El valor numérico del límite por derecha es incorrecto.")
        except ValueError:
            errores.append("- Formato inválido en 'Lim (x→a⁺)'. Debe ser un número o 'inf'.")

        # Valida la existencia del límite global 
        str_existe_esperado = "Sí" if existe_teorico else "No"
        if ans_existe.lower() != str_existe_esperado.lower():
            errores.append(f"- Conclusión de existencia errónea. El límite global { 'SÍ' if existe_teorico else 'NO' } existe.")

        # Valida el valor de la función en el punto f(a) 
        if modelo_evaluacion.caso in [1, 3]:
            # Flexibilidad de sinonimia admitida para el campo "No existe"
            terminos_no_existe = ["no existe", "indef", "none", "no", "no definida", "n/a", "indefinido"]
            if not any(t in ans_fa for t in terminos_no_existe):
                errores.append(f"- f({modelo_evaluacion.a}) no está definida en este campo real ('No existe').")
        elif modelo_evaluacion.caso == 2:
            d4 = modelo_evaluacion.dígitos[3]
            fa_esperado = modelo_evaluacion.a + d4
            try:
                if abs(float(ans_fa) - float(fa_esperado)) > 0.05:
                    errores.append(f"- El valor de f({modelo_evaluacion.a}) evaluado en el tramo correcto es incorrecto.")
            except ValueError:
                errores.append(f"- Formato numérico inválido en el casillero de f(a).")

        # Valida clasificación del tipo de discontinuidad
        indice_esperado = 0
        if modelo_evaluacion.caso == 1: indice_esperado = 2
        elif modelo_evaluacion.caso == 2: indice_esperado = 3
        elif modelo_evaluacion.caso == 3: indice_esperado = 4

        if ans_clasificacion_idx != indice_esperado:
            errores.append(f"- La clasificación de la discontinuidad seleccionada no corresponde al caso analítico.")

        # Valida el veredicto final en la interfaz
        if not errores:
            self.actualizar_barra_feedback("✓ ANÁLICES CORRECTO: ¡Excelente defensa matemática!", "#DCFCE7", "#166534", "#BBF7D0")
            
            # Ventana de validación exitosa 
            msg_exito = QMessageBox(self.vista)
            msg_exito.setWindowTitle("Evaluación Exitosa")
            msg_exito.setText("""
            <div style='font-family: -apple-system, sans-serif; padding: 5px; text-align: center;'>
                <h3 style='color: #16A34A; margin-top: 0;'>¡Felicidades!</h3>
                <p style='color: #374151; font-size: 13px;'>Todo tu análisis de límites laterales, existencia y clasificación es matemáticamente exacto.</p>
            </div>
            """)
            msg_exito.setStyleSheet("""
                QMessageBox { background-color: #FFFFFF; border-radius: 8px; }
                QPushButton { background-color: #16A34A; color: white; padding: 6px 16px; border-radius: 5px; font-weight: bold; border: none; }
                QPushButton:hover { background-color: #15803D; }
            """)
            msg_exito.exec()
        else:
            self.actualizar_barra_feedback("✗ ANÁLISIS INCORRECTO: Revisa tus respuestas.", "#FEE2E2", "#991B1B", "#FCA5A5")
            
            # Llama al nuevo componente estilizado para listar las discrepancias
            self.mostrar_advertencia_elegante(errores)

    def mostrar_advertencia_elegante(self, lista_errores):
        # Genera una ventana de alerta altamente estilizada y moderna para los errores
        msg_box = QMessageBox(self.vista)
        msg_box.setWindowTitle("Corrección de Límites")
        
        # Convertimos los errores a elementos de lista HTML limpios sin guiones feos
        items_html = "".join([f"<li style='margin-bottom: 7px; color: #4B5563;'>{err.replace('- ', '')}</li>" for err in lista_errores])
        
        # Estructura del layout interno en HTML semántico centrado y contenido ajustado
        contenido_html = f"""
        <div style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica; padding: 5px;'>
            <h2 style='color: #991B1B; margin-top: 0; margin-bottom: 8px; font-size: 15px; font-weight: 700;'>
                Discrepancias en tu entrega
            </h2>
            <p style='color: #374151; font-size: 13px; margin-bottom: 12px; line-height: 1.4;'>
                Se encontraron los siguientes puntos a corregir en tu análisis matemático:
            </p>
            <ul style='font-size: 12px; padding-left: 16px; margin-bottom: 14px; line-height: 1.5; color: #4B5563;'>
                {items_html}
            </ul>
            <p style='color: #6B7280; font-size: 11px; font-style: italic; border-top: 1px solid #E5E7EB; padding-top: 9px; margin-bottom: 0; line-height: 1.3;'>
                💡 Apóyate en el comportamiento visual del lienzo interactivo y en las aproximaciones numéricas de la tabla.
            </p>
        </div>
        """
        
        msg_box.setText(contenido_html)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        
        # Aplicamos la hoja de estilos QSS personalizada sobre el cuadro y el botón OK
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                
                /* CONTROL TOTAL DEL RECUADRO BLANCO EXTERNO */
                min-width: 350px;
                max-width: 360px;
            }
            QLabel {
                /* CONTROL DEL TEXTO INTERNO: Evita expandir horizontalmente y obliga saltos */
                min-width: 260px;
                max-width: 270px;
                word-wrap: true;
            }
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                font-family: -apple-system, sans-serif;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        
        msg_box.exec()

    def actualizar_barra_feedback(self, texto, bg_color, text_color, border_color):
        # Cambia visualmente la barra inferior de la tarjeta de input
        self.vista.lbl_validacion.setText(texto)
        self.vista.lbl_validacion.setStyleSheet(f"""
            background-color: {bg_color}; color: {text_color}; 
            font-weight: bold; font-size: 11px; padding: 8px; 
            border-radius: 6px; border: 1px solid {border_color};
        """)