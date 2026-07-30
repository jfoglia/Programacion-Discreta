"""
Punto 2 - RSA de juguete: llaves, cifrado y descifrado.

ADVERTENCIA: esto NO es seguridad real. Los primos son diminutos y se puede
factorizar n a mano. Sirve solo para ver la aritmetica modular funcionando.

Idea matematica
---------------
1. Se toman dos primos p, q y se define n = p*q.
2. phi(n) = (p-1)(q-1) cuenta los enteros de 1..n coprimos con n.
3. Se elige e con gcd(e, phi(n)) = 1. Esa condicion es exactamente la que
   garantiza que e tiene inverso multiplicativo d modulo phi(n).
4. Se calcula d con el algoritmo de Euclides extendido: e*d = 1 (mod phi(n)).
5. Cifrar: C = M^e mod n.   Descifrar: M = C^d mod n.
   Funciona porque C^d = M^(e*d) = M^(1 + t*phi(n)) = M (mod n),
   usando el teorema de Euler / pequeno teorema de Fermat.

Ejecucion:
    python3 src/cripto/rsa_juguete.py
"""


def es_primo(m: int) -> bool:
    """Primalidad por division de prueba hasta la raiz (suficiente para primos chicos)."""
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    d = 3
    while d * d <= m:
        if m % d == 0:
            return False
        d += 2
    return True


def euclides_extendido(a: int, b: int) -> tuple[int, int, int]:
    """Devuelve (g, x, y) con g = gcd(a, b) y a*x + b*y = g (identidad de Bezout).

    Version iterativa: se mantienen los coeficientes de a y b en cada resto.
    """
    r_ant, r_act = a, b
    x_ant, x_act = 1, 0
    y_ant, y_act = 0, 1
    while r_act != 0:
        cociente = r_ant // r_act
        r_ant, r_act = r_act, r_ant - cociente * r_act
        x_ant, x_act = x_act, x_ant - cociente * x_act
        y_ant, y_act = y_act, y_ant - cociente * y_act
    return r_ant, x_ant, y_ant


def mcd(a: int, b: int) -> int:
    """Maximo comun divisor (se obtiene del mismo algoritmo de Euclides)."""
    return euclides_extendido(a, b)[0]


def inverso_modular(a: int, m: int) -> int:
    """Devuelve d en 0..m-1 tal que a*d = 1 (mod m). Falla si gcd(a, m) != 1.

    De Bezout: a*x + m*y = 1  =>  a*x = 1 (mod m)  =>  d = x mod m.
    """
    g, x, _ = euclides_extendido(a, m)
    if g != 1:
        raise ValueError(f"{a} no tiene inverso modulo {m}: gcd = {g} (deberia ser 1)")
    return x % m


def potencia_modular(base: int, exponente: int, modulo: int) -> int:
    """base^exponente mod modulo por cuadrados sucesivos (implementado a mano).

    Se escribe el exponente en binario: cada bit decide si se multiplica el
    resultado por la potencia actual. Hace O(log exponente) multiplicaciones
    y nunca calcula el numero gigante base^exponente.
    """
    if modulo == 1:
        return 0
    if exponente < 0:
        raise ValueError("el exponente debe ser >= 0")
    resultado = 1
    base = base % modulo
    while exponente > 0:
        if exponente & 1:                  # bit menos significativo encendido
            resultado = (resultado * base) % modulo
        base = (base * base) % modulo      # siguiente cuadrado
        exponente >>= 1
    return resultado


def generar_llaves(p: int, q: int, e: int) -> dict:
    """Construye las llaves de RSA a partir de p, q y e. Valida las hipotesis."""
    if not es_primo(p):
        raise ValueError(f"p = {p} no es primo")
    if not es_primo(q):
        raise ValueError(f"q = {q} no es primo")
    if p == q:
        raise ValueError("p y q deben ser primos distintos (si no, phi(n) cambia)")

    n = p * q
    phi = (p - 1) * (q - 1)

    if not 1 < e < phi:
        raise ValueError(f"e = {e} debe cumplir 1 < e < phi(n) = {phi}")
    g = mcd(e, phi)
    if g != 1:
        raise ValueError(
            f"e = {e} no es valido: gcd(e, phi(n)) = {g} != 1, "
            f"entonces e no tiene inverso modulo phi(n) = {phi}"
        )

    d = inverso_modular(e, phi)
    return {
        "p": p, "q": q, "n": n, "phi": phi,
        "e": e, "d": d,
        "publica": (e, n),
        "privada": (d, n),
    }


def cifrar(mensaje: int, publica: tuple[int, int]) -> int:
    """C = M^e mod n. El mensaje debe ser un entero en 0..n-1."""
    e, n = publica
    if not 0 <= mensaje < n:
        raise ValueError(f"el mensaje {mensaje} debe estar entre 0 y n-1 = {n - 1}")
    return potencia_modular(mensaje, e, n)


def descifrar(cifrado: int, privada: tuple[int, int]) -> int:
    """M = C^d mod n."""
    d, n = privada
    if not 0 <= cifrado < n:
        raise ValueError(f"el cifrado {cifrado} debe estar entre 0 y n-1 = {n - 1}")
    return potencia_modular(cifrado, d, n)


def cifrar_texto(texto: str, publica: tuple[int, int]) -> list[int]:
    """Cifra letra por letra usando su codigo Unicode. Requiere n > ord(c)."""
    return [cifrar(ord(c), publica) for c in texto]


def descifrar_texto(bloques: list[int], privada: tuple[int, int]) -> str:
    return "".join(chr(descifrar(c, privada)) for c in bloques)


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 66)
    print("PUNTO 2 - RSA DE JUGUETE")
    print("=" * 66)

    print("\n[1] Caso de prueba obligatorio del taller (p=61, q=53, e=17, M=65)")
    llaves = generar_llaves(61, 53, 17)
    for clave in ("n", "phi", "e", "d"):
        print(f"  {clave:4s} = {llaves[clave]}")
    C = cifrar(65, llaves["publica"])
    M = descifrar(C, llaves["privada"])
    print(f"  C = 65^17 mod 3233 = {C}")
    print(f"  M = C^{llaves['d']} mod 3233 = {M}")
    esperado = {"n": 3233, "phi": 3120, "d": 2753}
    ok = all(llaves[k] == v for k, v in esperado.items()) and C == 2790 and M == 65
    print(f"  Coincide con los valores esperados (n=3233, phi=3120, d=2753, C=2790): {ok}")

    print("\n[2] Otro par de primos y un texto completo")
    llaves2 = generar_llaves(101, 103, 7)  # n = 10403 > 1114111? no, alcanza para ASCII
    print(f"  p=101 q=103 -> n={llaves2['n']}, phi={llaves2['phi']}, e=7, d={llaves2['d']}")
    print(f"  Verificacion e*d mod phi = {(llaves2['e'] * llaves2['d']) % llaves2['phi']} (debe ser 1)")
    texto = "UNAL 2026"
    bloques = cifrar_texto(texto, llaves2["publica"])
    recuperado = descifrar_texto(bloques, llaves2["privada"])
    print(f"  '{texto}' -> {bloques}")
    print(f"  descifrado -> '{recuperado}'  correcto: {recuperado == texto}")

    print("\n[3] Todos los mensajes 0..n-1 se recuperan (p=17, q=11, e=7)")
    llaves3 = generar_llaves(17, 11, 7)
    fallos = [m for m in range(llaves3["n"])
              if descifrar(cifrar(m, llaves3["publica"]), llaves3["privada"]) != m]
    print(f"  n={llaves3['n']}, d={llaves3['d']}; mensajes que fallan: {len(fallos)}")

    print("\n[4] Manejo de errores (e invalido, p no primo, mensaje fuera de rango)")
    casos = [
        ("e no coprimo con phi", lambda: generar_llaves(61, 53, 13)),   # gcd(13,3120)=13
        ("p no primo",           lambda: generar_llaves(60, 53, 17)),
        ("mensaje >= n",         lambda: cifrar(4000, llaves["publica"])),
    ]
    for nombre, accion in casos:
        try:
            accion()
            print(f"  {nombre}: NO se detecto (mal)")
        except ValueError as err:
            print(f"  {nombre}: detectado -> {err}")


if __name__ == "__main__":
    _demo()
