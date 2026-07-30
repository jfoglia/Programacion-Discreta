"""Pruebas del bloque B: Dijkstra (punto 4), cierre (punto 5), coloreo (punto 6).

Ejecucion:  python3 -m unittest discover -s tests -v
"""

import math
import random
import unittest

from src.grafos import cierre, coloreo
from src.grafos.dijkstra import dijkstra, reconstruir_ruta, ruta_mas_corta
from src.grafos.grafo import GrafoPonderado, grafo_ciudad


class TestGrafoCiudad(unittest.TestCase):
    """El grafo de prueba cumple lo que pide el taller."""

    def setUp(self):
        self.g = grafo_ciudad()

    def test_tamano_minimo_exigido(self):
        self.assertGreaterEqual(len(self.g.vertices), 8)     # minimo 8 vertices
        self.assertGreaterEqual(len(self.g.aristas()), 12)   # minimo 12 aristas

    def test_carga_desde_archivo_y_simetria(self):
        for u, v, peso in self.g.aristas():
            with self.subTest(arista=(u, v)):
                self.assertEqual(self.g.vecinos(u)[v], peso)
                self.assertEqual(self.g.vecinos(v)[u], peso)  # no dirigido

    def test_no_acepta_pesos_negativos(self):
        with self.assertRaises(ValueError):
            GrafoPonderado.desde_lista([("A", "B", -1)])


class TestDijkstra(unittest.TestCase):
    """Punto 4."""

    def setUp(self):
        self.g = grafo_ciudad()

    def test_caso_verificable_a_mano(self):
        #  A-B=1, B-C=1, A-C=5: el camino por B (2) gana al directo (5).
        g = GrafoPonderado.desde_lista([("A", "B", 1), ("B", "C", 1), ("A", "C", 5)])
        dist, ruta = ruta_mas_corta(g, "A", "C")
        self.assertEqual(dist, 2)
        self.assertEqual(ruta, ["A", "B", "C"])

    def test_distancias_conocidas_de_la_ciudad(self):
        esperado = {
            ("Portal", "Calle26"): 4,
            ("Portal", "Museo"): 7,
            ("Portal", "Centro"): 9,
            ("Portal", "Estadio"): 12,
            ("Museo", "Hospital"): 6,
            ("Portal", "Vereda"): 16,
        }
        for (o, d), valor in esperado.items():
            with self.subTest(par=(o, d)):
                self.assertEqual(ruta_mas_corta(self.g, o, d)[0], valor)

    def test_distancia_a_si_mismo_es_cero(self):
        for v in self.g.vertices:
            with self.subTest(v=v):
                self.assertEqual(ruta_mas_corta(self.g, v, v), (0, [v]))

    def test_la_ruta_devuelta_suma_la_distancia(self):
        """Coherencia: la ruta reportada debe pesar exactamente la distancia."""
        for origen in self.g.vertices:
            dist, padre = dijkstra(self.g, origen)
            for destino in self.g.vertices:
                ruta = reconstruir_ruta(padre, origen, destino)
                with self.subTest(par=(origen, destino)):
                    self.assertTrue(ruta)                    # el grafo es conexo
                    peso = sum(self.g.vecinos(a)[b] for a, b in zip(ruta, ruta[1:]))
                    self.assertAlmostEqual(peso, dist[destino])

    def test_simetria_en_grafo_no_dirigido(self):
        for o in self.g.vertices:
            for d in self.g.vertices:
                with self.subTest(par=(o, d)):
                    self.assertEqual(ruta_mas_corta(self.g, o, d)[0],
                                     ruta_mas_corta(self.g, d, o)[0])

    def test_desigualdad_triangular(self):
        vs = self.g.vertices
        for a in vs:
            for b in vs:
                for c in vs:
                    d_ab = ruta_mas_corta(self.g, a, b)[0]
                    d_bc = ruta_mas_corta(self.g, b, c)[0]
                    d_ac = ruta_mas_corta(self.g, a, c)[0]
                    self.assertLessEqual(d_ac, d_ab + d_bc + 1e-9)

    def test_sin_camino_devuelve_infinito(self):
        g = GrafoPonderado.desde_lista([("A", "B", 2), ("X", "Y", 3)])
        dist, ruta = ruta_mas_corta(g, "A", "Y")
        self.assertEqual(dist, math.inf)
        self.assertEqual(ruta, [])

    def test_coincide_con_fuerza_bruta_en_grafos_aleatorios(self):
        """Compara Dijkstra con Bellman-Ford (otro algoritmo) en grafos al azar."""
        rng = random.Random(11)
        for intento in range(15):
            n = rng.randint(4, 9)
            nombres = [f"v{i}" for i in range(n)]
            aristas = []
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.5:
                        aristas.append((nombres[i], nombres[j], rng.randint(1, 20)))
            if not aristas:
                continue
            g = GrafoPonderado.desde_lista(aristas)
            origen = g.vertices[0]
            dist_dijkstra, _ = dijkstra(g, origen)

            # Bellman-Ford: relaja todas las aristas |V|-1 veces.
            dist_bf = {v: math.inf for v in g.ady}
            dist_bf[origen] = 0
            for _ in range(len(g.ady) - 1):
                for u, v, w in g.aristas():
                    dist_bf[v] = min(dist_bf[v], dist_bf[u] + w)
                    dist_bf[u] = min(dist_bf[u], dist_bf[v] + w)
            with self.subTest(intento=intento):
                self.assertEqual(dist_dijkstra, dist_bf)

    def test_origen_o_destino_inexistente(self):
        with self.assertRaises(KeyError):
            ruta_mas_corta(self.g, "NoExiste", "Portal")
        with self.assertRaises(KeyError):
            ruta_mas_corta(self.g, "Portal", "NoExiste")


class TestCierre(unittest.TestCase):
    """Punto 5."""

    def setUp(self):
        self.g = grafo_ciudad()
        self.pares = [("Portal", "Universidad"), ("Portal", "Hospital"),
                      ("Calle26", "Parque"), ("Museo", "Estadio"),
                      ("Vereda", "Museo"), ("Portal", "Estadio")]

    def test_se_prueban_al_menos_cinco_pares(self):
        filas = cierre.comparar_cierre(self.g, self.pares, vertice_cerrado="Centro")
        self.assertGreaterEqual(len(filas), 5)
        for f in filas:
            self.assertIn(f["estado"], ("IGUAL", "AUMENTA", "DESCONECTADO",
                                        "ESTACION CERRADA"))

    def test_una_distancia_nunca_disminuye_tras_un_cierre(self):
        """Quitar aristas solo puede empeorar (o dejar igual) las distancias."""
        for v in self.g.vertices:
            filas = cierre.comparar_cierre(self.g, self.pares, vertice_cerrado=v)
            for f in filas:
                with self.subTest(cerrado=v, par=(f["origen"], f["destino"])):
                    self.assertGreaterEqual(f["diferencia"], 0)

    def test_detecta_desconexion(self):
        """Vereda solo se conecta por Terminal: al cerrar Terminal se aisla."""
        filas = cierre.comparar_cierre(self.g, [("Vereda", "Museo")],
                                       vertice_cerrado="Terminal")
        fila = filas[0]
        self.assertEqual(fila["estado"], "DESCONECTADO")
        self.assertEqual(fila["despues"], math.inf)
        self.assertEqual(fila["ruta_despues"], [])

    def test_detecta_aumento_de_distancia(self):
        filas = cierre.comparar_cierre(self.g, [("Portal", "Hospital")],
                                       vertice_cerrado="Centro")
        fila = filas[0]
        self.assertEqual(fila["estado"], "AUMENTA")
        self.assertEqual(fila["antes"], 13)
        self.assertEqual(fila["despues"], 14)
        self.assertEqual(fila["diferencia"], 1)
        self.assertNotIn("Centro", fila["ruta_despues"])

    def test_cierre_de_arista(self):
        filas = cierre.comparar_cierre(self.g, [("Museo", "Estadio")],
                                       arista_cerrada=("Museo", "Centro"))
        self.assertEqual(filas[0]["estado"], "AUMENTA")
        # El grafo original no debe modificarse (se trabaja sobre una copia).
        self.assertIn("Centro", self.g.vecinos("Museo"))

    def test_cierre_que_no_afecta_nada(self):
        filas = cierre.comparar_cierre(self.g, [("Portal", "Calle26")],
                                       vertice_cerrado="Vereda")
        self.assertEqual(filas[0]["estado"], "IGUAL")
        self.assertEqual(filas[0]["diferencia"], 0)

    def test_hay_que_indicar_exactamente_un_cierre(self):
        with self.assertRaises(ValueError):
            cierre.comparar_cierre(self.g, self.pares)
        with self.assertRaises(ValueError):
            cierre.comparar_cierre(self.g, self.pares, vertice_cerrado="Centro",
                                   arista_cerrada=("Museo", "Centro"))


class TestColoreo(unittest.TestCase):
    """Punto 6."""

    def setUp(self):
        self.g = coloreo.construir_grafo(coloreo.CONFLICTOS)

    def test_grafo_con_al_menos_diez_vertices(self):
        self.assertGreaterEqual(len(self.g), 10)

    def test_el_coloreo_es_valido(self):
        color = coloreo.colorear_voraz(self.g)
        self.assertTrue(coloreo.es_coloreo_valido(self.g, color))
        self.assertEqual(coloreo.conflictos_restantes(self.g, color), [])

    def test_todos_los_vertices_reciben_color(self):
        color = coloreo.colorear_voraz(self.g)
        self.assertEqual(set(color), set(self.g))
        vertices_en_grupos = [v for grupo in coloreo.grupos_por_color(color).values()
                              for v in grupo]
        self.assertCountEqual(vertices_en_grupos, list(self.g))

    def test_no_supera_la_cota_max_grado_mas_uno(self):
        for orden in [None, sorted(self.g), sorted(self.g, reverse=True)]:
            color = coloreo.colorear_voraz(self.g, orden)
            with self.subTest(orden=orden and orden[:2]):
                self.assertLessEqual(coloreo.numero_de_colores(color),
                                     coloreo.cota_superior_grado(self.g))

    def test_valido_para_cualquier_orden_aleatorio(self):
        rng = random.Random(5)
        for intento in range(50):
            orden = sorted(self.g)
            rng.shuffle(orden)
            color = coloreo.colorear_voraz(self.g, orden)
            with self.subTest(intento=intento):
                self.assertTrue(coloreo.es_coloreo_valido(self.g, color))

    def test_grafos_con_numero_cromatico_conocido(self):
        k4 = coloreo.construir_grafo([("A", "B"), ("A", "C"), ("A", "D"),
                                      ("B", "C"), ("B", "D"), ("C", "D")])
        self.assertEqual(coloreo.numero_de_colores(coloreo.colorear_voraz(k4)), 4)

        c6 = coloreo.construir_grafo([("v1", "v2"), ("v2", "v3"), ("v3", "v4"),
                                      ("v4", "v5"), ("v5", "v6"), ("v6", "v1")])
        self.assertEqual(coloreo.numero_de_colores(coloreo.colorear_voraz(c6)), 2)

        c5 = coloreo.construir_grafo([("v1", "v2"), ("v2", "v3"), ("v3", "v4"),
                                      ("v4", "v5"), ("v5", "v1")])
        self.assertEqual(coloreo.numero_de_colores(coloreo.colorear_voraz(c5)), 3)

    def test_el_voraz_no_siempre_es_optimo(self):
        """Grafo corona: es bipartito (2 colores) pero un orden malo usa 3."""
        corona = coloreo.construir_grafo([("a1", "b2"), ("a1", "b3"), ("a2", "b1"),
                                          ("a2", "b3"), ("a3", "b1"), ("a3", "b2")])
        bueno = coloreo.colorear_voraz(corona, ["a1", "a2", "a3", "b1", "b2", "b3"])
        malo = coloreo.colorear_voraz(corona, ["a1", "b1", "a2", "b2", "a3", "b3"])
        self.assertEqual(coloreo.numero_de_colores(bueno), 2)
        self.assertEqual(coloreo.numero_de_colores(malo), 3)
        # Los dos son validos: el voraz nunca produce una asignacion invalida.
        self.assertTrue(coloreo.es_coloreo_valido(corona, bueno))
        self.assertTrue(coloreo.es_coloreo_valido(corona, malo))

    def test_orden_invalido_y_lazo(self):
        with self.assertRaises(ValueError):
            coloreo.colorear_voraz(self.g, ["Calculo"])
        with self.assertRaises(ValueError):
            coloreo.construir_grafo([("A", "A")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
