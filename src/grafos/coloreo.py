"""
Punto 6 - Coloreo de grafos: organizar examenes sin choques.

Modelo
------
Vertices = cursos. Arista u-v = hay estudiantes inscritos en los dos cursos,
entonces sus examenes NO pueden ir en la misma franja. Colorear el grafo con
k colores = repartir los examenes en k franjas sin choques.

Idea matematica
---------------
Algoritmo voraz: se recorren los vertices en algun orden y a cada uno se le da
el color de menor indice que no usen sus vecinos ya coloreados. Eso siempre da
una coloracion VALIDA por construccion (nunca se elige un color prohibido) y
usa a lo sumo  max_grado + 1  colores, porque un vertice de grado d tiene como
maximo d colores bloqueados y hay d+1 colores disponibles.

No es optimo: el resultado depende del orden. El numero cromatico chi(G) es el
minimo real y calcularlo es NP-dificil; el voraz solo da una cota superior.
Aqui se usa el orden de Welsh-Powell (grado decreciente), que en la practica
da buenos resultados, y se compara con el orden alfabetico y con ordenes
aleatorios para mostrar que el numero de colores cambia.

Ejecucion:
    python3 src/grafos/coloreo.py
"""

import random


# Grafo de conflictos de prueba: 12 cursos, 24 conflictos.
CONFLICTOS = [
    ("Calculo", "Algebra"), ("Calculo", "Fisica"), ("Calculo", "Programacion"),
    ("Algebra", "Discretas"), ("Algebra", "Programacion"), ("Fisica", "Quimica"),
    ("Fisica", "Discretas"), ("Programacion", "Discretas"), ("Programacion", "Redes"),
    ("Discretas", "Logica"), ("Discretas", "Estadistica"), ("Logica", "Filosofia"),
    ("Logica", "Redes"), ("Redes", "SistemasOp"), ("SistemasOp", "Programacion"),
    ("SistemasOp", "BasesDatos"), ("BasesDatos", "Programacion"),
    ("BasesDatos", "Estadistica"), ("Estadistica", "Calculo"),
    ("Quimica", "Estadistica"), ("Filosofia", "Historia"), ("Historia", "Logica"),
    ("Historia", "Filosofia"), ("Quimica", "Algebra"),
]


def construir_grafo(aristas: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Lista de adyacencia (no dirigida, sin pesos) a partir de las aristas."""
    g: dict[str, set[str]] = {}
    for u, v in aristas:
        if u == v:
            raise ValueError(f"un curso no puede chocar consigo mismo: {u}")
        g.setdefault(u, set()).add(v)
        g.setdefault(v, set()).add(u)
    return g


def orden_welsh_powell(grafo: dict[str, set[str]]) -> list[str]:
    """Vertices ordenados por grado decreciente (desempate alfabetico)."""
    return sorted(grafo, key=lambda v: (-len(grafo[v]), v))


def colorear_voraz(grafo: dict[str, set[str]], orden: list[str] | None = None) -> dict[str, int]:
    """Coloreo voraz. Devuelve {vertice: color}, con colores 0, 1, 2, ...

    Para cada vertice se mira que colores ya tienen sus vecinos y se toma el
    menor color libre (mex del conjunto de colores prohibidos).
    """
    orden = orden if orden is not None else orden_welsh_powell(grafo)
    if set(orden) != set(grafo):
        raise ValueError("el orden debe contener exactamente los vertices del grafo")

    color: dict[str, int] = {}
    for v in orden:
        prohibidos = {color[u] for u in grafo[v] if u in color}
        c = 0
        while c in prohibidos:      # menor color no prohibido
            c += 1
        color[v] = c
    return color


def es_coloreo_valido(grafo: dict[str, set[str]], color: dict[str, int]) -> bool:
    """True si ningun par de vertices adyacentes comparte color."""
    if set(color) != set(grafo):
        return False
    return all(color[u] != color[v] for u in grafo for v in grafo[u])


def conflictos_restantes(grafo: dict[str, set[str]], color: dict[str, int]) -> list[tuple[str, str]]:
    """Aristas cuyos extremos quedaron del mismo color (deberia salir vacia)."""
    malas = {tuple(sorted((u, v))) for u in grafo for v in grafo[u] if color[u] == color[v]}
    return sorted(malas)


def grupos_por_color(color: dict[str, int]) -> dict[int, list[str]]:
    """Invierte el diccionario: color -> lista de vertices (las franjas horarias)."""
    grupos: dict[int, list[str]] = {}
    for v, c in sorted(color.items()):
        grupos.setdefault(c, []).append(v)
    return dict(sorted(grupos.items()))


def numero_de_colores(color: dict[str, int]) -> int:
    return len(set(color.values()))


def cota_superior_grado(grafo: dict[str, set[str]]) -> int:
    """max_grado + 1: cota que el voraz nunca supera."""
    return max((len(vec) for vec in grafo.values()), default=-1) + 1


def buscar_triangulo(grafo: dict[str, set[str]]) -> list[str]:
    """Busca (por fuerza bruta pequena) un triangulo: da una cota INFERIOR de chi.

    Si k vertices son todos adyacentes entre si, necesitan k colores distintos,
    asi que chi(G) >= k.
    """
    vs = sorted(grafo)
    for i, a in enumerate(vs):
        for b in vs[i + 1:]:
            if b not in grafo[a]:
                continue
            for c in vs[vs.index(b) + 1:]:
                if c in grafo[a] and c in grafo[b]:
                    return [a, b, c]
    return []


# ---------------------------------------------------------------- demostracion
def _demo() -> None:
    print("=" * 72)
    print("PUNTO 6 - COLOREO DE GRAFOS: FRANJAS DE EXAMEN SIN CHOQUES")
    print("=" * 72)

    g = construir_grafo(CONFLICTOS)
    print(f"\nGrafo de conflictos: {len(g)} cursos, {len(CONFLICTOS)} conflictos")
    print("  Grados:")
    for v in orden_welsh_powell(g):
        print(f"    {v:14s} grado {len(g[v])}  choca con: {', '.join(sorted(g[v]))}")

    print("\n[1] Coloreo voraz con orden Welsh-Powell (grado decreciente)")
    color = colorear_voraz(g)
    print(f"  Colores usados: {numero_de_colores(color)} "
          f"(cota del voraz: max_grado + 1 = {cota_superior_grado(g)})")
    for c, cursos in grupos_por_color(color).items():
        print(f"    Franja {c + 1}: {', '.join(cursos)}")
    print(f"  Coloreo valido (ningun par adyacente comparte franja): "
          f"{es_coloreo_valido(g, color)}")
    print(f"  Conflictos que quedaron sin resolver: {conflictos_restantes(g, color)}")
    tri = buscar_triangulo(g)
    if tri:
        print(f"  Cota inferior: {tri} forman un triangulo -> se necesitan >= 3 franjas")

    print("\n[2] El resultado depende del orden (por eso el voraz no es optimo)")
    pruebas = [("alfabetico", sorted(g)), ("inverso", sorted(g, reverse=True))]
    rng = random.Random(2026)
    for i in range(3):
        aleatorio = sorted(g)
        rng.shuffle(aleatorio)
        pruebas.append((f"aleatorio {i + 1}", aleatorio))
    for nombre, orden in pruebas:
        c = colorear_voraz(g, orden)
        print(f"  orden {nombre:12s} -> {numero_de_colores(c)} colores, "
              f"valido: {es_coloreo_valido(g, c)}")

    print("\n[3] Casos de control con respuesta conocida")
    #  Grafo completo K4: necesita exactamente 4 colores.
    k4 = construir_grafo([("A", "B"), ("A", "C"), ("A", "D"),
                          ("B", "C"), ("B", "D"), ("C", "D")])
    c_k4 = colorear_voraz(k4)
    print(f"  K4 (completo de 4)  -> {numero_de_colores(c_k4)} colores (esperado 4), "
          f"valido: {es_coloreo_valido(k4, c_k4)}")
    #  Ciclo par C6: es bipartito, 2 colores bastan.
    c6_aristas = [("v1", "v2"), ("v2", "v3"), ("v3", "v4"),
                  ("v4", "v5"), ("v5", "v6"), ("v6", "v1")]
    c6 = construir_grafo(c6_aristas)
    c_c6 = colorear_voraz(c6)
    print(f"  Ciclo C6 (par)      -> {numero_de_colores(c_c6)} colores (esperado 2), "
          f"valido: {es_coloreo_valido(c6, c_c6)}")
    #  Ciclo impar C5: no es bipartito, necesita 3.
    c5 = construir_grafo([("v1", "v2"), ("v2", "v3"), ("v3", "v4"),
                          ("v4", "v5"), ("v5", "v1")])
    c_c5 = colorear_voraz(c5)
    print(f"  Ciclo C5 (impar)    -> {numero_de_colores(c_c5)} colores (esperado 3), "
          f"valido: {es_coloreo_valido(c5, c_c5)}")

    print("\n[4] Ejemplo clasico donde un orden malo desperdicia colores")
    #  Grafo "corona" (bipartito: a_i unido a b_j solo si i != j).
    #  Con 2 colores basta (es bipartito), pero un orden alternado hace que el
    #  voraz use 3. Es el contraejemplo tipico de que el voraz no es optimo.
    corona = construir_grafo([("a1", "b2"), ("a1", "b3"), ("a2", "b1"),
                              ("a2", "b3"), ("a3", "b1"), ("a3", "b2")])
    bueno = colorear_voraz(corona, ["a1", "a2", "a3", "b1", "b2", "b3"])
    malo = colorear_voraz(corona, ["a1", "b1", "a2", "b2", "a3", "b3"])
    print(f"  orden por lados : {numero_de_colores(bueno)} colores -> {grupos_por_color(bueno)}")
    print(f"  orden alternado : {numero_de_colores(malo)} colores -> {grupos_por_color(malo)}")
    print("  Ambos son validos, pero uno usa mas franjas de las necesarias.")


if __name__ == "__main__":
    _demo()
