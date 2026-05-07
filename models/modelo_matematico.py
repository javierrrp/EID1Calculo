class ModeloMatematico:
    def __init__(self):
        self.rut_valido = False
        self.digitos = []  # d1, d2, d3, d4, d5, d6, d7, d8
        self.dv = ""       # Dígito verificador

    def validar_rut(self, rut_completo):
        """
        Implementación manual del Algoritmo Módulo 11 (Fase 2 del PDF).
        Retorna (bool, mensaje_paso_a_paso)
        """
        try:
            # 1. Limpieza de datos (quitar puntos y guión)
            rut_limpio = rut_completo.replace(".", "").replace("-", "").upper()
            cuerpo = rut_limpio[:-1]
            dv_ingresado = rut_limpio[-1]

            if not cuerpo.isdigit():
                return False, "Error: El cuerpo del RUT debe contener solo números."

            # 2. Algoritmo Módulo 11
            suma = 0
            multiplicador = 2
            pasos = []

            # Se recorre el cuerpo de derecha a izquierda
            for d in reversed(cuerpo):
                parcial = int(d) * multiplicador
                pasos.append(f"{d} x {multiplicador} = {parcial}")
                suma += parcial
                multiplicador += 1
                if multiplicador > 7:
                    multiplicador = 2

            resto = suma % 11
            resultado = 11 - resto
            
            # Determinar DV esperado
            if resultado == 11:
                dv_esperado = "0"
            elif resultado == 10:
                dv_esperado = "K"
            else:
                dv_esperado = str(resultado)

            # 3. Guardar dígitos si es válido para las siguientes fases
            if dv_ingresado == dv_esperado:
                self.rut_valido = True
                # Asegurar que tenemos exactamente 8 dígitos (rellenar con 0 si es necesario)
                cuerpo_pad = cuerpo.zfill(8)
                self.digitos = [int(d) for d in cuerpo_pad]
                self.dv = dv_ingresado
                
                log = "Suma total: " + str(suma) + "\n" + "\n".join(pasos)
                log += f"\n\nDV Calculado: {dv_esperado} == DV Ingresado: {dv_ingresado} ¡ÉXITO!"
                return True, log
            else:
                return False, f"DV Incorrecto. Calculado: {dv_esperado}"

        except Exception as e:
            return False, f"Error crítico: {str(e)}"

    def obtener_coeficientes_conica(self):
        """
        Calcula A, B, C, D, E y v según las reglas de la Fase 4
        """
        if not self.rut_valido: return None

        d = self.digitos
        # Ejemplo de reglas del PDF:
        v = d[0] + d[1] # Variable auxiliar v
        A = d[2] + 2
        B = d[3] + 3
        # Si d8 es impar, B es negativo (Hipérbola)
        if d[7] % 2 != 0:
            B = -B
            
        C = d[4] - 5
        D = d[5] * 2
        E = (d[6] + 1) * -10
        
        return {"A": A, "B": B, "C": C, "D": D, "E": E, "v": v}

    def obtener_caso_limite(self):
        """
        Determina el caso de la función por tramos (Fase 6)
        """
        d8 = self.digitos[7]
        residuo = d8 % 3
        
        if residuo == 0: return "Caso 1: Discontinuidad Removible"
        if residuo == 1: return "Caso 2: Discontinuidad de Salto"
        return "Caso 3: Discontinuidad Infinita"