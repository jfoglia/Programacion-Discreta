"""
Punto 10 - Primer simulador cuantico: bits, qubits y mediciones.

Se usa solo la libreria estandar (numeros complejos nativos de Python) para
que quede claro que toda la matematica esta implementada aqui: el producto
matriz-vector, la normalizacion y la regla de medida.

Idea matematica
---------------
Estado de un qubit: vector de dos entradas complejas
        |psi> = alpha|0> + beta|1>  <->  (alpha, beta)
con la condicion de normalizacion |alpha|^2 + |beta|^2 = 1.

Las compuertas son matrices 2x2 unitarias y aplicarlas es multiplicar
matriz por vector:
        X = [[0,1],[1,0]]        intercambia |0> y |1> (NOT cuantico)
        Z = [[1,0],[0,-1]]       cambia el signo de la amplitud de |1>
        H = (1/raiz2)[[1,1],[1,-1]]  crea superposicion

Regla de Born (medida): P(0) = |alpha|^2, P(1) = |beta|^2. La medida es
aleatoria y destruye la superposicion (el estado colapsa a |0> o |1>).
Como las matrices son unitarias, la suma de probabilidades siempre es 1.

Ejecucion:
    python3 src/cuantica/qubit.py
"""

import random
from math import isclose, sqrt

# Vectores base
KET0: tuple[complex, complex] = (1 + 0j, 0 + 0j)
KET1: tuple[complex, complex] = (0 + 0j, 1 + 0j)

# Compuertas como matrices 2x2 (filas)
INV_R2 = 1 / sqrt(2)
X = ((0 + 0j, 1 + 0j), (1 + 0j, 0 + 0j))
Z = ((1 + 0j, 0 + 0j), (0 + 0j, -1 + 0j))
H = ((INV_R2 + 0j, INV_R2 + 0j), (INV_R2 + 0j, -INV_R2 + 0j))
I = ((1 + 0j, 0 + 0j), (0 + 0j, 1 + 0j))

COMPUERTAS = {"X": X, "Z": Z, "H": H, "I": I}


class Qubit:
    """Un qubit: estado = vector de dos amplitudes complejas."""

    def __init__(self, alpha: complex = 1 + 0j, beta: complex = 0 + 0j,
                 rng: random.Random | None = None):
        norma = abs(alpha) ** 2 + abs(beta) ** 2
        if isclose(norma, 0.0, abs_tol=1e-12):
            raise ValueError("el vector cero no es un estado valido")
        if not isclose(norma, 1.0, abs_tol=1e-9):
            # Se normaliza para que las probabilidades sumen 1.
            factor = 1 / sqrt(norma)
            alpha, beta = alpha * factor, beta * factor
        self.estado: tuple[complex, complex] = (complex(alpha), complex(beta))
        self.rng = rng or random.Random()

    # ------------------------------------------------------------- compuertas
    def aplicar(self, matriz, nombre: str = "") -> "Qubit":
        """Multiplica matriz (2x2) por el vector de estado. Devuelve self para encadenar."""
        a, b = self.estado
        nuevo = (matriz[0][0] * a + matriz[0][1] * b,
                 matriz[1][0] * a + matriz[1][1] * b)
        self.estado = nuevo
        norma = sum(abs(c) ** 2 for c in nuevo)
        if not isclose(norma, 1.0, abs_tol=1e-9):
            raise ValueError(f"la compuerta {nombre or matriz} no es unitaria (norma {norma})")
        return self

    def x(self) -> "Qubit":
        return self.aplicar(X, "X")

    def z(self) -> "Qubit":
        return self.aplicar(Z, "Z")

    def h(self) -> "Qubit":
        return self.aplicar(H, "H")

    def aplicar_circuito(self, nombres: str) -> "Qubit":
        """Aplica una secuencia como 'HZH' de izquierda a derecha (orden temporal)."""
        for nombre in nombres.upper():
            if nombre not in COMPUERTAS:
                raise ValueError(f"compuerta desconocida: {nombre}")
            self.aplicar(COMPUERTAS[nombre], nombre)
        return self

    # ----------------------------------------------------------- probabilidades
    def probabilidades(self) -> tuple[float, float]:
        """Regla de Born: (|alpha|^2, |beta|^2)."""
        a, b = self.estado
        return (abs(a) ** 2, abs(b) ** 2)

    def medir(self) -> int:
        """Una medida: devuelve 0 o 1 al azar segun las probabilidades y COLAPSA."""
        p0, _ = self.probabilidades()
        resultado = 0 if self.rng.random() < p0 else 1
        self.estado = KET0 if resultado == 0 else KET1   # colapso
        return resultado

    def medir_muchas(self, repeticiones: int = 1000) -> dict[int, int]:
        """Frecuencias observadas al repetir el experimento (preparar + medir).

        Importante: se vuelve a preparar el MISMO estado antes de cada medida,
        porque medir destruye la superposicion.
        """
        estado_inicial = self.estado
        conteo = {0: 0, 1: 0}
        for _ in range(repeticiones):
            self.estado = estado_inicial
            conteo[self.medir()] += 1
        self.estado = estado_inicial
        return conteo

    # ---------------------------------------------------------------- utilidades
    def __eq__(self, otro) -> bool:
        """Igualdad numerica de amplitudes (tolerante a error de punto flotante)."""
        if not isinstance(otro, Qubit):
            return NotImplemented
        return all(abs(x - y) < 1e-9 for x, y in zip(self.estado, otro.estado))

    def __str__(self) -> str:
        a, b = self.estado
        return f"({_c(a)})|0> + ({_c(b)})|1>"

    def __repr__(self) -> str:
        return f"Qubit{self.estado}"


def _c(z: complex) -> str:
    """Formatea un complejo corto, omitiendo la parte imaginaria si es cero."""
    if abs(z.imag) < 1e-12:
        return f"{z.real:+.4f}"
    return f"{z.real:+.4f}{z.imag:+.4f}i"


def cero(rng: random.Random | None = None) -> Qubit:
    return Qubit(*KET0, rng=rng)


def uno(rng: random.Random | None = None) -> Qubit:
    return Qubit(*KET1, rng=rng)


def reporte(q: Qubit, etiqueta: str, repeticiones: int = 1000) -> dict:
    """Imprime estado, probabilidades y frecuencias de `repeticiones` medidas."""
    p0, p1 = q.probabilidades()
    conteo = q.medir_muchas(repeticiones)
    f0, f1 = conteo[0] / repeticiones, conteo[1] / repeticiones
    print(f"  {etiqueta:16s} estado = {q}")
    print(f"  {'':16s} P(0) = {p0:.4f}  P(1) = {p1:.4f}   (suma = {p0 + p1:.6f})")
    print(f"  {'':16s} {repeticiones} medidas -> 0: {conteo[0]} ({f0:.3f}), "
          f"1: {conteo[1]} ({f1:.3f})")
    return {"p0": p0, "p1": p1, "conteo": conteo}


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 72)
    print("PUNTO 10 - SIMULADOR DE UN QUBIT")
    print("=" * 72)
    rng = random.Random(2026)      # semilla fija para que la salida sea reproducible
    N = 1000

    print("\n[1] Casos de prueba obligatorios del taller")
    print("  X|0> = |1>")
    q = cero(rng).x()
    reporte(q, "X|0>", N)
    print(f"  Es exactamente |1>: {q == uno()}")

    print("\n  H|0> -> aproximadamente 50% y 50%")
    q = cero(rng).h()
    r = reporte(q, "H|0>", N)
    print(f"  Probabilidades cerca de 0.5: "
          f"{abs(r['p0'] - 0.5) < 1e-9 and abs(r['p1'] - 0.5) < 1e-9}")
    print(f"  Frecuencias observadas dentro de +-5%: "
          f"{abs(r['conteo'][0] / N - 0.5) < 0.05}")

    print("\n  HH|0> = |0> (salvo error numerico)")
    q = cero(rng).h().h()
    reporte(q, "HH|0>", N)
    print(f"  Vuelve a |0>: {q == cero()}   (H es su propia inversa: H*H = I)")

    print("\n[2] Otras combinaciones de compuertas")
    circuitos = ["X", "Z", "H", "XZ", "HZ", "HZH", "XX", "ZZ", "HXH"]
    for c in circuitos:
        q = cero(rng).aplicar_circuito(c)
        p0, p1 = q.probabilidades()
        print(f"  {c + '|0>':10s} = {str(q):44s} P(0)={p0:.3f} P(1)={p1:.3f}")
    print("  Observaciones: Z|0> = |0> (Z solo cambia el signo de la amplitud de |1>),")
    print("  HZH|0> = |1> (Z en la base de Hadamard actua como X) y XX = ZZ = I.")

    print("\n[3] La fase relativa no se ve al medir, pero si al interferir")
    q_hz = cero(rng).h().z()          # H y luego Z
    print(f"  H|0> luego Z: {q_hz}  P = {q_hz.probabilidades()}")
    print("  Las probabilidades son iguales a las de H|0>: la fase relativa no se")
    print("  ve en una medida directa. Aplicando otra H si aparece la diferencia:")
    print(f"    HH|0>  -> {cero(rng).aplicar_circuito('HH').probabilidades()}")
    print(f"    HZH|0> -> {cero(rng).aplicar_circuito('HZH').probabilidades()}")

    print("\n[4] Estado sesgado y comprobacion estadistica")
    #  |psi> = sqrt(0.25)|0> + sqrt(0.75)|1>  ->  P(0) = 0.25, P(1) = 0.75
    q = Qubit(sqrt(0.25), sqrt(0.75), rng=rng)
    r = reporte(q, "0.5|0>+0.866|1>", N)
    print(f"  Frecuencia de 0 cerca de 0.25: {abs(r['conteo'][0] / N - 0.25) < 0.05}")
    #  Estado con amplitud compleja: la fase no cambia las probabilidades.
    q = Qubit(INV_R2, INV_R2 * 1j, rng=rng)
    reporte(q, "(|0>+i|1>)/r2", N)

    print("\n[5] Normalizacion automatica y validaciones")
    q = Qubit(3, 4, rng=rng)          # se normaliza a (0.6, 0.8)
    print(f"  Qubit(3,4) normalizado -> {q}  P = "
          f"({q.probabilidades()[0]:.2f}, {q.probabilidades()[1]:.2f}) (esperado 0.36, 0.64)")
    for descripcion, accion in [("vector cero", lambda: Qubit(0, 0)),
                                ("compuerta inexistente", lambda: cero().aplicar_circuito("Q"))]:
        try:
            accion()
            print(f"  {descripcion}: NO se detecto (mal)")
        except ValueError as err:
            print(f"  {descripcion}: rechazado -> {err}")

    print("\n[6] El colapso: medir dos veces seguidas da el mismo resultado")
    q = cero(rng).h()
    primera = q.medir()
    segunda = q.medir()
    print(f"  Primera medida: {primera}, estado despues: {q}")
    print(f"  Segunda medida: {segunda}  (igual a la primera: {primera == segunda})")


if __name__ == "__main__":
    _demo()
