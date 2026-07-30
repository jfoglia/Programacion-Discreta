"""
Punto 9 - Shannon: medir informacion en un mensaje (+ Huffman como extension).

Idea matematica
---------------
Si un simbolo s aparece con probabilidad p(s), su "sorpresa" es -log2 p(s) bits:
un simbolo casi seguro (p cerca de 1) aporta casi 0 bits, uno raro aporta muchos.
La entropia es el promedio de esa sorpresa:

        H = - sum_i p_i * log2(p_i)     [bits por simbolo]

Propiedades que el programa comprueba:
  * H = 0 si el texto usa un solo simbolo (no hay incertidumbre).
  * H es maxima e igual a log2(k) cuando los k simbolos son equiprobables.
  * H NO depende de la longitud del texto, solo de las proporciones: "AB" y
    "AABB" tienen la misma entropia (1 bit por simbolo).

Teorema de Shannon (fuente sin memoria): ningun codigo libre de prefijos puede
tener longitud promedio menor que H. Huffman llega a  H <= L < H + 1, y el
programa lo verifica en cada ejemplo.

Ejecucion:
    python3 src/info/shannon.py
"""

import heapq
from collections import Counter
from math import log2


# ------------------------------------------------------------ frecuencias y H
def frecuencias(texto: str) -> dict[str, int]:
    """Cuenta cuantas veces aparece cada simbolo (cada caracter es un simbolo)."""
    return dict(Counter(texto))


def probabilidades(texto: str) -> dict[str, float]:
    """p(s) = veces que aparece s / longitud del texto."""
    if not texto:
        return {}
    total = len(texto)
    return {s: c / total for s, c in frecuencias(texto).items()}


def entropia(texto: str) -> float:
    """H = -sum p_i log2 p_i, en bits por simbolo. Texto vacio -> 0."""
    return -sum(p * log2(p) for p in probabilidades(texto).values())


def entropia_maxima(texto: str) -> float:
    """log2(k) con k = numero de simbolos distintos: el techo de H para ese alfabeto."""
    k = len(set(texto))
    return log2(k) if k > 0 else 0.0


def redundancia(texto: str) -> float:
    """Cuanto le falta al texto para ser 'maximamente impredecible' (en bits)."""
    return entropia_maxima(texto) - entropia(texto)


def informe(texto: str, nombre: str = "texto", mostrar_tabla: bool = True) -> dict:
    """Imprime frecuencias, probabilidades, sorpresa y entropia. Devuelve el resumen."""
    H = entropia(texto)
    Hmax = entropia_maxima(texto)
    print(f"\n  {nombre}: {texto[:56]!r}{'...' if len(texto) > 56 else ''}")
    print(f"    longitud = {len(texto)}, simbolos distintos = {len(set(texto))}")
    if mostrar_tabla:
        print(f"    {'simbolo':9s} {'frec':>5s} {'p':>8s} {'-log2 p':>9s} {'aporte':>8s}")
        for s, c in sorted(frecuencias(texto).items(), key=lambda kv: (-kv[1], kv[0])):
            p = c / len(texto)
            print(f"    {repr(s):9s} {c:5d} {p:8.4f} {-log2(p):9.4f} {-p * log2(p):8.4f}")
    print(f"    H = {H:.4f} bits/simbolo   (maximo posible log2({len(set(texto))}) "
          f"= {Hmax:.4f}, redundancia = {Hmax - H:.4f})")
    print(f"    Informacion total del mensaje: {H * len(texto):.2f} bits")
    return {"nombre": nombre, "H": H, "Hmax": Hmax, "longitud": len(texto),
            "distintos": len(set(texto))}


def comparar(texto_a: str, texto_b: str, nombre_a: str = "A", nombre_b: str = "B") -> str:
    """Compara dos textos y explica cual tiene mas entropia y por que."""
    ha, hb = entropia(texto_a), entropia(texto_b)
    if abs(ha - hb) < 1e-12:
        return (f"  {nombre_a} y {nombre_b} tienen la MISMA entropia ({ha:.4f} bits/simbolo): "
                f"sus proporciones de simbolos coinciden.")
    mayor, menor = (nombre_a, nombre_b) if ha > hb else (nombre_b, nombre_a)
    h_mayor, h_menor = (ha, hb) if ha > hb else (hb, ha)
    return (f"  {mayor} tiene MAYOR entropia ({h_mayor:.4f} vs {h_menor:.4f} bits/simbolo): "
            f"reparte sus apariciones entre mas simbolos y de forma mas parecida, "
            f"asi que es mas dificil predecir el siguiente caracter. {menor} es mas "
            f"repetitivo, entonces cada simbolo nuevo sorprende menos.")


# ------------------------------------------- extension opcional: codigo Huffman
def codigo_huffman(texto: str) -> dict[str, str]:
    """Construye el codigo de Huffman: {simbolo: cadena de bits}.

    Algoritmo voraz: se toman repetidamente los dos nodos de menor frecuencia y
    se unen en uno nuevo cuya frecuencia es la suma. Los simbolos raros quedan
    mas profundos en el arbol, o sea con codigos mas largos.
    """
    frec = frecuencias(texto)
    if not frec:
        return {}
    if len(frec) == 1:                       # caso borde: un solo simbolo -> 1 bit
        return {next(iter(frec)): "0"}

    contador = 0                             # desempate estable para el monticulo
    monticulo: list = []
    for s, c in sorted(frec.items()):
        heapq.heappush(monticulo, (c, contador, {"hoja": s}))
        contador += 1

    while len(monticulo) > 1:
        c1, _, n1 = heapq.heappop(monticulo)
        c2, _, n2 = heapq.heappop(monticulo)
        heapq.heappush(monticulo, (c1 + c2, contador, {"izq": n1, "der": n2}))
        contador += 1

    codigos: dict[str, str] = {}

    def recorrer(nodo, prefijo: str) -> None:
        if "hoja" in nodo:
            codigos[nodo["hoja"]] = prefijo
        else:
            recorrer(nodo["izq"], prefijo + "0")
            recorrer(nodo["der"], prefijo + "1")

    recorrer(monticulo[0][2], "")
    return codigos


def longitud_promedio(texto: str, codigos: dict[str, str]) -> float:
    """L = sum p_i * len(codigo_i): bits por simbolo que gasta el codigo."""
    return sum(p * len(codigos[s]) for s, p in probabilidades(texto).items())


def codificar(texto: str, codigos: dict[str, str]) -> str:
    return "".join(codigos[c] for c in texto)


def decodificar(bits: str, codigos: dict[str, str]) -> str:
    """Decodifica leyendo bit por bit: el codigo es libre de prefijos."""
    inverso = {v: k for k, v in codigos.items()}
    salida, actual = [], ""
    for bit in bits:
        actual += bit
        if actual in inverso:
            salida.append(inverso[actual])
            actual = ""
    if actual:
        raise ValueError("la cadena de bits no corresponde a un mensaje completo")
    return "".join(salida)


def informe_huffman(texto: str, nombre: str = "texto") -> dict:
    """Compara la longitud promedio de Huffman con la entropia (H <= L < H+1)."""
    codigos = codigo_huffman(texto)
    H = entropia(texto)
    L = longitud_promedio(texto, codigos)
    bits_huffman = len(codificar(texto, codigos))
    bits_fijos = len(texto) * max(1, (len(set(texto)) - 1).bit_length())
    print(f"\n  Huffman para {nombre}:")
    print(f"    codigos: {dict(sorted(codigos.items(), key=lambda kv: (len(kv[1]), kv[0])))}")
    print(f"    H = {H:.4f}   L = {L:.4f} bits/simbolo   se cumple H <= L < H+1: "
          f"{H - 1e-12 <= L < H + 1}")
    print(f"    mensaje codificado: {bits_huffman} bits vs {bits_fijos} bits con "
          f"codigo de longitud fija")
    print(f"    decodificacion exacta: "
          f"{decodificar(codificar(texto, codigos), codigos) == texto}")
    return {"H": H, "L": L, "bits": bits_huffman}


# ---------------------------------------------------------------- demostracion
REPETITIVO = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAB"
VARIADO = "La entropia mide incertidumbre, no longitud del texto."


def _demo() -> None:
    print("=" * 72)
    print("PUNTO 9 - ENTROPIA DE SHANNON")
    print("=" * 72)

    print("\n[1] Un mensaje muy repetitivo y uno mas variado")
    a = informe(REPETITIVO, "repetitivo")
    b = informe(VARIADO, "variado")
    print("\n  Comparacion:")
    print(comparar(VARIADO, REPETITIVO, "'variado'", "'repetitivo'"))
    print(f"  H(variado) > H(repetitivo): {b['H'] > a['H']}")

    print("\n[2] Casos con respuesta conocida")
    casos = [
        ("un solo simbolo   'AAAA'", "AAAA", 0.0),
        ("dos equiprobables 'AB'", "AB", 1.0),
        ("dos equiprobables 'AABB'", "AABB", 1.0),
        ("cuatro equiprob.  'ABCD'", "ABCD", 2.0),
        ("ocho equiprob.    'ABCDEFGH'", "ABCDEFGH", 3.0),
        ("sesgado           'AAAB'", "AAAB", 0.8113),
    ]
    for nombre, texto, esperado in casos:
        H = entropia(texto)
        print(f"  {nombre:30s} H = {H:.4f}  esperado {esperado:.4f}  "
              f"ok: {abs(H - esperado) < 1e-4}")

    print("\n[3] La entropia no depende de la longitud, sino de las proporciones")
    for texto in ("AB", "AABB", "AAAABBBB", "AB" * 50):
        etiqueta = repr(texto) if len(texto) <= 18 else f"'AB' repetido {len(texto)//2} veces"
        print(f"  {etiqueta:26s} longitud {len(texto):3d} -> H = {entropia(texto):.4f}")

    print("\n[4] Entropia maxima y redundancia")
    for texto, nombre in [(REPETITIVO, "repetitivo"), (VARIADO, "variado"),
                          ("ABCDEFGH", "equiprobable")]:
        print(f"  {nombre:14s} H = {entropia(texto):.4f}  Hmax = {entropia_maxima(texto):.4f}  "
              f"redundancia = {redundancia(texto):.4f}")
    print("  Un texto equiprobable no tiene redundancia: no se puede comprimir mas.")

    print("\n[5] Extension opcional: codigo de Huffman")
    for texto, nombre in [(REPETITIVO, "'repetitivo'"), (VARIADO, "'variado'"),
                          ("ABCDEFGH", "'equiprobable'")]:
        informe_huffman(texto, nombre)
    print("\n  Nota: cuando las probabilidades son potencias de 1/2, L = H exactamente")
    r = informe_huffman("AAAABBCD", "'AAAABBCD' (p = 1/2, 1/4, 1/8, 1/8)")
    print(f"  L == H en este caso: {abs(r['L'] - r['H']) < 1e-12}")


if __name__ == "__main__":
    _demo()
