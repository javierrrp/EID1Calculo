
class ErrorConicas(Exception):
    #Excepcion propia del modulo para errores controlados
    pass



class ModeloConicas:
    def __init__(self, a, b, c, d, e):
        self._validar_coeficientes(a, b, c, d, e)
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)
        self.e = float(e)
        self.pasos_desarrollo = []

    # ─────────────────────────────────────────────────────────────
    # VALIDACIONES INTERNAS
    # ─────────────────────────────────────────────────────────────
    
    @staticmethod
    def _validar_coeficientes(a, b, c, d, e):

        nombres = {"A": a, "B": b, "C": c, "D": d, "E": e}
        for nombre, valor in nombres.items():
            try:
                float(valor)
            except (TypeError, ValueError):
                raise ErrorConicas(
                    f"El coeficiente {nombre} debe ser un número válido. "
                    f"Valor proporcionado: {repr(valor)}"
                )
        
        if abs(float(a)) < 1e-9 and abs(float(b)) < 1e-9:
            raise ErrorConicas(
                "La ecuacion es degenerada: A y B no pueden ser ambos cero. "
                "No representa ninguna conica estandar"
            )

    def clasificar_conica(self):
        try:
            if abs(self.a - self.b) < 1e-9 and abs(self.a) > 1e-9:
                return "Circunferencia"
            if self.a * self.b > 0:
                return "Elipse"
            if self.a * self.b < 0:
                return "Hipérbola"
            if abs(self.a) < 1e-9 and abs(self.b) > 1e-9:
                return "Parábola con eje horizontal"
            if abs(self.b) < 1e-9 and abs(self.a) > 1e-9:
                return "Parábola con eje vertical"
            return "Cónica no clasificada"
        except Exception as exc:
            raise ErrorConicas(f"Error inesperado al clasificar la cónica: {exc}") from exc
    
    def completar_cuadrados(self):
        try:
            self.pasos_desarrollo = []
            self.pasos_desarrollo.append(
                f"Ecuación original: {self.a:.4g}x² + {self.b:.4g}y² "
                f"+ {self.c:.4g}x + {self.d:.4g}y + {self.e:.4g} = 0"
            )
 
            lado_derecho = -self.e
            h = 0.0
            k = 0.0
 
            #Completar cuadrado en X
            if abs(self.a) > 1e-9:
                mitad_c_sobre_a = self.c / (2.0 * self.a)   # c/(2A)
                termino_suma_x = mitad_c_sobre_a ** 2        # (c/2A) 
                aporte_x = self.a * termino_suma_x           # A·(c/2A)²
 
                lado_derecho += aporte_x
                h = -mitad_c_sobre_a                         # h = -c/(2A)
 
                self.pasos_desarrollo.append(
                    f"Completar cuadrado en X: h = {h:.6g}, "
                    f"suma al lado derecho = {aporte_x:.6g}"
                )
            else:
                self.pasos_desarrollo.append("A = 0 → no se completa cuadrado en X (parábola horizontal).")
 
            #Completar cuadrado en Y
            if abs(self.b) > 1e-9:
                mitad_d_sobre_b = self.d / (2.0 * self.b)
                termino_suma_y = mitad_d_sobre_b ** 2
                aporte_y = self.b * termino_suma_y
 
                lado_derecho += aporte_y
                k = -mitad_d_sobre_b
 
                self.pasos_desarrollo.append(
                    f"Completar cuadrado en Y: k = {k:.6g}, "
                    f"suma al lado derecho = {aporte_y:.6g}"
                )
            else:
                self.pasos_desarrollo.append("B = 0 → no se completa cuadrado en Y (parábola vertical).")
 
            self.pasos_desarrollo.append(
                f"Forma canónica: {self.a:.4g}(x - {h:.4g})² "
                f"+ {self.b:.4g}(y - {k:.4g})² = {lado_derecho:.6g}"
            )
 
            return h, k, lado_derecho
 
        except ErrorConicas:
            raise
        except ZeroDivisionError:
            # No debería ocurrir por las guardas anteriores, pero por si acaso.
            raise ErrorConicas(
                "División por cero al completar el cuadrado. "
                "Verifica que A y B no sean simultáneamente cero."
            )
        except Exception as exc:
            raise ErrorConicas(f"Error inesperado en completar_cuadrados: {exc}") from exc
        

    def obtener_elementos_geometricos(self) -> dict:
    
        try:
            tipo = self.clasificar_conica()
            h, k, lado_der = self.completar_cuadrados()
 
            # Corregir el -0.0 que puede aparecer en h o k
            h_str = f"{h:.4g}" if h != 0 else "0"
            k_str = f"{k:.4g}" if k != 0 else "0"

            base = {
                "tipo": tipo,
                "centro": f"({h_str}, {k_str})",
                "radio": "no aplica",
                "focos": "no aplica",
                "vertices": "no aplica",
            }
 
            if tipo == "Circunferencia":
                if abs(self.a) < 1e-9:
                    raise ErrorConicas("Circunferencia con A = 0: imposible calcular radio.")
                r2 = lado_der / self.a
                if r2 < 0:
                    base["radio"] = "Imaginario "
                elif abs(r2) < 1e-9:
                    base["radio"] = "0 (punto degenerado)"
                else:
                    radio = r2 ** 0.5
                    base["radio"] = f"{radio:.4g}"
                return base
 
            if tipo == "Elipse":
                if abs(self.a) < 1e-9 or abs(self.b) < 1e-9:
                    raise ErrorConicas("Elipse con coeficiente cero: imposible calcular semiejes.")
                a2 = lado_der / self.a
                b2 = lado_der / self.b
                if a2 <= 0 or b2 <= 0:
                    base["vertices"] = "Elipse degenerada (semiejes no reales)"
                    return base
                semi_a = a2 ** 0.5
                semi_b = b2 ** 0.5
                mayor = max(semi_a, semi_b)
                menor = min(semi_a, semi_b)
                c_foco = (mayor ** 2 - menor ** 2) ** 0.5
                if a2 >= b2:
                    focos = f"({h + c_foco:.4g}, {k:.4g}) y ({h - c_foco:.4g}, {k:.4g})"
                    vertices = f"({h + semi_a:.4g}, {k:.4g}) y ({h - semi_a:.4g}, {k:.4g})"
                else:
                    focos = f"({h:.4g}, {k + c_foco:.4g}) y ({h:.4g}, {k - c_foco:.4g})"
                    vertices = f"({h:.4g}, {k + semi_b:.4g}) y ({h:.4g}, {k - semi_b:.4g})"
                base["focos"] = focos
                base["vertices"] = vertices
                return base
 
            if tipo == "Hipérbola":
                if abs(self.a) < 1e-9 or abs(self.b) < 1e-9:
                    raise ErrorConicas("Hipérbola con coeficiente cero: imposible calcular semiejes.")
                a2 = lado_der / self.a
                b2 = lado_der / self.b
                if a2 == 0 or b2 == 0:
                    base["vertices"] = "Hipérbola degenerada"
                    return base
                # Eje transverso en la dirección del coeficiente positivo
                if self.a > 0:
                    if a2 <= 0:
                        base["vertices"] = "Hipérbola con a² negativo (verificar signos)"
                        return base
                    semi_a = a2 ** 0.5
                    semi_b = abs(b2) ** 0.5
                    c_foco = (a2 + abs(b2)) ** 0.5
                    focos = f"({h + c_foco:.4g}, {k:.4g}) y ({h - c_foco:.4g}, {k:.4g})"
                    vertices = f"({h + semi_a:.4g}, {k:.4g}) y ({h - semi_a:.4g}, {k:.4g})"
                else:
                    if b2 >= 0:
                        base["vertices"] = "Hipérbola con b² no negativo (verificar signos)"
                        return base
                    semi_b = abs(b2) ** 0.5
                    semi_a = abs(a2) ** 0.5
                    c_foco = (abs(a2) + abs(b2)) ** 0.5
                    focos = f"({h:.4g}, {k + c_foco:.4g}) y ({h:.4g}, {k - c_foco:.4g})"
                    vertices = f"({h:.4g}, {k + semi_b:.4g}) y ({h:.4g}, {k - semi_b:.4g})"
                base["focos"] = focos
                base["vertices"] = vertices
                return base
 
            # Parábola u otro tipo
            base["vertices"] = f"({h:.4g}, {k:.4g})"
            return base
 
        except ErrorConicas:
            raise
        except Exception as exc:
            # Retornamos dict seguro para que la vista nunca reciba None
            msg = f"Error al obtener elementos: {exc}"
            return {
                "tipo": "Error",
                "centro": msg,
                "radio": "—",
                "focos": "—",
                "vertices": "—",
            }
        
    def obtener_pasos_texto(self):
        if not self.pasos_desarrollo:
            return (
                "No hay pasos disponibles.\n"
                "Llama primero a completar_cuadrados() para generar el desarrollo."
            )

        return "\n".join(self.pasos_desarrollo)
    

    def expandir_general(
            self, h: float, k: float, lado_derecho: float
    
    ) -> tuple[float, float, float, str]:
        
        try: 
            for nombre, val in (("h", h), ("k", k), ("lado_derecho", lado_derecho)):
                try:
                    float(val)
                except (TypeError, ValueError):
                    raise ErrorConicas(
                        f"El parametro '{nombre}' debe ser un numerico. "
                        f"Valor recibido: {repr(val)}"
                    )
            h = float(h)
            k = float(k)
            lado_derecho = float(lado_derecho)

            pasos = []
            pasos.append("── Procedimiento Inverso: Canónica → General ──\n")
            pasos.append(
                f"Forma canónica: {self.a:.4g}(x - {h:.4g})² "
                f"+ {self.b:.4g}(y - {k:.4g})² = {lado_derecho:.6g}\n"
            )



            pasos.append("\n1. Desarrollamos los binomios al cuadrado:")
            pasos.append(f"   (x - {h:.4g})² = x² - {2*h:.4g}x + {h**2:.4g}")
            pasos.append(f"   (y - {k:.4g})² = y² - {2*k:.4g}y + {k**2:.4g}\n")
        
            c_calculado = -2 * self.a * h
            d_calculado = -2 * self.b * k

            termino_ind_x = self.a * h ** 2
            termino_ind_y = self.b * k ** 2

            pasos.append("\n2. Multiplicamos por los coeficientes externos A y B:")
            pasos.append(
                f"   {self.a:.4g}·(x² - {2*h:.4g}x + {h**2:.4g}) "
                f"= {self.a:.4g}x² + {c_calculado:.4g}x + {termino_ind_x:.4g}"
            )
            pasos.append(
                f"   {self.b:.4g}·(y² - {2*k:.4g}y + {k**2:.4g}) "
                f"= {self.b:.4g}y² + {d_calculado:.4g}y + {termino_ind_y:.4g}\n"
            )
        

            e_calculado = termino_ind_x + termino_ind_y - lado_derecho
            pasos.append("\n3. Agrupamos terminos independientes trasladando el lado derecho:")
            pasos.append(
                f"   E = {termino_ind_x:.4g} + {termino_ind_y:.4g} "
                f"- {lado_derecho:.4g} = {e_calculado:.4g}\n"
            )
 
            ecuacion_general = (
                f"{self.a:.4g}x² + {self.b:.4g}y² + {c_calculado:.4g}x "
                f"+ {d_calculado:.4g}y + {e_calculado:.4g} = 0"
            )
            pasos.append("4. Ecuación general reconstruida:")
            pasos.append(f"   {ecuacion_general}")
 
            return c_calculado, d_calculado, e_calculado, "\n".join(pasos)
        
        except ErrorConicas:
            raise
        except OverflowError:
            raise ErrorConicas(
                "Desbordamiento numérico al expandir la ecuación general. "
                "Los coeficientes son demasiado grandes."
            )
        except Exception as exc:
            raise ErrorConicas(f"Error inesperado en expandir_general: {exc}") from exc
    