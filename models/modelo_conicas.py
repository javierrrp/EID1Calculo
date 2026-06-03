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
            if lado_der > 0:
                radio = f"{(lado_der ** 0.5):.2f}"
            elif lado_der == 0:
                radio = "0 (Es un punto)"
            else:
                radio = "Imaginario (No existe locus real)"

            return {
                "tipo": tipo,
                "centro": f"({h:.2f}, {k:.2f})",
                "radio": radio,
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
    

    def expandir_general(self, h, k, lado_derecho):
        pasos = []
        pasos.append(f"Ecuacion canónica: {self.a:.2f}(x - h)² + {self.b}(y - k)² = lado_derecho")

        pasos.append("\n1. Desarrollamos los binomios al cuadrado:")
        pasos.append(f"   (x - {h:.2f})² = x² - 2*h*x + h²")
        pasos.append(f"   (y - {k:.2f})² = y² - 2*k*y + k²")
        
        c_calculado = -2 * self.a * h
        d_calculado = -2 * self.b * k

        termino_ind_x = self.a * h ** 2
        termino_ind_y = self.b * k ** 2

        pasos.append("\n2. Multiplicamos por los coeficientes externos A y B:")
        pasos.append(f"   {self.a:.2f}(x² - 2*{h:.2f}*x + {h:.2f}²) = {self.a:.2f}x² + {c_calculado:.2f}x + {termino_ind_x:.2f}")
        pasos.append(f"   {self.b}(y² - 2*{k:.2f}*y + {k:.2f}²) = {self.b}y² + {d_calculado:.2f}y + {termino_ind_y:.2f}")
        

        e_calculado = termino_ind_x + termino_ind_y - lado_derecho
        pasos.append("\n3. Agrupamos terminos independientes trasladando el lado derecho:")
        pasos.append(f"   E = {termino_ind_x:.2f} + {termino_ind_y:.2f} - {lado_derecho:.2f} = {e_calculado:.2f}")

        ecuacion_general = f"{self.a:.2f}x² + {self.b}y² + {c_calculado:.2f}x + {d_calculado:.2f}y + {e_calculado:.2f} = 0"
        pasos.append(f"\n4. Ecuación general: \n {ecuacion_general}")

        return c_calculado, d_calculado, e_calculado, "\n".join(pasos)