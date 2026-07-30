"""
Punto 1 - Cifrado Cesar: cifrar, descifrar y romper por fuerza bruta.

Idea matematica
---------------
Numeramos el alfabeto latino sin enie: A -> 0, B -> 1, ..., Z -> 25.
Cifrar con desplazamiento k es la funcion  E_k(x) = (x + k) mod 26
y descifrar es su inversa  D_k(y) = (y - k) mod 26.
Como sumar k modulo 26 es una biyeccion del conjunto Z_26 en si mismo,
el cifrado es reversible y la inversa es "restar k" (equivalente a sumar 26 - k).

Ejecucion:
    python3 src/cripto/cesar.py
"""

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = len(ALFABETO)  # 26

# Frecuencias aproximadas de las letras en espanol (en porcentaje).
# Solo se usan para ordenar los candidatos del ataque de fuerza bruta:
# el ataque en si prueba las 26 claves, esto unicamente sugiere la mas probable.
FRECUENCIA_ES = {
    "A": 11.53, "B": 2.22, "C": 4.02, "D": 5.01, "E": 12.18, "F": 0.69,
    "G": 1.77, "H": 0.70, "I": 6.25, "J": 0.44, "K": 0.02, "L": 4.97,
    "M": 3.15, "N": 6.71, "O": 8.68, "P": 2.51, "Q": 0.88, "R": 6.87,
    "S": 7.98, "T": 4.63, "U": 2.93, "V": 0.90, "W": 0.02, "X": 0.22,
    "Y": 0.90, "Z": 0.52,
}


def desplazar_letra(letra: str, k: int) -> str:
    """Desplaza UNA letra k posiciones conservando si era mayuscula o minuscula.

    Cualquier caracter que no sea una letra del alfabeto (espacios, signos,
    numeros, tildes) se devuelve sin tocar.
    """
    mayuscula = letra.upper()
    if mayuscula not in ALFABETO:
        return letra
    x = ALFABETO.index(mayuscula)          # letra -> numero
    y = (x + k) % N                         # aritmetica modular
    nueva = ALFABETO[y]                     # numero -> letra
    return nueva if letra.isupper() else nueva.lower()


def cifrar(texto: str, k: int) -> str:
    """E_k aplicada a todo el texto: cada letra se corre k posiciones."""
    return "".join(desplazar_letra(c, k) for c in texto)


def descifrar(texto: str, k: int) -> str:
    """D_k aplicada a todo el texto. Descifrar es cifrar con -k."""
    return cifrar(texto, -k)


def puntaje_espanol(texto: str) -> float:
    """Que tan parecido es el texto al espanol (chi-cuadrado; menor es mejor).

    Compara la cantidad observada de cada letra con la cantidad esperada
    segun FRECUENCIA_ES. Un texto en espanol da un puntaje bajo.
    """
    letras = [c for c in texto.upper() if c in ALFABETO]
    total = len(letras)
    if total == 0:
        return float("inf")
    chi = 0.0
    for letra in ALFABETO:
        observado = letras.count(letra)
        esperado = total * FRECUENCIA_ES[letra] / 100.0
        chi += (observado - esperado) ** 2 / esperado
    return chi


def fuerza_bruta(texto_cifrado: str) -> list[tuple[int, str, float]]:
    """Prueba las 26 claves posibles y devuelve los candidatos.

    Devuelve una lista de (k, texto_descifrado, puntaje) ORDENADA por puntaje,
    asi el primer elemento es el candidato mas probable en espanol.
    El espacio de claves tiene solo 26 elementos (en realidad 25 utiles),
    por eso revisarlo completo es inmediato para un computador.
    """
    candidatos = []
    for k in range(N):
        intento = descifrar(texto_cifrado, k)
        candidatos.append((k, intento, puntaje_espanol(intento)))
    candidatos.sort(key=lambda t: t[2])
    return candidatos


def romper(texto_cifrado: str) -> tuple[int, str]:
    """Devuelve (k_estimado, texto) del mejor candidato del ataque."""
    k, texto, _ = fuerza_bruta(texto_cifrado)[0]
    return k, texto


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 66)
    print("PUNTO 1 - CIFRADO CESAR")
    print("=" * 66)

    ejemplos = [
        ("HOLA UNAL", 3),                                   # caso minimo del taller
        ("Ataque al amanecer, 5 tanques!", 7),              # mayus/minus/signos/numeros
        ("Zzz... el modulo 26 cierra el ciclo", 1),         # prueba el "wrap-around"
    ]

    print("\n[1] Cifrar y descifrar con k conocido")
    for texto, k in ejemplos:
        c = cifrar(texto, k)
        d = descifrar(c, k)
        print(f"  k={k:2d}  original : {texto}")
        print(f"        cifrado  : {c}")
        print(f"        descifrado: {d}   -> recuperado correctamente: {d == texto}")

    print("\n[2] Ataque de fuerza bruta (k desconocido)")
    secreto = cifrar("LA ARITMETICA MODULAR HACE REVERSIBLE EL CIFRADO", 11)
    print(f"  Mensaje interceptado: {secreto}")
    print("  Los 26 desplazamientos posibles (ordenados por parecido al espanol):")
    for k, intento, chi in fuerza_bruta(secreto)[:5]:
        print(f"    k={k:2d}  chi={chi:8.1f}  {intento[:52]}")
    print("    ... (los otros 21 candidatos quedan descartados por el puntaje)")
    k_est, texto_est = romper(secreto)
    print(f"  Clave estimada: k={k_est}  ->  {texto_est}")

    print("\n[3] Propiedades verificadas")
    print(f"  cifrar(texto, 0)  no cambia nada        : {cifrar('UNAL', 0) == 'UNAL'}")
    print(f"  cifrar(texto, 26) == texto (mod 26)     : {cifrar('UNAL', 26) == 'UNAL'}")
    print(f"  cifrar(cifrar(t,4),9) == cifrar(t,13)   : "
          f"{cifrar(cifrar('UNAL', 4), 9) == cifrar('UNAL', 13)}")


if __name__ == "__main__":
    _demo()
