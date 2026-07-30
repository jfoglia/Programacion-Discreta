"""
Punto 3 - MPC basico: calcular un promedio sin mostrar los datos.

Simulacion (no protocolo industrial) de suma secreta con 3 servidores.

Idea matematica
---------------
Cada nota x se parte en 3 partes aleatorias modulo M:
    s1, s2 uniformes en Z_M   y   s3 = (x - s1 - s2) mod M
de modo que  x = s1 + s2 + s3 (mod M).

Una parte sola no dice nada de x: si s1 es uniforme en Z_M e independiente
de x, entonces para cualquier valor observado de s1 todos los x siguen siendo
igual de probables (es el mismo argumento del "one time pad" pero en Z_M).
Lo mismo pasa con dos partes: solo la suma de las TRES revela x.

Cada servidor i recibe la parte s_i de todas las notas y publica un solo
numero: T_i = suma de sus partes (mod M). Como la suma es asociativa y
conmutativa, sumar por columnas o por filas da lo mismo:
    (T_1 + T_2 + T_3) mod M = suma de todas las notas (mod M).
Si esa suma real es menor que M, el resultado modular ES la suma real.

Ejecucion:
    python3 src/cripto/mpc_promedio.py
"""

import random

MODULO = 1_000_003        # primo comodo: mucho mas grande que cualquier suma de notas
NUM_SERVIDORES = 3


def repartir(valor: int, modulo: int = MODULO, partes: int = NUM_SERVIDORES,
             rng: random.Random | None = None) -> list[int]:
    """Parte un valor en `partes` sumandos aleatorios modulo `modulo`.

    Las primeras partes-1 son uniformes; la ultima se ajusta para que la
    suma cuadre. Asi cualquier subconjunto propio de partes es aleatorio puro.
    """
    rng = rng or random.SystemRandom()
    aleatorias = [rng.randrange(modulo) for _ in range(partes - 1)]
    ultima = (valor - sum(aleatorias)) % modulo
    return aleatorias + [ultima]


class Servidor:
    """Servidor que solo acumula partes. Nunca ve una nota completa."""

    def __init__(self, nombre: str, modulo: int = MODULO):
        self.nombre = nombre
        self.modulo = modulo
        self.acumulado = 0          # suma de las partes recibidas (mod modulo)
        self.partes_vistas: list[int] = []   # solo para poder mostrar la privacidad

    def recibir(self, parte: int) -> None:
        self.partes_vistas.append(parte)
        self.acumulado = (self.acumulado + parte) % self.modulo

    def publicar_total(self) -> int:
        """Lo unico que el servidor entrega al final: su total parcial."""
        return self.acumulado


def protocolo_suma_secreta(notas: list[int], modulo: int = MODULO,
                           rng: random.Random | None = None
                           ) -> tuple[int, float, list[Servidor]]:
    """Ejecuta el protocolo y devuelve (suma, promedio, servidores).

    Valida que las notas sean enteros entre 0 y 50 (rango pedido en el taller).
    """
    if not notas:
        raise ValueError("la lista de notas no puede estar vacia")
    for nota in notas:
        if not isinstance(nota, int) or not 0 <= nota <= 50:
            raise ValueError(f"nota invalida: {nota!r} (debe ser entero entre 0 y 50)")
    if len(notas) * 50 >= modulo:
        raise ValueError("el modulo es demasiado pequeno para esta cantidad de notas")

    servidores = [Servidor(f"S{i + 1}", modulo) for i in range(NUM_SERVIDORES)]

    # Reparto: cada estudiante manda una parte distinta a cada servidor.
    for nota in notas:
        for servidor, parte in zip(servidores, repartir(nota, modulo, rng=rng)):
            servidor.recibir(parte)

    # Reconstruccion: se suman los totales publicados. Nadie revelo notas.
    total = sum(s.publicar_total() for s in servidores) % modulo
    promedio = total / len(notas)
    return total, promedio, servidores


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 66)
    print("PUNTO 3 - MPC BASICO: PROMEDIO SIN REVELAR NOTAS")
    print("=" * 66)

    print("\n[1] Ejemplo minimo del taller: notas [40, 35, 50, 25]")
    notas = [40, 35, 50, 25]
    suma, promedio, servidores = protocolo_suma_secreta(notas)
    print(f"  Salida publica del protocolo -> suma = {suma}, promedio = {promedio}")
    print(f"  Esperado: suma = 150, promedio = 37.5  -> correcto: "
          f"{suma == 150 and promedio == 37.5}")
    print("  Totales que publico cada servidor (solo estos numeros salen):")
    for s in servidores:
        print(f"    {s.nombre}: {s.publicar_total()}")
    print(f"  ({servidores[0].publicar_total()} + {servidores[1].publicar_total()}"
          f" + {servidores[2].publicar_total()}) mod {MODULO} = {suma}")

    print("\n[2] Ninguna parte por separado revela una nota")
    rng = random.Random(7)  # semilla fija solo para que el ejemplo sea reproducible
    partes = repartir(40, rng=rng)
    print(f"  La nota 40 se partio en: {partes}")
    print(f"  Cada parte suelta parece un numero al azar en 0..{MODULO - 1}.")
    print(f"  Solo la suma de las tres da la nota: {sum(partes) % MODULO}")
    print("  Lo que ve cada servidor de TODAS las notas (nada parecido a las notas):")
    for s in servidores:
        print(f"    {s.nombre} vio {s.partes_vistas}")

    print("\n[3] Funciona con listas de cualquier tamano")
    for lista in ([50], [0, 0, 0], list(range(0, 51, 5)), [random.randint(0, 50) for _ in range(1000)]):
        suma, promedio, _ = protocolo_suma_secreta(lista)
        etiqueta = str(lista) if len(lista) <= 11 else f"<{len(lista)} notas aleatorias>"
        print(f"  {etiqueta:38s} suma={suma:6d} promedio={promedio:7.3f} "
              f"correcto: {suma == sum(lista)}")

    print("\n[4] Validaciones")
    for caso, lista in [("nota fuera de rango", [10, 51]), ("lista vacia", [])]:
        try:
            protocolo_suma_secreta(lista)
            print(f"  {caso}: NO se detecto (mal)")
        except ValueError as err:
            print(f"  {caso}: detectado -> {err}")


if __name__ == "__main__":
    _demo()
