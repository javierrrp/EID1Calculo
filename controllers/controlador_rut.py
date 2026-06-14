from view.vista_rut import VistaRut
from models.modelo_rut import (
    validar_rut,
    extraer_digitos,
    extraer_dv,
    calcular_variable_auxiliar,
    construir_ecuacion,
    clasificar_conica,
    construir_forma_canonica,
    expansion_canonica_a_general,
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
            self.vista.mostrar_canonica(
                "── Forma Canónica ──\nIngrese un RUT válido para continuar."
            )
            self.vista.mostrar_inverso(
                "── Procedimiento Inverso ──\nIngrese un RUT válido para continuar."
            )
            self.vista.mostrar_conica("—", "—", "—")
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
        tipo, explicacion, log_clasificacion = clasificar_conica(datos_ec["A"], datos_ec["B"])
        self.vista.mostrar_clasificacion(log_clasificacion)
        self.vista.mostrar_conica(tipo, datos_ec["ecuacion_str"], explicacion)

        # ── Paso 5: Forma canónica ───────────────────────────────
        datos_canon = construir_forma_canonica(
            datos_ec["A"], datos_ec["B"],
            datos_ec["C"], datos_ec["D"], datos_ec["E"]
        )
        self.vista.mostrar_canonica(datos_canon["log"])

        # ── Paso 6: Procedimiento inverso (canónica → general) ───
        datos_inv = expansion_canonica_a_general(
            datos_ec["A"], datos_ec["B"],
            datos_canon["h"], datos_canon["k"],
            datos_canon.get("lado_der", 0),
            tipo
        )
        self.vista.mostrar_inverso(datos_inv["log"])

        # ── Paso 7: Caso de límite (d8) ──────────────────────────
        caso_limite = determinar_caso_limite(digitos[7])

        # ── Guardar para los otros controladores ─────────────────
        self.datos_ecuacion = {
            **datos_ec,
            **datos_canon,
            "digitos": digitos,
            "dv": dv,
            "v": v,
            "tipo_conica": tipo,
            "caso_limite": caso_limite,
            "datos_canon": datos_canon,
        }

        self.vista._mostrar_tab("resultado")
