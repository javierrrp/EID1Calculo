class ModeloConicas:
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e    
        self.pasos_desarrollo = []

    def clasificar_conica(self):
        if self.a == self.b and self.a != 0:
            return "Circunferencia"
        
        # Si A y B tienen el mismo signo pero son distintos -> Elipse
        elif self.a * self.b > 0 and self.a != self.b:
            return "Elipse"
        # Si A y B tienen signos opuestos -> Hipérbola
        elif self.a * self.b < 0:
            return "Hipérbola"
        # Si A o B es 0 -> Parábola
        elif self.a == 0 and self.b != 0:
            return "Parábola con eje horizontal"
        elif self.b == 0 and self.a != 0:
            return "Parábola con eje vertical"
        else:
            return "Otra conica"
    
    def completar_cuadrados(self):
        self.pasos_desarrollo = []
        self.pasos_desarrollo.append(f"Ecuacion original: {self.a:.2f}x^2 + {self.b}y^2 + {self.c:.2f}x + {self.d:.2f}y + {self.e:.2f} = 0") 

        lado_derecho = -self.e
        h = 0
        if self.a != 0:
            termino_suma_x = (self.c / (2 * self.a)) ** 2

            lado_derecho += self.a * termino_suma_x

            h = -(self.c / (2 * self.a))

            self.pasos_desarrollo.append(f"2. Completamos cuadrado de X: sumamos {self.a * termino_suma_x} al lado derecho.")
        k = 0
        if self.b != 0:
            termino_suma_y = (self.d / (2 * self.b)) ** 2
            lado_derecho += self.b * termino_suma_y
            k = -(self.d / (2 * self.b))
            self.pasos_desarrollo.append(f"3. Completamos cuadrado de Y: sumamos {self.b * termino_suma_y} al lado derecho.")
        self.pasos_desarrollo.append(f"Ecuación canónica: {self.a:.2f}(x - {h:.2f})² + {self.b}(y - {k})² = {lado_derecho:.2f}")

        return h, k, lado_derecho
    def obtener_elementos_geometricos(self):

        tipo = self.clasificar_conica()
        h, k, lado_der = self.completar_cuadrados()

        if tipo == "Circunferencia":
            radio = lado_der ** 0.5 if lado_der > 0 else 0

            return {
                "tipo": tipo,
                "centro": f"({h:.2f}, {k:.2f})",
                "radio": f"{radio:.2f}",
                "focos": "no aplica",
                "vertices": "no aplica"
            }
        else:
            return {
                "tipo": tipo,
                "centro": f"({h:.2f}, {k:.2f})",
                "radio": "por calcular...",
                "focos": "por calcular...",
                "vertices": "por calcular..."
            }
        
    def obtener_pasos_texto(self):

        return "\n".join(self.pasos_desarrollo)
    


