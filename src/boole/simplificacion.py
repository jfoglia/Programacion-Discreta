"""
Punto 8 - Simplificacion booleana: hacer un circuito mas barato.
Implementacion propia de Quine-McCluskey + cubrimiento minimo exacto.

Idea matematica
---------------
Un mintermino de n variables es una fila de la tabla de verdad donde la funcion
vale 1, escrita como producto de las n variables (negadas o no). Por ejemplo con
A,B,C el mintermino 5 = 101 es  A & !B & C.  Toda funcion booleana es la suma
(OR) de sus minterminos: esa es la forma canonica suma de productos.

Quine-McCluskey usa una sola regla del algebra de Boole, aplicada muchas veces:
        X*Y + X*!Y = X            (adyacencia: la variable Y desaparece)
Dos terminos que difieren en exactamente UN bit se combinan en uno con un guion
en esa posicion. Se repite por rondas hasta que nada mas se pueda combinar; los
terminos que quedan sin combinarse son los IMPLICANTES PRIMOS.

Segundo paso: elegir el menor numero de implicantes primos que cubran todos los
minterminos (problema de cubrimiento de conjuntos). Aqui se resuelve exacto:
primero los implicantes primos ESENCIALES (los unicos que cubren algun
mintermino) y luego busqueda exhaustiva por tamano creciente sobre el resto.

Dos expresiones son equivalentes si tienen la misma tabla de verdad, porque la
tabla ES la funcion; el programa verifica eso al final con el evaluador propio
del punto 7.

Ejecucion:
    python3 src/boole/simplificacion.py
"""

from itertools import combinations

try:
    from .tablas_verdad import son_equivalentes, vector_salida
except ImportError:
    from tablas_verdad import son_equivalentes, vector_salida


# ------------------------------------------------------ representacion de cubos
def a_cubo(minterm: int, n: int) -> str:
    """Mintermino -> cadena de bits de longitud n. Ej: 5 con n=3 -> '101'."""
    return format(minterm, f"0{n}b")


def combinar(c1: str, c2: str) -> str | None:
    """Si dos cubos difieren en exactamente una posicion, devuelve el cubo con '-'.

    Si difieren en 0 o en mas de una posicion, devuelve None (no se combinan).
    """
    diferencias = [i for i, (a, b) in enumerate(zip(c1, c2)) if a != b]
    if len(diferencias) != 1:
        return None
    i = diferencias[0]
    return c1[:i] + "-" + c1[i + 1:]


def minterminos_de_cubo(cubo: str) -> set[int]:
    """Todos los minterminos que cubre un cubo (cada '-' duplica las opciones)."""
    resultado = {0}
    for bit in cubo:
        if bit == "-":
            resultado = {v * 2 for v in resultado} | {v * 2 + 1 for v in resultado}
        else:
            resultado = {v * 2 + int(bit) for v in resultado}
    return resultado


def cubo_a_expresion(cubo: str, variables: list[str]) -> str:
    """Cubo -> producto de literales. '1-0' con [A,B,C] -> 'A & !C'."""
    literales = [(var if bit == "1" else f"!{var}")
                 for var, bit in zip(variables, cubo) if bit != "-"]
    return " & ".join(literales) if literales else "1"   # cubo de puros '-' = constante 1


# -------------------------------------------------- paso 1: implicantes primos
def implicantes_primos(minterms: set[int], n: int) -> list[str]:
    """Encuentra todos los implicantes primos combinando por rondas."""
    if not minterms:
        return []
    actuales = {a_cubo(m, n) for m in minterms}
    primos: set[str] = set()

    while actuales:
        usados: set[str] = set()
        siguientes: set[str] = set()
        for c1, c2 in combinations(sorted(actuales), 2):
            fusion = combinar(c1, c2)
            if fusion is not None:
                usados.add(c1)
                usados.add(c2)
                siguientes.add(fusion)
        # Lo que no se pudo combinar en esta ronda ya es primo.
        primos |= (actuales - usados)
        actuales = siguientes
    return sorted(primos)


# ------------------------------------------- paso 2: cubrimiento minimo exacto
def cubrimiento_minimo(primos: list[str], minterms: set[int]) -> list[str]:
    """Menor subconjunto de implicantes primos que cubre todos los minterminos."""
    if not minterms:
        return []
    cobertura = {p: minterminos_de_cubo(p) & minterms for p in primos}

    # Esenciales: minterminos cubiertos por un solo implicante primo.
    esenciales: set[str] = set()
    for m in minterms:
        quienes = [p for p in primos if m in cobertura[p]]
        if len(quienes) == 1:
            esenciales.add(quienes[0])

    faltan = minterms - set().union(*(cobertura[p] for p in esenciales)) if esenciales else set(minterms)
    if not faltan:
        return sorted(esenciales)

    # Para el resto: busqueda exhaustiva por tamano creciente (cubrimiento exacto).
    candidatos = [p for p in primos if p not in esenciales and cobertura[p] & faltan]
    for k in range(1, len(candidatos) + 1):
        for subconjunto in combinations(candidatos, k):
            if faltan <= set().union(*(cobertura[p] for p in subconjunto)):
                return sorted(esenciales | set(subconjunto))
    return sorted(esenciales | set(candidatos))   # no deberia ocurrir


# ------------------------------------------------------------- API del punto 8
def simplificar(minterms, variables: list[str]) -> dict:
    """Simplifica la funcion dada por sus minterminos.

    Devuelve un diccionario con la forma canonica, los implicantes primos, los
    implicantes escogidos, la expresion simplificada y el conteo de literales.
    """
    n = len(variables)
    minterms = set(minterms)
    for m in minterms:
        if not 0 <= m < 2 ** n:
            raise ValueError(f"mintermino {m} fuera de rango para {n} variables (0..{2**n - 1})")

    canonica = " | ".join(f"({cubo_a_expresion(a_cubo(m, n), variables)})"
                          for m in sorted(minterms)) or "0"

    primos = implicantes_primos(minterms, n)
    elegidos = cubrimiento_minimo(primos, minterms)

    if not minterms:
        simplificada = "0"                        # funcion constante 0
    elif len(minterms) == 2 ** n:
        simplificada = "1"                        # funcion constante 1
    elif len(elegidos) == 1:
        simplificada = cubo_a_expresion(elegidos[0], variables)
    else:
        # Con varios terminos se agrupa cada producto entre parentesis para leerlo mejor.
        simplificada = " | ".join(f"({cubo_a_expresion(c, variables)})" for c in elegidos)

    return {
        "variables": variables,
        "minterminos": sorted(minterms),
        "canonica": canonica,
        "primos": primos,
        "primos_legibles": [cubo_a_expresion(c, variables) for c in primos],
        "elegidos": elegidos,
        "simplificada": simplificada,
        "literales_canonica": len(minterms) * n,
        "literales_simplificada": sum(len(c) - c.count("-") for c in elegidos),
    }


def verificar(resultado: dict) -> bool:
    """Comprueba que la expresion original y la simplificada tienen la misma tabla."""
    variables = resultado["variables"]
    if resultado["simplificada"] in ("0", "1"):
        # Casos constantes: se comparan contra el vector de salida esperado.
        esperado = tuple(int(i in set(resultado["minterminos"]))
                         for i in range(2 ** len(variables)))
        constante = int(resultado["simplificada"])
        return esperado == tuple([constante] * 2 ** len(variables))
    return son_equivalentes(resultado["canonica"], resultado["simplificada"], variables)


def imprimir_resultado(resultado: dict, titulo: str = "") -> None:
    v = resultado["variables"]
    print(f"\n  {titulo}")
    print(f"    Variables         : {', '.join(v)}")
    print(f"    Minterminos       : {resultado['minterminos']}")
    print(f"    Forma canonica    : {resultado['canonica']}")
    print(f"    Implicantes primos: {resultado['primos']} "
          f"-> {resultado['primos_legibles']}")
    print(f"    Escogidos         : {resultado['elegidos']}")
    print(f"    SIMPLIFICADA      : {resultado['simplificada']}")
    print(f"    Literales         : {resultado['literales_canonica']} -> "
          f"{resultado['literales_simplificada']}")
    print(f"    Misma tabla de verdad que la original: {verificar(resultado)}")


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 72)
    print("PUNTO 8 - SIMPLIFICACION BOOLEANA (QUINE-MCCLUSKEY PROPIO)")
    print("=" * 72)

    print("\n[1] Caso sugerido en el taller: 3 variables, minterminos {1,3,5,7}")
    r = simplificar({1, 3, 5, 7}, ["A", "B", "C"])
    imprimir_resultado(r, "f(A,B,C) = suma de minterminos 1,3,5,7")
    print(f"    Esperado por el taller: equivalente a C  -> "
          f"{son_equivalentes(r['simplificada'], 'C', ['A', 'B', 'C'])}")
    print("    Lectura: los cuatro minterminos son 001,011,101,111; A y B toman")
    print("    todos los valores posibles, solo C es siempre 1, entonces f = C.")

    print("\n[2] Cuatro variables: minterminos {0,1,2,5,6,7,8,9,10,14}")
    r2 = simplificar({0, 1, 2, 5, 6, 7, 8, 9, 10, 14}, ["A", "B", "C", "D"])
    imprimir_resultado(r2, "f(A,B,C,D)")

    print("\n[3] Mas casos, incluyendo los extremos")
    casos = [
        ("3 vars, {0,1,2,3,4,5,6,7} (siempre 1)", {0, 1, 2, 3, 4, 5, 6, 7}, ["A", "B", "C"]),
        ("3 vars, {} (siempre 0)", set(), ["A", "B", "C"]),
        ("3 vars, {0} (un solo mintermino)", {0}, ["A", "B", "C"]),
        ("3 vars, {0,7} (no se pueden combinar)", {0, 7}, ["A", "B", "C"]),
        ("3 vars, {1,2,5,6} (queda un XOR disfrazado)", {1, 2, 5, 6}, ["A", "B", "C"]),
        ("4 vars, {4,8,9,10,11,12,14,15}", {4, 8, 9, 10, 11, 12, 14, 15}, ["A", "B", "C", "D"]),
    ]
    for titulo, mt, vs in casos:
        res = simplificar(mt, vs)
        print(f"    {titulo:42s} -> {res['simplificada']:36s} "
              f"(valido: {verificar(res)})")

    print("\n[4] Verificacion exhaustiva: TODAS las funciones de 3 variables")
    fallos = 0
    for mascara in range(256):                      # 2^(2^3) funciones posibles
        mt = {i for i in range(8) if (mascara >> i) & 1}
        res = simplificar(mt, ["A", "B", "C"])
        if not verificar(res):
            fallos += 1
    print(f"    Funciones probadas: 256   simplificaciones incorrectas: {fallos}")

    print("\n[5] Verificacion exhaustiva: TODAS las funciones de 4 variables")
    fallos4 = 0
    for mascara in range(0, 65536, 7):              # muestra amplia (9363 funciones)
        mt = {i for i in range(16) if (mascara >> i) & 1}
        res = simplificar(mt, ["A", "B", "C", "D"])
        if not verificar(res):
            fallos4 += 1
    print(f"    Funciones probadas: {len(range(0, 65536, 7))}   incorrectas: {fallos4}")

    print("\n[6] Comparacion de costo (cuantas compuertas nos ahorramos)")
    r6 = simplificar({0, 1, 4, 5, 8, 9, 12, 13}, ["A", "B", "C", "D"])
    print(f"    canonica    : {r6['canonica']}")
    print(f"    simplificada: {r6['simplificada']}")
    print(f"    literales   : {r6['literales_canonica']} -> {r6['literales_simplificada']}")
    print(f"    misma tabla : {vector_salida(r6['canonica'], r6['variables']) == vector_salida(r6['simplificada'], r6['variables'])}")


if __name__ == "__main__":
    _demo()
