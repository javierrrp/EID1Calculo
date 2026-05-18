class ModeloLimites:
    def __init__(self):
        self.dígitos = []
        self.a = 0
        self.caso = 0  # 1: Removible, 2: Salto, 3: Infinita
        self.nombre_caso = ""

    def configurar_desde_rut(self, cuerpo_rut):
        """
        Extrae los dígitos del RUT y configura el caso correspondiente
        según las reglas de divisibilidad de la EID N°1.
        """
        # Convertir el cuerpo del RUT a una lista de enteros
        self.dígitos = [int(d) for d in str(cuerpo_rut) if d.isdigit()]
        
        # Si el RUT tiene menos de 8 dígitos (por ejemplo, 7 millones), 
        # rellenamos con ceros a la izquierda para mantener consistencia de índices
        while len(self.dígitos) < 8:
            self.dígitos.insert(0, 0)
            
        # El punto de análisis principal se define como d3 (índice 2 en Python)
        self.a = self.dígitos[2]
        
        # d8 es el último dígito del cuerpo (índice 7 en Python)
        d8 = self.dígitos[7]
        
        # Criterio de selección del caso según residuo de d8 / 3
        if d8 % 3 == 0:
            self.caso = 1
            self.nombre_caso = "Discontinuidad Removible"
        elif d8 % 3 == 1:
            self.caso = 2
            self.nombre_caso = "Discontinuidad de Salto"
        else:
            self.caso = 3
            self.nombre_caso = "Discontinuidad Infinita"

    def evaluar_funcion(self, x):
        """
        Evalúa la función por tramos construida algorítmicamente a partir del RUT.
        Implementa lógica de excepciones para evitar divisiones por cero en evaluación directa.
        """
        d1 = self.dígitos[0]
        d2 = self.dígitos[1]
        d4 = self.dígitos[3]
        d5 = self.dígitos[4]
        
        # CASO 1: Discontinuidad Removible
        if self.caso == 1:
            # f1(x) = ((x - a)*(x + d1)) / (x - a) si x < a
            # Para x >= a usaremos la versión simplificada o continua para simular el tramo continuo
            if abs(x - self.a) < 1e-9:
                # Matemáticamente no está definida en el punto exacto por división por cero
                return None 
            else:
                return ((x - self.a) * (x + d1)) / (x - self.a)

        # CASO 2: Discontinuidad de Salto
        elif self.caso == 2:
            if x < self.a:
                return x + d2
            else:
                return x + d4

        # CASO 3: Discontinuidad Infinita
        elif self.caso == 3:
            # f(x) = (d5 + 1) / (x - a)
            if abs(x - self.a) < 1e-9:
                return None # Asíntota vertical, división por cero
            else:
                return (d5 + 1) / (x - self.a)
        
        return 0.0

    def generar_tabla_valores(self):
        """
        Genera la evidencia computacional requerida por la Fase 5.
        Evalúa entornos decrecientes por izquierda y crecientes por derecha en torno a 'a'.
        """
        # Desplazamientos específicos indicados en el documento de la EID
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
        """
        Calcula de forma analítica exacta los límites analizados por el algoritmo
        para contrastarlos o usarlos en las validaciones internas de control.
        """
        d1 = self.dígitos[0]
        d2 = self.dígitos[1]
        d4 = self.dígitos[3]
        d5 = self.dígitos[4]
        
        if self.caso == 1:
            lim_izq = self.a + d1
            lim_der = self.a + d1
            existencia = True
        elif self.caso == 2:
            lim_izq = self.a + d2
            lim_der = self.a + d4
            existencia = (lim_izq == lim_der)
        else: # Caso 3
            # Determina la tendencia al infinito según el signo del numerador (d5 + 1 siempre > 0)
            lim_izq = float('-inf')
            lim_der = float('inf')
            existencia = False
            
        return lim_izq, lim_der, existencia