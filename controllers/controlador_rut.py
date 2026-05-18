
from view.vista_rut import VistaRut
from models.modelo_rut import (
    validar_rut,
    extraer_digitos,
    extraer_dv,
    calcular_variable_auxiliar,
    construir_ecuacion,
    clasificar_conica,
    determinar_caso_limite,
)


class ControladorRut:
    def __init__(self, modelo_compartido=None):
        self.modelo = modelo_compartido
        self.vista = VistaRut()
        self.datos_ecuacion: dict | None = None
        self.vista.boton_validar_clicado.connect(self.procesar_rut)

    def procesar_rut(self, rut_texto: str):
        # ── Paso 1: Validar ──────────────────────────────────────
        exito, log_validacion = validar_rut(rut_texto)
        self.vista.mostrar_resultado(exito, log_validacion)

        if not exito:
            self.datos_ecuacion = None
            self.vista.mostrar_variable_v(
                "── Variable auxiliar v ──\nIngrese un RUT válido para continuar."
            )
            self.vista.mostrar_ecuacion(
                "── Construcción de la Ecuación General ──\nIngrese un RUT válido para continuar."
            )
            self.vista.mostrar_conica("—", "—", "—")
            self.vista.mostrar_caso_limite(None)
            return

        # ── Paso 2: Variable v ───────────────────────────────────
        dv = extraer_dv(rut_texto)
        v, log_v = calcular_variable_auxiliar(dv)
        self.vista.mostrar_variable_v(log_v)

        # ── Paso 3: Ecuación ─────────────────────────────────────
        digitos = extraer_digitos(rut_texto)
        datos_ec = construir_ecuacion(digitos, v)
        self.vista.mostrar_ecuacion(datos_ec["log"])

        # ── Paso 4: Clasificar cónica ────────────────────────────
        tipo, explicacion = clasificar_conica(datos_ec["A"], datos_ec["B"])
        self.vista.mostrar_conica(tipo, datos_ec["ecuacion_str"], explicacion)

        # ── Paso 5: Caso de límite (d8) ──────────────────────────
        caso_limite = determinar_caso_limite(digitos[7])
        self.vista.mostrar_caso_limite(caso_limite)

        # ── Guardar para los otros controladores ─────────────────
        self.datos_ecuacion = {
            **datos_ec,
            "digitos": digitos,
            "dv": dv,
            "v": v,
            "tipo_conica": tipo,
            "caso_limite": caso_limite,
        }

        self.vista._mostrar_tab("resultado")
