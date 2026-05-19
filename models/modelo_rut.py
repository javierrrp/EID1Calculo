def separar_rut(rut_texto: str) -> tuple[str, str]:
    rut = rut_texto.strip().replace(".", "").replace(" ", "").upper()
    if "-" not in rut:
        raise ValueError("El RUT no contiene guión separador.")

    cuerpo, dv = rut.split("-", 1)

    if not cuerpo or not dv:
        raise ValueError("El RUT debe tener cuerpo y dígito verificador.")

    return cuerpo, dv

def validar_rut(rut_texto: str) -> tuple[bool, str]:
    log = []
    rut_norm = rut_texto.strip().replace(".", "").replace(" ", "").upper()
    log.append(f"RUT normalizado: {rut_norm}")

    try:
        cuerpo, dv = separar_rut(rut_texto)
    except ValueError as e:
        return False, _log(f"ERROR: {str(e)}", log)

    if not cuerpo.isdigit():
        return False, _log("ERROR: El cuerpo debe contener solo dígitos.", log)

    if len(cuerpo) < 7 or len(cuerpo) > 8:
        return False, _log(f"ERROR: El cuerpo del RUT debe tener 7 u 8 dígitos (tiene {len(cuerpo)}).", log)

    validos_dv = [str(i) for i in range(10)] + ["K"]
    if dv not in validos_dv:
        return False, _log("ERROR: El dígito verificador debe ser 0-9 o K.", log)

    # Adaptación a 8 dígitos con ceros a la izquierda para el modelo matemático
    cuerpo_8 = cuerpo.zfill(8)
    log.append(f"Cuerpo original del RUT: {cuerpo} ({len(cuerpo)} dígitos)")
    log.append(f"Para el modelo matemático se completa a 8 dígitos: {cuerpo_8}")

    digitos = [int(c) for c in cuerpo_8]
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
    cuerpo, _ = separar_rut(rut_texto)
    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe contener solo dígitos.")
    if len(cuerpo) < 7 or len(cuerpo) > 8:
        raise ValueError(f"El cuerpo del RUT debe tener 7 u 8 dígitos (tiene {len(cuerpo)}).")
    cuerpo_8 = cuerpo.zfill(8)
    return [int(c) for c in cuerpo_8]


def extraer_dv(rut_texto: str) -> str:
    _, dv = separar_rut(rut_texto)
    validos_dv = [str(i) for i in range(10)] + ["K"]
    if dv not in validos_dv:
        raise ValueError("El dígito verificador debe ser 0-9 o K.")
    return dv


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
        return "Parábola", f"Exactamente uno es cero (A={_fmt(A)}, B={_fmt(B)})  →  Parábola."
    if abs(A - B) < eps:
        return "Circunferencia", f"A = B = {_fmt(A)} y ambos ≠ 0  →  Circunferencia."
    if (A > 0) == (B > 0):
        return "Elipse", f"A={_fmt(A)} y B={_fmt(B)} mismo signo, A ≠ B  →  Elipse."
    return "Hipérbola", f"A={_fmt(A)} y B={_fmt(B)} signos opuestos  →  Hipérbola."


def determinar_caso_limite(d8: int) -> dict:
    """
    Determina el tipo de discontinuidad según d8 (Fase 6 del PDF).
      d8 % 3 == 0  →  Caso 1: Discontinuidad Removible
      d8 % 3 == 1  →  Caso 2: Discontinuidad de Salto
      d8 % 3 == 2  →  Caso 3: Discontinuidad Infinita
    Retorna dict con caso (int 1/2/3), nombre, explicacion.
    """
    residuo = d8 % 3
    casos = {
        0: ("Removible",  1,
            f"d8 = {d8}  →  {d8} mod 3 = 0  →  Caso 1: Discontinuidad Removible.\n"
            f"Se construye una función racional con factor común que se anula en x = a."),
        1: ("De Salto",   2,
            f"d8 = {d8}  →  {d8} mod 3 = 1  →  Caso 2: Discontinuidad de Salto.\n"
            f"Se construyen dos tramos lineales con valores distintos al acercarse a x = a."),
        2: ("Infinita",   3,
            f"d8 = {d8}  →  {d8} mod 3 = 2  →  Caso 3: Discontinuidad Infinita.\n"
            f"Se construye una función cuyo denominador se anula en x = a."),
    }
    nombre, caso_num, explicacion = casos[residuo]
    return {
        "caso": caso_num,
        "nombre": nombre,
        "explicacion": explicacion,
        "d8": d8,
        "residuo": residuo,
    }


def expansion_canonica_a_general(A: float, B: float,
                                 h: float, k: float,
                                 r_o_p: float = 0,
                                 tipo: str = "") -> dict:
    """
    Dado el centro/vértice (h, k) y los coeficientes A, B,
    expande la forma canónica de vuelta a Ax²+By²+Cx+Dy+E=0
    mostrando cada paso algebraico de manera limpia.
    """
    log = ["── Expansión: Forma Canónica  →  Ecuación General ──"]
    log.append("")

    log.append(f"Partimos de la forma canónica con centro/vértice en (h, k) = ({_fmt(h)}, {_fmt(k)})")
    log.append("")
    log.append(f"Expandimos A·(x - h)²:")
    log.append(f"  A·(x - {_fmt(h)})²  =  A·(x² - 2·{_fmt(h)}·x + {_fmt(h)}²)")
    log.append(f"  =  A·x²  -  {_fmt(2*h)}A·x  +  {_fmt(h*h)}A")
    log.append("")
    log.append(f"Expandimos B·(y - k)²:")
    log.append(f"  B·(y - {_fmt(k)})²  =  B·(y² - 2·{_fmt(k)}·y + {_fmt(k)}²)")
    log.append(f"  =  B·y²  -  {_fmt(2*k)}B·y  +  {_fmt(k*k)}B")
    log.append("")

    # Coeficientes numéricos calculados directamente
    C_val = -2 * h * A
    D_val = -2 * k * B
    E_val = (h * h * A) + (k * k * B)

    log.append("Reuniendo términos en la forma Ax² + By² + Cx + Dy + E = 0:")
    log.append(f"  C = -2·h·A = -2·({_fmt(h)})·({_fmt(A)}) = {_fmt(C_val)}")
    log.append(f"  D = -2·k·B = -2·({_fmt(k)})·({_fmt(B)}) = {_fmt(D_val)}")
    log.append(f"  E = h²·A + k²·B = ({_fmt(h*h)})·({_fmt(A)}) + ({_fmt(k*k)})·({_fmt(B)}) = {_fmt(E_val)}")
    log.append("")

    log.append("Ecuación general reconstruida:")
    ec = (f"({_fmt(A)})x²  +  ({_fmt(B)})y²  +  ({_fmt(C_val)})x  "
          f"+  ({_fmt(D_val)})y  +  ({_fmt(E_val)})  =  0")
    log.append(ec)

    return {
        "C": C_val, "D": D_val, "E": E_val,
        "ecuacion_str": ec,
        "log": "\n".join(log)
    }


# ── helpers privados ─────────────────────────────────────────
def _fstr(n, d):
    if d == 1 or n == 0:
        return str(int(n))
    if n % d == 0:
        return str(int(n // d))
    return f"{int(n)}/{int(d)}"


def _fmt(v):
    try:
        if float(v).is_integer():
            return str(int(v))
    except (ValueError, TypeError):
        return str(v)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s


def _log(msg, lines):
    lines.append(msg)
    return "\n".join(lines)