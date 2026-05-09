
def validar_rut(rut_texto: str) -> tuple[bool, str]:
    """
    Valida un RUT chileno usando el algoritmo oficial Módulo 11.
    Retorna (exito: bool, log_pasos: str) para que la vista lo muestre.
    """
    log = []

    rut = rut_texto.strip().replace(".", "").replace(" ", "").upper()
    log.append(f"RUT normalizado: {rut}")

    if "-" not in rut:
        return False, _log("ERROR: El RUT no contiene guión separador.", log)

    cuerpo, dv = rut.split("-", 1)

    if not cuerpo.isdigit():
        return False, _log("ERROR: El cuerpo debe contener solo dígitos.", log)

    if len(cuerpo) != 8:
        return False, _log(f"ERROR: El cuerpo debe tener 8 dígitos (tiene {len(cuerpo)}).", log)

    validos_dv = [str(i) for i in range(10)] + ["K"]
    if dv not in validos_dv:
        return False, _log("ERROR: El dígito verificador debe ser 0-9 o K.", log)

    digitos = [int(c) for c in cuerpo]
    log.append(f"Dígitos: d1={digitos[0]} d2={digitos[1]} d3={digitos[2]} d4={digitos[3]} "
               f"d5={digitos[4]} d6={digitos[5]} d7={digitos[6]} d8={digitos[7]}")

    factores = [2, 3, 4, 5, 6, 7, 2, 3]
    log.append("")
    log.append("Multiplicación de derecha a izquierda por factores [2,3,4,5,6,7,2,3]:")

    suma = 0
    for i, (d, f) in enumerate(zip(reversed(digitos), factores)):
        prod = d * f
        suma += prod
        log.append(f"  d{8-i} = {d}  ×  {f}  =  {prod}")

    log.append(f"Suma total = {suma}")
    resto = suma % 11
    log.append(f"Resto: {suma} mod 11 = {resto}")

    calc = 11 - resto
    log.append(f"11 - {resto} = {calc}")

    if calc == 11:
        dv_esp = "0"
        log.append("Resultado 11  →  dígito verificador esperado = 0")
    elif calc == 10:
        dv_esp = "K"
        log.append("Resultado 10  →  dígito verificador esperado = K")
    else:
        dv_esp = str(calc)
        log.append(f"Dígito verificador esperado = {dv_esp}")

    log.append("")
    if dv == dv_esp:
        log.append(f"✓ DV ingresado ({dv}) coincide con el esperado ({dv_esp}).")
        log.append("✓ RUT VÁLIDO")
        return True, "\n".join(log)
    else:
        log.append(f"✗ DV ingresado ({dv}) ≠ esperado ({dv_esp}).")
        log.append("✗ RUT INVÁLIDO")
        return False, "\n".join(log)


def extraer_digitos(rut_texto: str) -> list[int]:
    rut = rut_texto.strip().replace(".", "").replace(" ", "").upper()
    cuerpo = rut.split("-")[0]
    return [int(c) for c in cuerpo]


def extraer_dv(rut_texto: str) -> str:
    rut = rut_texto.strip().replace(".", "").replace(" ", "").upper()
    return rut.split("-")[1]


def calcular_variable_auxiliar(dv: str) -> tuple[int, str]:
    log = ["── Variable auxiliar v ──"]
    log.append(f"Dígito verificador DV = '{dv}'")

    if dv == "K":
        v = 10
        log.append("Regla: DV = K  →  v = 10")
    elif dv == "0":
        v = 11
        log.append("Regla: DV = 0  →  v = 11")
    else:
        v = int(dv)
        log.append(f"Regla: DV es dígito 1-9  →  v = {v}")

    log.append(f"v = {v}")
    return v, "\n".join(log)


def construir_ecuacion(digitos: list[int], v: int) -> dict:
    d = digitos
    log = ["── Construcción de la Ecuación General ──"]

    A_num, A_den = d[0] + d[1], v
    B_num, B_den = d[2] + d[3], v
    C = -(d[4] + d[5])
    D_val = -(d[6] + d[7])
    E = d[0] + d[2] + d[4] + d[6]

    log.append(f"A = (d1+d2)/v = ({d[0]}+{d[1]})/{v} = {A_num}/{v}")
    log.append(f"B = (d3+d4)/v = ({d[2]}+{d[3]})/{v} = {B_num}/{v}")
    log.append(f"C = -(d5+d6)  = -({d[4]}+{d[5]}) = {C}")
    log.append(f"D = -(d7+d8)  = -({d[6]}+{d[7]}) = {D_val}")
    log.append(f"E = d1+d3+d5+d7 = {d[0]}+{d[2]}+{d[4]}+{d[6]} = {E}")

    def _mcd(a, b):
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a or 1

    def _simp(n, dd):
        if n == 0:
            return 0, 1
        g = _mcd(abs(n), abs(dd))
        return n // g, dd // g

    A_n, A_d = _simp(A_num, A_den)
    B_n, B_d = _simp(B_num, B_den)
    A_val = A_n / A_d
    B_val = B_n / B_d

    log.append("")
    log.append("── Ajustes de cónicas ──")

    if d[7] % 2 != 0:
        B_val = -B_val
        B_n = -B_n
        log.append(f"Ajuste 1: d8={d[7]} es IMPAR  →  B = -B = {_fstr(B_n, B_d)}")
    else:
        log.append(f"Ajuste 1: d8={d[7]} es par    →  B sin cambio")

    if d[0] == d[1]:
        B_val = A_val
        B_n, B_d = A_n, A_d
        log.append(f"Ajuste 2: d1=d2={d[0]}  →  B = A = {_fstr(A_n, A_d)}")
    else:
        log.append(f"Ajuste 2: d1({d[0]}) ≠ d2({d[1]})  →  sin cambio")

    s56 = d[4] + d[5]
    if s56 % 3 == 0:
        log.append(f"Ajuste 3: d5+d6={s56}, múltiplo de 3  →  PARÁBOLA")
        if d[6] % 2 == 0:
            B_val, B_n, B_d = 0, 0, 1
            log.append(f"  d7={d[6]} par  →  B=0 (eje vertical)")
        else:
            A_val, A_n, A_d = 0, 0, 1
            log.append(f"  d7={d[6]} impar  →  A=0 (eje horizontal)")
    else:
        log.append(f"Ajuste 3: d5+d6={s56}, no múltiplo de 3  →  sin cambio")

    log.append("")
    log.append("── Ecuación resultante ──")
    log.append(f"A = {_fstr(A_n, A_d)}")
    log.append(f"B = {_fstr(B_n, B_d)}")
    log.append(f"C = {C}")
    log.append(f"D = {D_val}")
    log.append(f"E = {E}")
    ec = (f"({_fstr(A_n,A_d)})x²  +  ({_fstr(B_n,B_d)})y²  "
          f"+  ({C})x  +  ({D_val})y  +  ({E})  =  0")
    log.append(ec)

    return {
        "A": A_val, "B": B_val, "C": C, "D": D_val, "E": E,
        "A_frac": (A_n, A_d), "B_frac": (B_n, B_d),
        "ecuacion_str": ec,
        "log": "\n".join(log)
    }


def clasificar_conica(A: float, B: float) -> tuple[str, str]:
    eps = 1e-9
    az = abs(A) < eps
    bz = abs(B) < eps

    if az and bz:
        return "Degenerada", "A=0 y B=0. No representa una cónica estándar."
    if az or bz:
        return "Parábola", (
            f"Exactamente uno de los coeficientes es cero "
            f"(A={_fmt(A)}, B={_fmt(B)})  →  Parábola."
        )
    if abs(A - B) < eps:
        return "Circunferencia", (
            f"A = B = {_fmt(A)} y ambos ≠ 0  →  Circunferencia."
        )
    if (A > 0) == (B > 0):
        return "Elipse", (
            f"A={_fmt(A)} y B={_fmt(B)} tienen el mismo signo, A ≠ B  →  Elipse."
        )
    return "Hipérbola", (
        f"A={_fmt(A)} y B={_fmt(B)} tienen signos opuestos  →  Hipérbola."
    )


# ── helpers privados ─────────────────────────────────────────
def _fstr(n, d):
    """Muestra fracción simplificada. Si el denominador divide exacto, muestra entero."""
    if d == 1 or n == 0:
        return str(int(n))
    # FIX: si n es divisible exacto por d, mostrar entero en vez de fracción
    if n % d == 0:
        return str(int(n // d))
    return f"{int(n)}/{int(d)}"

def _fmt(v):
    return str(int(v)) if v == int(v) else f"{v:.4f}"

def _log(msg, lines):
    lines.append(msg)
    return "\n".join(lines)