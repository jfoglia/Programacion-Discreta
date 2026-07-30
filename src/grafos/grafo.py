"""
Estructura de grafo ponderado usada por los puntos 4 y 5.

Se guarda como lista de adyacencia: un diccionario
    vertice -> { vecino: peso, ... }
que es la representacion mas comoda para Dijkstra (recorrer los vecinos de un
vertice es O(grado) y no O(numero de vertices) como en la matriz de adyacencia).
"""

from pathlib import Path


class GrafoPonderado:
    """Grafo con pesos, dirigido o no dirigido."""

    def __init__(self, dirigido: bool = False):
        self.dirigido = dirigido
        self.ady: dict[str, dict[str, float]] = {}

    # ------------------------------------------------------------ construccion
    def agregar_vertice(self, v: str) -> None:
        self.ady.setdefault(v, {})

    def agregar_arista(self, u: str, v: str, peso: float) -> None:
        """Agrega la arista u-v. Dijkstra exige pesos no negativos."""
        if peso < 0:
            raise ValueError(f"peso negativo no permitido: {u}-{v} = {peso}")
        self.agregar_vertice(u)
        self.agregar_vertice(v)
        self.ady[u][v] = peso
        if not self.dirigido:
            self.ady[v][u] = peso

    def quitar_vertice(self, v: str) -> None:
        """Elimina el vertice y todas sus aristas (simula cerrar una estacion)."""
        if v not in self.ady:
            raise KeyError(f"el vertice {v} no existe")
        del self.ady[v]
        for vecinos in self.ady.values():
            vecinos.pop(v, None)

    def quitar_arista(self, u: str, v: str) -> None:
        """Elimina la conexion u-v (simula cerrar un tramo)."""
        if v not in self.ady.get(u, {}):
            raise KeyError(f"la arista {u}-{v} no existe")
        del self.ady[u][v]
        if not self.dirigido:
            self.ady[v].pop(u, None)

    def copia(self) -> "GrafoPonderado":
        """Copia independiente, para no danar el grafo original al cerrar cosas."""
        nuevo = GrafoPonderado(self.dirigido)
        nuevo.ady = {u: dict(vecinos) for u, vecinos in self.ady.items()}
        return nuevo

    # ---------------------------------------------------------------- consultas
    @property
    def vertices(self) -> list[str]:
        return sorted(self.ady)

    def vecinos(self, v: str) -> dict[str, float]:
        return self.ady.get(v, {})

    def aristas(self) -> list[tuple[str, str, float]]:
        """Lista de aristas; en el caso no dirigido cada una aparece una sola vez."""
        vistas = []
        for u, vecinos in self.ady.items():
            for v, peso in vecinos.items():
                if self.dirigido or u <= v:
                    vistas.append((u, v, peso))
        return sorted(vistas)

    def __repr__(self) -> str:
        return (f"GrafoPonderado(dirigido={self.dirigido}, "
                f"|V|={len(self.ady)}, |E|={len(self.aristas())})")

    # ------------------------------------------------------------------ archivo
    @classmethod
    def desde_archivo(cls, ruta: str | Path, dirigido: bool = False) -> "GrafoPonderado":
        """Carga un grafo de un archivo de texto con lineas 'u v peso'."""
        g = cls(dirigido)
        with open(ruta, encoding="utf-8") as f:
            for numero, linea in enumerate(f, start=1):
                linea = linea.split("#")[0].strip()
                if not linea:
                    continue
                partes = linea.split()
                if len(partes) != 3:
                    raise ValueError(f"linea {numero} mal formada: {linea!r}")
                u, v, peso = partes
                g.agregar_arista(u, v, float(peso))
        return g

    @classmethod
    def desde_lista(cls, aristas, dirigido: bool = False) -> "GrafoPonderado":
        """Carga un grafo desde una lista de tuplas (u, v, peso)."""
        g = cls(dirigido)
        for u, v, peso in aristas:
            g.agregar_arista(u, v, peso)
        return g


# Ruta del grafo de prueba de la ciudad (10 vertices, 15 aristas).
RUTA_CIUDAD = Path(__file__).resolve().parents[2] / "data" / "ciudad.txt"


def grafo_ciudad() -> GrafoPonderado:
    """Grafo de prueba del taller: se lee del archivo data/ciudad.txt."""
    return GrafoPonderado.desde_archivo(RUTA_CIUDAD)
