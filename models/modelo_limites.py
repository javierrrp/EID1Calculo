class ModeloLimites:
    def __init__(self):
        self.dígitos = []
        self.a = 0
        self.caso = 0  # 1: Removible, 2: Salto, 3: Infinita
        self.nombre_caso = ""
        self.ejercicio_cargado = False

    def configurar_desde_rut(self, cuerpo_rut):
        try:
            # Fuerza conversión y limpia caracteres no numéricos
            filtrado = [int(d) for d in str(cuerpo_rut) if d.isdigit()]
            
            if not filtrado:
                raise ValueError("El formato del RUT no provee componentes numéricos procesables.")
                
            self.dígitos = filtrado
            
            while len(self.dígitos) < 8:
                self.dígitos.insert(0, 0)
                
            self.a = self.dígitos[2]
            d8 = self.dígitos[7]
            
            if d8 % 3 == 0:
                self.caso = 1
                self.nombre_caso = "Discontinuidad Removible"
            elif d8 % 3 == 1:
                self.caso = 2
                self.nombre_caso = "Discontinuidad de Salto"
            else:
                self.caso = 3
                self.nombre_caso = "Discontinuidad Infinita"
                
            self.ejercicio_cargado = True
            
        except Exception as e:
            self.ejercicio_cargado = False
            raise RuntimeError(f"Error crítico en la segmentación matemática del RUT: {str(e)}")

    def evaluar_funcion(self, x):
        if not self.ejercicio_cargado:
            return None
            
        try:
            d1 = self.dígitos[0]
            d2 = self.dígitos[1]
            d4 = self.dígitos[3]
            d5 = self.dígitos[4]
            
            if abs(x - self.a) < 1e-9:
                if self.caso in [1, 3]:
                    return None 
            
            if self.caso == 1:
                return ((x - self.a) * (x + d1)) / (x - self.a)
            elif self.caso == 2:
                return (x + d2) if x < self.a else (x + d4)
            elif self.caso == 3:
                return (d5 + 1) / (x - self.a)
                
        except ZeroDivisionError:
            return None
        except Exception:
            return None
        return 0.0

    def generar_tabla_valores(self):
        # Genera entornos asumiendo el estado controlado de evaluar_funcion.
        if not self.ejercicio_cargado:
            return [], []
            
        desplazamientos_izq = [-1.0, -0.1, -0.01, -0.001]
        desplazamientos_der = [0.001, 0.01, 0.1, 1.0]
        
        tabla_izq = []
        for h in desplazamientos_izq:
            x_val = self.a + h
            y_val = self.evaluar_funcion(x_val)
            tabla_izq.append((x_val, y_val))
            
        tabla_der = []
        for h in desplazamientos_der:
            x_val = self.a + h
            y_val = self.evaluar_funcion(x_val)
            tabla_der.append((x_val, y_val))
            
        return tabla_izq, tabla_der

    def obtener_limites_teoricos(self):
        # Calcula de forma analítica exacta los límites.
        if not self.ejercicio_cargado:
            return None, None, False
            
        d1 = self.dígitos[0]
        d2 = self.dígitos[1]
        d4 = self.dígitos[3]
        
        if self.caso == 1:
            lim_izq = self.a + d1
            lim_der = self.a + d1
            existencia = True
        elif self.caso == 2:
            lim_izq = self.a + d2
            lim_der = self.a + d4
            existencia = (lim_izq == lim_der)
        else: 
            lim_izq = float('-inf')
            lim_der = float('inf')
            existencia = False
            
        return lim_izq, lim_der, existencia

    def obtener_solucionario(self):
        # Estructura las respuestas esperadas convirtiéndolas a texto estándar para validación.
        if not self.ejercicio_cargado:
            return {}
            
        lim_izq, lim_der, existencia = self.obtener_limites_teoricos()
        f_en_a = self.evaluar_funcion(self.a)
        
        return {
            "lim_izq": "-inf" if lim_izq == float('-inf') else str(round(float(lim_izq), 3)),
            "lim_der": "inf" if lim_der == float('inf') else str(round(float(lim_der), 3)),
            "existe": "Sí" if existencia else "No",
            "f_a": "no definido" if f_en_a is None else str(round(float(f_en_a), 3)),
            "continua": "No",
            "tipo_discont": self.nombre_caso
        }

    def verificar_respuestas(self, resp_alumno):
        # Compara las respuestas con tolerancia numérica en punto flotante.
        if not self.ejercicio_cargado:
            raise ValueError("Operación denegada: No existe un ejercicio activo.")
            
        solucion = self.obtener_solucionario()
        retroalimentacion = {}
        
        for llave in solucion:
            alumno_val = str(resp_alumno.get(llave, "")).strip().lower().replace(",", ".")
            correcto_val = str(solucion[llave]).strip().lower()
            
            try:
                # Validación con rango de tolerancia flotante nativo
                retroalimentacion[f"{llave}_ok"] = abs(float(alumno_val) - float(correcto_val)) < 1e-2
            except ValueError:
                # Comparación directa de cadenas para términos analíticos ('inf', 'no definido', etc.)
                retroalimentacion[f"{llave}_ok"] = (alumno_val == correcto_val)
                
        return retroalimentacion