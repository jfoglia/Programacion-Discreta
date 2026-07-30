"""
Punto 4 - Ruta mas corta: una ciudad como grafo (algoritmo de Dijkstra).

Idea matematica
---------------
Se mantiene una estimacion dist[v] de la distancia desde el origen y un
conjunto de vertices ya "cerrados" (con distancia definitiva).
Invariante: cuando se extrae el vertice u con la MENOR estimacion pendiente,
esa estimacion ya es optima. Razon: cualquier otro camino hacia u tendria que
salir del conjunto cerrado por algun vertice pendiente w con dist[w] >= dist[u]
y luego sumar pesos >= 0, asi que no puede mejorar dist[u].
Ese "sumar pesos >= 0" es justo donde se necesita que no haya pesos negativos.

Relajacion: si dist[u] + peso(u,v) < dist[v], se mejora dist[v] y se anota que
la mejor forma conocida de llegar a v es pasando por u (padre[v] = u). Con esos
padres se reconstruye la ruta al final.

La cola de prioridad (heapq) es solo la estructura de datos que da el minimo;
la logica del algoritmo (relajacion, cierre, reconstruccion) esta escrita aqui.

Ejecucion:
    python3 src/grafos/dijkstra.py
"""

import heapq
import math

try:  # permite importar el modulo como paquete o ejecutarlo directo
    from .grafo import GrafoPonderado, grafo_ciudad
except ImportError:
    from grafo import GrafoPonderado, grafo_ciudad

INF = math.inf


def dijkstra(grafo: GrafoPonderado, origen: str) -> tuple[dict[str, float], dict[str, str | None]]:
    """Distancias minimas desde `origen` a todos los vertices alcanzables.

    Devuelve (dist, padre). dist[v] = inf si v no es alcanzable.
    """
    if origen not in grafo.ady:
        raise KeyError(f"el origen {origen} no esta en el grafo")

    dist: dict[str, float] = {v: INF for v in grafo.ady}
    padre: dict[str, str | None] = {v: None for v in grafo.ady}
    cerrado: set[str] = set()

    dist[origen] = 0
    monticulo = [(0.0, origen)]        # (distancia estimada, vertice)

    while monticulo:
        d_u, u = heapq.heappop(monticulo)
        if u in cerrado:               # copia obsoleta del vertice: se ignora
            continue
        cerrado.add(u)                 # aqui dist[u] ya es definitiva

        for v, peso in grafo.vecinos(u).items():
            if v in cerrado:
                continue
            if d_u + peso < dist[v]:   # relajacion de la arista (u, v)
                dist[v] = d_u + peso
                padre[v] = u
                heapq.heappush(monticulo, (dist[v], v))

    return dist, padre


def reconstruir_ruta(padre: dict[str, str | None], origen: str, destino: str) -> list[str]:
    """Camino origen -> destino siguiendo los padres al reves. [] si no hay camino."""
    if destino != origen and padre.get(destino) is None:
        return []
    ruta = [destino]
    while ruta[-1] != origen:
        anterior = padre[ruta[-1]]
        if anterior is None:
            return []
        ruta.append(anterior)
    ruta.reverse()
    return ruta


def ruta_mas_corta(grafo: GrafoPonderado, origen: str, destino: str) -> tuple[float, list[str]]:
    """Devuelve (distancia_total, ruta). Distancia inf y ruta [] si no hay camino."""
    if destino not in grafo.ady:
        raise KeyError(f"el destino {destino} no esta en el grafo")
    dist, padre = dijkstra(grafo, origen)
    if dist[destino] == INF:
        return INF, []
    return dist[destino], reconstruir_ruta(padre, origen, destino)


def formatear_ruta(ruta: list[str]) -> str:
    return " -> ".join(ruta) if ruta else "(sin camino)"


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 72)
    print("PUNTO 4 - DIJKSTRA SOBRE LA RED DE TRANSPORTE")
    print("=" * 72)

    g = grafo_ciudad()
    print(f"\nGrafo cargado desde data/ciudad.txt: {g}")
    print(f"  Vertices ({len(g.vertices)}): {', '.join(g.vertices)}")
    print(f"  Aristas ({len(g.aristas())}):")
    for u, v, p in g.aristas():
        print(f"    {u:12s} -- {v:12s} {p:g} min")

    print("\n[1] Rutas mas cortas entre pares concretos")
    pares = [("Portal", "Estadio"), ("Portal", "Parque"), ("Vereda", "Universidad"),
             ("Museo", "Hospital"), ("Calle26", "Calle26")]
    for o, d in pares:
        dist, ruta = ruta_mas_corta(g, o, d)
        print(f"  {o:8s} -> {d:12s} distancia = {dist:5g}   ruta: {formatear_ruta(ruta)}")

    print("\n[2] Tabla de distancias desde Portal a todo el resto")
    dist, padre = dijkstra(g, "Portal")
    for v in g.vertices:
        ruta = reconstruir_ruta(padre, "Portal", v)
        print(f"  Portal -> {v:12s} {dist[v]:5g}   {formatear_ruta(ruta)}")

    print("\n[3] Grafo pequeno de control (se puede verificar a mano)")
    #  A -1- B -1- C   y   A -5- C : el camino por B (2) gana al directo (5)
    chico = GrafoPonderado.desde_lista([("A", "B", 1), ("B", "C", 1), ("A", "C", 5)])
    dist_chico, ruta_chico = ruta_mas_corta(chico, "A", "C")
    print(f"  A -> C: distancia = {dist_chico:g} (por B, no la arista directa de 5)")
    print(f"  ruta: {formatear_ruta(ruta_chico)}")

    print("\n[4] Casos limite")
    aislado = GrafoPonderado.desde_lista([("A", "B", 2), ("X", "Y", 3)])
    dist_inf, ruta_inf = ruta_mas_corta(aislado, "A", "Y")
    print(f"  Componentes separadas: A -> Y distancia = {dist_inf}, ruta = {formatear_ruta(ruta_inf)}")
    try:
        GrafoPonderado.desde_lista([("A", "B", -3)])
    except ValueError as err:
        print(f"  Peso negativo rechazado -> {err}")
    print(f"  Distancia de un vertice a si mismo: {ruta_mas_corta(g, 'Museo', 'Museo')[0]:g}")


if __name__ == "__main__":
    _demo()
