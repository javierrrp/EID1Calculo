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
    log.append("")

    try:
        cuerpo, dv = separar_rut(rut_texto)
    except ValueError as e:
        return False, _log(f"ERROR: {str(e)}", log)

    if not cuerpo.isdigit():
        return False, _log("ERROR: El cuerpo debe contener solo dígitos.", log)

    if len(cuerpo) < 7 or len(cuerpo) > 8:
        return False, _log(f"ERROR: El cuerpo debe tener 7 u 8 dígitos (tiene {len(cuerpo)}).", log)

    validos_dv = [str(i) for i in range(10)] + ["K"]
    if dv not in validos_dv:
        return False, _log("ERROR: El dígito verificador debe ser 0-9 o K.", log)

    cuerpo_8 = cuerpo.zfill(8)
    log.append(f"Cuerpo original: {cuerpo} ({len(cuerpo)} dígitos)")
    log.append(f"Completado a 8 dígitos con ceros: {cuerpo_8}")
    log.append("")

    digitos = [int(c) for c in cuerpo_8]
    log.append(f"Dígitos extraídos:")
    for i, d in enumerate(digitos):
        log.append(f"  d{i+1} = {d}")
    log.append("")

    factores = [2, 3, 4, 5, 6, 7, 2, 3]
    log.append("── Algoritmo Módulo 11 ──")
    log.append("Se multiplica cada dígito de DERECHA a IZQUIERDA por los factores [2,3,4,5,6,7,2,3]:")
    log.append("")

    suma = 0
    for i, (d, f) in enumerate(zip(reversed(digitos), factores)):
        prod = d * f
        suma += prod
        log.append(f"  d{8-i} = {d}  ×  {f}  =  {prod}   (suma acumulada: {suma})")

    log.append("")
    log.append(f"Suma total = {suma}")
    resto = suma % 11
    log.append(f"Resto = {suma} mod 11 = {resto}")
    calc = 11 - resto
    log.append(f"11 - {resto} = {calc}")
    log.append("")

    if calc == 11:
        dv_esp = "0"
        log.append("Resultado 11  →  DV esperado = 0  (cuando 11 - resto = 11, el DV es 0)")
    elif calc == 10:
        dv_esp = "K"
        log.append("Resultado 10  →  DV esperado = K  (cuando 11 - resto = 10, el DV es K)")
    else:
        dv_esp = str(calc)
        log.append(f"DV esperado = {dv_esp}")

    log.append("")
    if dv == dv_esp:
        log.append(f"✓ DV ingresado ({dv}) = DV esperado ({dv_esp})")
        log.append("✓ RUT VÁLIDO")
        return True, "\n".join(log)
    else:
        log.append(f"✗ DV ingresado ({dv}) ≠ DV esperado ({dv_esp})")
        log.append("✗ RUT INVÁLIDO")
        return False, "\n".join(log)


def extraer_digitos(rut_texto: str) -> list[int]:
    cuerpo, _ = separar_rut(rut_texto)
    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT debe contener solo dígitos.")
    if len(cuerpo) < 7 or len(cuerpo) > 8:
        raise ValueError(f"El cuerpo debe tener 7 u 8 dígitos (tiene {len(cuerpo)}).")
    cuerpo_8 = cuerpo.zfill(8)
    return [int(c) for c in cuerpo_8]


def extraer_dv(rut_texto: str) -> str:
    _, dv = separar_rut(rut_texto)
    validos_dv = [str(i) for i in range(10)] + ["K"]
    if dv not in validos_dv:
        raise ValueError("El dígito verificador debe ser 0-9 o K.")
    return dv


def calcular_variable_auxiliar(dv: str) -> tuple[int, str]:
    log = ["── Variable Auxiliar v ──"]
    log.append("")
    log.append(f"El dígito verificador DV = '{dv}'")
    log.append("")
    log.append("Regla de definición de v:")
    log.append("  • Si DV = K  →  v = 10")
    log.append("  • Si DV = 0  →  v = 11")
    log.append("  • Si DV es dígito 1-9  →  v = DV")
    log.append("")

    if dv == "K":
        v = 10
        log.append(f"DV = 'K'  →  se aplica la primera regla  →  v = 10")
    elif dv == "0":
        v = 11
        log.append(f"DV = '0'  →  se aplica la segunda regla  →  v = 11")
    else:
        v = int(dv)
        log.append(f"DV = '{dv}' (dígito entre 1 y 9)  →  se aplica la tercera regla  →  v = {v}")

    log.append("")
    log.append(f"Valor final: v = {v}")
    log.append("")
    log.append("Este valor v se usará como DENOMINADOR en el cálculo de los coeficientes A y B.")
    return v, "\n".join(log)


def construir_ecuacion(digitos: list[int], v: int) -> dict:
    d = digitos
    log = ["── Construcción de la Ecuación General ──"]
    log.append("")
    log.append("La ecuación general de segundo grado tiene la forma:")
    log.append("  Ax² + By² + Cx + Dy + E = 0")
    log.append("")
    log.append("Los coeficientes se calculan con las siguientes fórmulas:")
    log.append(f"  A = (d1 + d2) / v    B = (d3 + d4) / v")
    log.append(f"  C = -(d5 + d6)       D = -(d7 + d8)      E = d1 + d3 + d5 + d7")
    log.append("")
    log.append("── Paso 1: Cálculo base de coeficientes ──")
    log.append("")

    A_num = d[0] + d[1]
    B_num = d[2] + d[3]
    C = -(d[4] + d[5])
    D_val = -(d[6] + d[7])
    E = d[0] + d[2] + d[4] + d[6]

    log.append(f"  A = (d1 + d2) / v = ({d[0]} + {d[1]}) / {v} = {A_num} / {v}")
    log.append(f"  B = (d3 + d4) / v = ({d[2]} + {d[3]}) / {v} = {B_num} / {v}")
    log.append(f"  C = -(d5 + d6) = -({d[4]} + {d[5]}) = {C}")
    log.append(f"  D = -(d7 + d8) = -({d[6]} + {d[7]}) = {D_val}")
    log.append(f"  E = d1 + d3 + d5 + d7 = {d[0]} + {d[2]} + {d[4]} + {d[6]} = {E}")

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

    A_n, A_d = _simp(A_num, v)
    B_n, B_d = _simp(B_num, v)
    A_val = A_n / A_d
    B_val = B_n / B_d

    if A_d != 1:
        log.append(f"  Simplificando A: {A_num}/{v} = {_fstr(A_n, A_d)}")
    if B_d != 1:
        log.append(f"  Simplificando B: {B_num}/{v} = {_fstr(B_n, B_d)}")

    log.append("")
    log.append("── Paso 2: Ajustes para obtener distintas cónicas ──")
    log.append("")

    ajuste_aplicado = False

    if d[7] % 2 != 0:
        B_val = -B_val
        B_n = -B_n
        log.append(f"  Ajuste 1: d8 = {d[7]} es IMPAR  →  B se reemplaza por -B")
        log.append(f"    Nuevo B = {_fstr(B_n, B_d)}  (esto permite la aparición de hipérbolas)")
        ajuste_aplicado = True
    else:
        log.append(f"  Ajuste 1: d8 = {d[7]} es par  →  B no cambia")

    if d[0] == d[1]:
        B_val = A_val
        B_n, B_d = A_n, A_d
        log.append(f"  Ajuste 2: d1 = d2 = {d[0]}  →  se impone B = A = {_fstr(A_n, A_d)}")
        log.append(f"    (esto permite la aparición de circunferencias)")
        ajuste_aplicado = True
    else:
        log.append(f"  Ajuste 2: d1 = {d[0]} ≠ d2 = {d[1]}  →  sin cambio en B")

    s56 = d[4] + d[5]
    if s56 % 3 == 0:
        log.append(f"  Ajuste 3: d5 + d6 = {d[4]} + {d[5]} = {s56}")
        log.append(f"    {s56} es múltiplo de 3  →  se generará una PARÁBOLA")
        if d[6] % 2 == 0:
            B_val, B_n, B_d = 0, 0, 1
            log.append(f"    d7 = {d[6]} es par  →  B = 0  (parábola de eje vertical)")
        else:
            A_val, A_n, A_d = 0, 0, 1
            log.append(f"    d7 = {d[6]} es impar  →  A = 0  (parábola de eje horizontal)")
        ajuste_aplicado = True
    else:
        log.append(f"  Ajuste 3: d5 + d6 = {d[4]} + {d[5]} = {s56}")
        log.append(f"    {s56} no es múltiplo de 3  →  sin cambio")

    if not ajuste_aplicado:
        log.append("  (No se aplicó ningún ajuste especial)")

    log.append("")
    log.append("── Paso 3: Coeficientes finales ──")
    log.append("")
    log.append(f"  A = {_fstr(A_n, A_d)}")
    log.append(f"  B = {_fstr(B_n, B_d)}")
    log.append(f"  C = {C}")
    log.append(f"  D = {D_val}")
    log.append(f"  E = {E}")
    log.append("")

    ec = (f"({_fstr(A_n,A_d)})x²  +  ({_fstr(B_n,B_d)})y²  "
          f"+  ({C})x  +  ({D_val})y  +  ({E})  =  0")
    log.append("── Ecuación General resultante ──")
    log.append("")
    log.append(f"  {ec}")

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
        return "Degenerada", "A = 0 y B = 0. No representa una cónica estándar."
    if az or bz:
        cual = "A" if az else "B"
        return "Parábola", (
            f"Exactamente uno de los coeficientes es cero ({cual} = 0)  →  Parábola.\n"
            f"  • A = {_fmt(A)}, B = {_fmt(B)}"
        )
    if abs(A - B) < eps:
        return "Circunferencia", (
            f"A = B = {_fmt(A)} y ambos son distintos de cero  →  Circunferencia.\n"
            f"  • Cuando los coeficientes de x² e y² son iguales, la figura es un círculo."
        )
    if (A > 0) == (B > 0):
        return "Elipse", (
            f"A = {_fmt(A)} y B = {_fmt(B)} tienen el mismo signo, pero A ≠ B  →  Elipse.\n"
            f"  • Coeficientes positivos distintos producen una elipse."
        )
    return "Hipérbola", (
        f"A = {_fmt(A)} y B = {_fmt(B)} tienen signos opuestos  →  Hipérbola.\n"
        f"  • Coeficientes de signos contrarios producen una hipérbola."
    )


def construir_forma_canonica(A: float, B: float, C: float, D: float, E: float) -> dict:
    """
    Transforma la ecuación general Ax²+By²+Cx+Dy+E=0 a su forma canónica
    mostrando el procedimiento paso a paso de completar el cuadrado.
    """
    log = ["── Transformación: Ecuación General → Forma Canónica ──"]
    log.append("")
    log.append(f"Partimos de: ({_fmt(A)})x² + ({_fmt(B)})y² + ({_fmt(C)})x + ({_fmt(D)})y + ({_fmt(E)}) = 0")
    log.append("")

    eps = 1e-9
    az = abs(A) < eps
    bz = abs(B) < eps
    h, k, lado_der = 0.0, 0.0, 0.0

    log.append("Paso 1: Pasar el término independiente al lado derecho")
    log.append(f"  ({_fmt(A)})x² + ({_fmt(B)})y² + ({_fmt(C)})x + ({_fmt(D)})y = {_fmt(-E)}")
    log.append("")

    if not az:
        log.append("Paso 2: Completar el cuadrado en x")
        log.append(f"  Factorizamos A = {_fmt(A)} del grupo de x:")
        log.append(f"  {_fmt(A)}·(x² + ({_fmt(C/A)})x) + ({_fmt(B)})y² + ({_fmt(D)})y = {_fmt(-E)}")
        h = -(C / (2 * A))
        comp_x = (C / (2 * A)) ** 2
        log.append(f"  Término a agregar y restar: (C/2A)² = ({_fmt(C/A)}/2)² = {_fmt(comp_x)}")
        log.append(f"  {_fmt(A)}·(x + {_fmt(C/(2*A))})² + ({_fmt(B)})y² + ({_fmt(D)})y")
        log.append(f"    = {_fmt(-E)} + {_fmt(A)}·{_fmt(comp_x)}")
        log.append(f"    = {_fmt(-E + A*comp_x)}")
        log.append(f"  → centro en x: h = -(C/2A) = -({_fmt(C)})/(2·{_fmt(A)}) = {_fmt(h)}")
        lado_der = -E + A * comp_x
        log.append("")
    else:
        log.append("Paso 2: A = 0, no hay término x², se omite completar cuadrado en x")
        lado_der = -E
        log.append("")

    if not bz:
        log.append("Paso 3: Completar el cuadrado en y")
        log.append(f"  Factorizamos B = {_fmt(B)} del grupo de y:")
        k = -(D / (2 * B))
        comp_y = (D / (2 * B)) ** 2
        log.append(f"  Término a agregar y restar: (D/2B)² = ({_fmt(D/B)}/2)² = {_fmt(comp_y)}")
        log.append(f"  Lado derecho pasa a: {_fmt(lado_der)} + {_fmt(B)}·{_fmt(comp_y)} = {_fmt(lado_der + B*comp_y)}")
        lado_der = lado_der + B * comp_y
        log.append(f"  → centro en y: k = -(D/2B) = -({_fmt(D)})/(2·{_fmt(B)}) = {_fmt(k)}")
        log.append("")
    else:
        log.append("Paso 3: B = 0, no hay término y², se omite completar cuadrado en y")
        log.append("")

    log.append("Paso 4: Forma canónica resultante")
    log.append("")

    tipo, _ = clasificar_conica(A, B)

    if tipo == "Circunferencia":
        r2 = lado_der / A if abs(A) > eps else 0
        r = r2 ** 0.5 if r2 > 0 else 0
        log.append(f"  (x - {_fmt(h)})² + (y - {_fmt(k)})² = {_fmt(r2)}")
        log.append(f"  Centro: ({_fmt(h)}, {_fmt(k)})    Radio: r = √{_fmt(r2)} = {_fmt(r):.4f}")
        forma_canonica = f"(x - {_fmt(h)})² + (y - {_fmt(k)})² = {_fmt(r2)}"
        return {"h": h, "k": k, "r2": r2, "r": r, "lado_der": lado_der,
                "forma_canonica": forma_canonica, "log": "\n".join(log)}

    elif tipo == "Elipse":
        a2 = lado_der / A if abs(A) > eps else 1
        b2 = lado_der / B if abs(B) > eps else 1
        log.append(f"  (x - {_fmt(h)})² / {_fmt(a2)}  +  (y - {_fmt(k)})² / {_fmt(b2)}  = 1")
        log.append(f"  Centro: ({_fmt(h)}, {_fmt(k)})")
        log.append(f"  a² = {_fmt(a2)},  b² = {_fmt(b2)}")
        forma_canonica = f"(x-{_fmt(h)})²/{_fmt(a2)} + (y-{_fmt(k)})²/{_fmt(b2)} = 1"
        return {"h": h, "k": k, "a2": a2, "b2": b2, "lado_der": lado_der,
                "forma_canonica": forma_canonica, "log": "\n".join(log)}

    elif tipo == "Hipérbola":
        a2 = lado_der / A if abs(A) > eps else 1
        b2 = lado_der / B if abs(B) > eps else 1
        if A > 0:
            log.append(f"  (x - {_fmt(h)})² / {_fmt(a2)}  -  (y - {_fmt(k)})² / {_fmt(-b2)}  = 1")
            log.append(f"  Eje transverso horizontal, Centro: ({_fmt(h)}, {_fmt(k)})")
        else:
            log.append(f"  (y - {_fmt(k)})² / {_fmt(-b2)}  -  (x - {_fmt(h)})² / {_fmt(a2)}  = 1")
            log.append(f"  Eje transverso vertical, Centro: ({_fmt(h)}, {_fmt(k)})")
        forma_canonica = f"hiperbola: h={_fmt(h)}, k={_fmt(k)}, a2={_fmt(a2)}, b2={_fmt(b2)}"
        return {"h": h, "k": k, "a2": a2, "b2": b2, "lado_der": lado_der,
                "forma_canonica": forma_canonica, "log": "\n".join(log)}

    else:  # Parábola
        if az:
            p = -D / (2 * B) if abs(B) > eps else 0
            log.append(f"  Parábola de eje horizontal")
            log.append(f"  x - {_fmt(h)} = {_fmt(1/(4*p)) if abs(p) > eps else '?'}·(y - {_fmt(k)})²")
        else:
            p = -C / (2 * A) if abs(A) > eps else 0
            log.append(f"  Parábola de eje vertical")
            log.append(f"  y - {_fmt(k)} = {_fmt(1/(4*p)) if abs(p) > eps else '?'}·(x - {_fmt(h)})²")
        log.append(f"  Vértice: ({_fmt(h)}, {_fmt(k)})")
        forma_canonica = f"parabola: vertice=({_fmt(h)},{_fmt(k)})"
        return {"h": h, "k": k, "p": p, "lado_der": lado_der,
                "forma_canonica": forma_canonica, "log": "\n".join(log)}


def expansion_canonica_a_general(A: float, B: float,
                                  h: float, k: float,
                                  lado_der: float = 0,
                                  tipo: str = "") -> dict:
    """
    Dado el centro (h, k) y los coeficientes A, B,
    expande la forma canónica de vuelta a Ax²+By²+Cx+Dy+E=0
    mostrando cada paso algebraico de manera clara.
    """
    log = ["── Procedimiento Inverso: Forma Canónica → Ecuación General ──"]
    log.append("")
    log.append(f"Partimos de la forma canónica con centro/vértice (h, k) = ({_fmt(h)}, {_fmt(k)})")
    log.append("")

    log.append("Paso 1: Expandir A·(x - h)²")
    log.append(f"  A·(x - {_fmt(h)})²")
    log.append(f"  = A·(x² - 2·{_fmt(h)}·x + ({_fmt(h)})²)")
    log.append(f"  = A·x² - {_fmt(2*h)}·A·x + {_fmt(h*h)}·A")
    log.append("")

    log.append("Paso 2: Expandir B·(y - k)²")
    log.append(f"  B·(y - {_fmt(k)})²")
    log.append(f"  = B·(y² - 2·{_fmt(k)}·y + ({_fmt(k)})²)")
    log.append(f"  = B·y² - {_fmt(2*k)}·B·y + {_fmt(k*k)}·B")
    log.append("")

    C_val = -2 * h * A
    D_val = -2 * k * B
    E_val = (h * h * A) + (k * k * B) - lado_der

    log.append("Paso 3: Reunir coeficientes")
    log.append(f"  C = -2·h·A = -2·({_fmt(h)})·({_fmt(A)}) = {_fmt(C_val)}")
    log.append(f"  D = -2·k·B = -2·({_fmt(k)})·({_fmt(B)}) = {_fmt(D_val)}")
    log.append(f"  E = h²·A + k²·B - lado_der")
    log.append(f"    = ({_fmt(h*h)})·({_fmt(A)}) + ({_fmt(k*k)})·({_fmt(B)}) - ({_fmt(lado_der)})")
    log.append(f"    = {_fmt(E_val)}")
    log.append("")

    log.append("Paso 4: Ecuación general reconstruida")
    log.append("")
    ec = (f"({_fmt(A)})x²  +  ({_fmt(B)})y²  +  ({_fmt(C_val)})x  "
          f"+  ({_fmt(D_val)})y  +  ({_fmt(E_val)})  =  0")
    log.append(f"  {ec}")
    log.append("")
    log.append("Verificación: los coeficientes A, B, C, D, E recuperados deben coincidir")
    log.append("con los calculados a partir del RUT.")

    return {
        "C": C_val, "D": D_val, "E": E_val,
        "ecuacion_str": ec,
        "log": "\n".join(log)
    }


def determinar_caso_limite(d8: int) -> dict:
    residuo = d8 % 3
    casos = {
        0: ("Removible", 1,
            f"d8 = {d8}  →  {d8} mod 3 = 0  →  Caso 1: Discontinuidad Removible.\n"
            f"Se construye una función racional con factor común que se anula en x = a."),
        1: ("De Salto", 2,
            f"d8 = {d8}  →  {d8} mod 3 = 1  →  Caso 2: Discontinuidad de Salto.\n"
            f"Se construyen dos tramos lineales con valores distintos al acercarse a x = a."),
        2: ("Infinita", 3,
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
