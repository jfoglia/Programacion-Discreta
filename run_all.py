#!/usr/bin/env python3
"""
Lanzador del taller: ejecuta la demostracion de los 10 puntos.

Uso:
    python3 run_all.py            # ejecuta los 10 puntos en orden
    python3 run_all.py 2 7 10     # ejecuta solo los puntos indicados
    python3 run_all.py --lista    # muestra la lista de puntos
"""

import sys

from src.boole import simplificacion, tablas_verdad
from src.cripto import cesar, mpc_promedio, rsa_juguete
from src.cuantica import qubit
from src.grafos import cierre, coloreo, dijkstra
from src.info import shannon

PUNTOS = {
    1: ("Cifrado Cesar", cesar),
    2: ("RSA de juguete", rsa_juguete),
    3: ("MPC: promedio sin revelar datos", mpc_promedio),
    4: ("Dijkstra: ruta mas corta", dijkstra),
    5: ("Cierre de una estacion", cierre),
    6: ("Coloreo de grafos", coloreo),
    7: ("Tablas de verdad", tablas_verdad),
    8: ("Simplificacion booleana", simplificacion),
    9: ("Entropia de Shannon", shannon),
    10: ("Simulador de un qubit", qubit),
}


def main(argv: list[str]) -> int:
    if "--lista" in argv or "-l" in argv:
        for numero, (nombre, _) in PUNTOS.items():
            print(f"  {numero:2d}. {nombre}")
        return 0

    if argv:
        try:
            elegidos = [int(a) for a in argv]
        except ValueError:
            print("Los argumentos deben ser numeros de punto (1..10). "
                  "Use --lista para verlos.")
            return 1
        desconocidos = [p for p in elegidos if p not in PUNTOS]
        if desconocidos:
            print(f"Puntos inexistentes: {desconocidos} (validos: 1..10)")
            return 1
    else:
        elegidos = list(PUNTOS)

    for numero in elegidos:
        nombre, modulo = PUNTOS[numero]
        print(f"\n\n{'#' * 72}\n#  PUNTO {numero}: {nombre}\n{'#' * 72}")
        modulo._demo()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
