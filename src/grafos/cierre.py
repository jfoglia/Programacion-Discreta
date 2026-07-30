"""
Punto 5 - Cierre de una estacion: medir el impacto en la red.

Idea
----
Se calculan las rutas mas cortas ANTES del cierre, se elimina el vertice
(o la arista) del grafo y se recalculan. La comparacion por pares
origen-destino muestra tres situaciones posibles:

  * IGUAL         : la ruta optima no usaba ese vertice/arista.
  * AUMENTA       : habia que pasar por ahi; ahora toca un desvio mas largo.
  * DESCONECTADO  : el cierre parte el grafo y ya no existe ningun camino.

Formalmente: quitar aristas nunca puede disminuir una distancia minima, porque
el conjunto de caminos posibles del grafo nuevo es un subconjunto del anterior
y el minimo de un subconjunto es mayor o igual. Por eso "diferencia" siempre
es >= 0 (o infinita si se desconecta).

Ejecucion:
    python3 src/grafos/cierre.py
"""

import math

try:
    from .dijkstra import formatear_ruta, ruta_mas_corta
    from .grafo import GrafoPonderado, grafo_ciudad
except ImportError:
    from dijkstra import formatear_ruta, ruta_mas_corta
    from grafo import GrafoPonderado, grafo_ciudad

INF = math.inf


def comparar_cierre(grafo: GrafoPonderado, pares: list[tuple[str, str]],
                    vertice_cerrado: str | None = None,
                    arista_cerrada: tuple[str, str] | None = None) -> list[dict]:
    """Compara las rutas de `pares` antes y despues de un cierre.

    Se indica exactamente uno de: vertice_cerrado o arista_cerrada.
    Devuelve una lista de filas con origen, destino, antes, despues,
    diferencia, estado y las dos rutas.
    """
    if (vertice_cerrado is None) == (arista_cerrada is None):
        raise ValueError("indique exactamente un cierre: un vertice O una arista")

    despues = grafo.copia()
    if vertice_cerrado is not None:
        despues.quitar_vertice(vertice_cerrado)
    else:
        despues.quitar_arista(*arista_cerrada)

    filas = []
    for origen, destino in pares:
        d_antes, r_antes = ruta_mas_corta(grafo, origen, destino)

        # Si el cierre elimina el propio origen o destino, el par deja de existir.
        if origen not in despues.ady or destino not in despues.ady:
            d_despues, r_despues, estado = INF, [], "ESTACION CERRADA"
        else:
            d_despues, r_despues = ruta_mas_corta(despues, origen, destino)
            if d_despues == INF:
                estado = "DESCONECTADO"
            elif d_despues > d_antes:
                estado = "AUMENTA"
            else:
                estado = "IGUAL"

        diferencia = INF if d_despues == INF else d_despues - d_antes
        filas.append({
            "origen": origen, "destino": destino,
            "antes": d_antes, "despues": d_despues,
            "diferencia": diferencia, "estado": estado,
            "ruta_antes": r_antes, "ruta_despues": r_despues,
        })
    return filas


def _fmt(x: float) -> str:
    return "inf" if x == INF else f"{x:g}"


def imprimir_tabla(filas: list[dict], titulo: str, mostrar_rutas: bool = True) -> None:
    """Tabla: origen | destino | antes | despues | diferencia | estado."""
    print(f"\n{titulo}")
    print(f"  {'origen':12s} {'destino':12s} {'antes':>7s} {'despues':>8s} "
          f"{'dif':>6s}  estado")
    print("  " + "-" * 62)
    for f in filas:
        print(f"  {f['origen']:12s} {f['destino']:12s} {_fmt(f['antes']):>7s} "
              f"{_fmt(f['despues']):>8s} {_fmt(f['diferencia']):>6s}  {f['estado']}")
    if mostrar_rutas:
        print("\n  Detalle de las rutas:")
        for f in filas:
            print(f"    {f['origen']} -> {f['destino']}")
            print(f"       antes  : {formatear_ruta(f['ruta_antes'])}")
            print(f"       despues: {formatear_ruta(f['ruta_despues'])}")


def resumen(filas: list[dict]) -> dict:
    """Cuenta cuantos pares empeoraron, cuantos se desconectaron, etc."""
    return {
        "iguales": sum(1 for f in filas if f["estado"] == "IGUAL"),
        "aumentaron": sum(1 for f in filas if f["estado"] == "AUMENTA"),
        "desconectados": sum(1 for f in filas
                             if f["estado"] in ("DESCONECTADO", "ESTACION CERRADA")),
    }


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 72)
    print("PUNTO 5 - IMPACTO DEL CIERRE DE UNA ESTACION")
    print("=" * 72)

    g = grafo_ciudad()
    pares = [("Portal", "Universidad"), ("Portal", "Hospital"), ("Calle26", "Parque"),
             ("Museo", "Estadio"), ("Vereda", "Museo"), ("Portal", "Estadio")]

    print("\n[Escenario 1] Se cierra la estacion Centro (es un nodo de paso central)")
    filas = comparar_cierre(g, pares, vertice_cerrado="Centro")
    imprimir_tabla(filas, "Tabla comparativa (cierre de Centro):")
    print(f"  Resumen: {resumen(filas)}")

    print("\n[Escenario 2] Se cierra la estacion Terminal (Vereda solo cuelga de ahi)")
    filas2 = comparar_cierre(g, pares, vertice_cerrado="Terminal")
    imprimir_tabla(filas2, "Tabla comparativa (cierre de Terminal):", mostrar_rutas=False)
    print(f"  Resumen: {resumen(filas2)}")
    print("  Los pares que salen o llegan a Vereda quedan sin camino: Vereda era")
    print("  una hoja del grafo colgada de Terminal, asi que se aisla por completo.")

    print("\n[Escenario 3] Se cierra solo el tramo Museo -- Centro (una arista)")
    filas3 = comparar_cierre(g, pares, arista_cerrada=("Museo", "Centro"))
    imprimir_tabla(filas3, "Tabla comparativa (cierre del tramo Museo--Centro):",
                   mostrar_rutas=False)
    print(f"  Resumen: {resumen(filas3)}")

    print("\n[Escenario 4] Se cierra Parque, que casi no se usa en las rutas optimas")
    filas4 = comparar_cierre(g, pares, vertice_cerrado="Parque")
    imprimir_tabla(filas4, "Tabla comparativa (cierre de Parque):", mostrar_rutas=False)
    print(f"  Resumen: {resumen(filas4)}")
    print("  Poco impacto: ninguna ruta optima entre los otros pares pasaba por Parque,")
    print("  asi que solo desaparece el par que tenia a Parque como destino.")

    print("\n[Verificacion] Ninguna distancia puede bajar tras un cierre:")
    todas = filas + filas2 + filas3 + filas4
    print(f"  diferencias >= 0 en los {len(todas)} pares evaluados: "
          f"{all(f['diferencia'] >= 0 for f in todas)}")


if __name__ == "__main__":
    _demo()
