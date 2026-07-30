"""Pruebas de los puntos 9 (entropia de Shannon) y 10 (simulador de un qubit).

Ejecucion:  python3 -m unittest discover -s tests -v
"""

import random
import unittest
from math import log2, sqrt

from src.cuantica.qubit import H, INV_R2, KET0, KET1, Qubit, X, Z, cero, uno
from src.info.shannon import (codificar, codigo_huffman, comparar, decodificar,
                              entropia, entropia_maxima, frecuencias,
                              longitud_promedio, probabilidades, redundancia)


class TestShannon(unittest.TestCase):
    """Punto 9."""

    def test_frecuencias_y_probabilidades(self):
        texto = "AABBBC"
        self.assertEqual(frecuencias(texto), {"A": 2, "B": 3, "C": 1})
        p = probabilidades(texto)
        self.assertAlmostEqual(sum(p.values()), 1.0)
        self.assertAlmostEqual(p["B"], 0.5)

    def test_valores_conocidos_de_entropia(self):
        casos = [("AAAA", 0.0), ("AB", 1.0), ("AABB", 1.0), ("ABCD", 2.0),
                 ("ABCDEFGH", 3.0), ("AAAB", 0.811278), ("AAAABBCD", 1.75)]
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertAlmostEqual(entropia(texto), esperado, places=5)

    def test_texto_vacio(self):
        self.assertEqual(entropia(""), 0.0)
        self.assertEqual(probabilidades(""), {})
        self.assertEqual(codigo_huffman(""), {})

    def test_entropia_cero_solo_si_hay_un_simbolo(self):
        self.assertEqual(entropia("ZZZZZZ"), 0.0)
        self.assertGreater(entropia("ZZZZZA"), 0.0)

    def test_entropia_maxima_con_simbolos_equiprobables(self):
        for k in range(1, 9):
            texto = "".join(chr(ord("a") + i) for i in range(k))
            with self.subTest(k=k):
                self.assertAlmostEqual(entropia(texto), log2(k))
                self.assertAlmostEqual(redundancia(texto), 0.0)

    def test_la_entropia_nunca_supera_log2_del_alfabeto(self):
        rng = random.Random(9)
        for intento in range(30):
            texto = "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 200)))
            with self.subTest(intento=intento):
                self.assertLessEqual(entropia(texto), entropia_maxima(texto) + 1e-12)

    def test_no_depende_de_la_longitud_sino_de_las_proporciones(self):
        self.assertAlmostEqual(entropia("AB"), entropia("AABB"))
        self.assertAlmostEqual(entropia("AB"), entropia("AB" * 100))
        self.assertAlmostEqual(entropia("AAAB"), entropia("AAABAAAB"))

    def test_texto_repetitivo_tiene_menos_entropia_que_uno_variado(self):
        repetitivo = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAB"
        variado = "La entropia mide incertidumbre, no longitud del texto."
        self.assertLess(entropia(repetitivo), entropia(variado))
        self.assertIn("MAYOR entropia", comparar(variado, repetitivo, "variado", "rep"))
        self.assertIn("MISMA entropia", comparar("AB", "AABB", "x", "y"))

    def test_huffman_es_libre_de_prefijos(self):
        texto = "abracadabra alcachofa"
        codigos = codigo_huffman(texto)
        for a in codigos.values():
            for b in codigos.values():
                if a != b:
                    self.assertFalse(b.startswith(a))

    def test_huffman_codifica_y_decodifica(self):
        rng = random.Random(4)
        textos = ["AAAABBCD", "abracadabra", "AAAAAAAAAB", "ABCDEFGH",
                  "".join(rng.choice("aabbbcdddde ") for _ in range(300))]
        for texto in textos:
            codigos = codigo_huffman(texto)
            with self.subTest(texto=texto[:20]):
                self.assertEqual(decodificar(codificar(texto, codigos), codigos), texto)

    def test_cota_de_shannon_H_menor_igual_L_menor_H_mas_1(self):
        rng = random.Random(6)
        textos = ["AAAABBCD", "abracadabra", "ABCDEFGH", "AAAAAAAAAB",
                  "".join(rng.choice("abcdefghij") for _ in range(500))]
        for texto in textos:
            codigos = codigo_huffman(texto)
            H = entropia(texto)
            L = longitud_promedio(texto, codigos)
            with self.subTest(texto=texto[:20]):
                self.assertLessEqual(H - 1e-9, L)      # ningun codigo baja de H
                self.assertLess(L, H + 1)              # Huffman no se pasa por 1 bit

    def test_huffman_iguala_la_entropia_con_potencias_de_un_medio(self):
        texto = "AAAABBCD"                              # p = 1/2, 1/4, 1/8, 1/8
        codigos = codigo_huffman(texto)
        self.assertAlmostEqual(longitud_promedio(texto, codigos), entropia(texto))

    def test_un_solo_simbolo_usa_un_bit(self):
        codigos = codigo_huffman("AAAA")
        self.assertEqual(codigos, {"A": "0"})
        self.assertEqual(decodificar("0000", codigos), "AAAA")

    def test_bits_incompletos_al_decodificar(self):
        codigos = codigo_huffman("AAAABBCD")
        with self.assertRaises(ValueError):
            decodificar(codificar("AAAABBCD", codigos) + "1", codigos)


class TestQubit(unittest.TestCase):
    """Punto 10."""

    def test_estado_inicial_es_ket0(self):
        q = cero()
        self.assertEqual(q.estado, KET0)
        self.assertEqual(q.probabilidades(), (1.0, 0.0))

    def test_caso_obligatorio_X_sobre_ket0(self):
        q = cero().x()
        self.assertEqual(q, uno())
        p0, p1 = q.probabilidades()
        self.assertAlmostEqual(p0, 0.0)
        self.assertAlmostEqual(p1, 1.0)

    def test_caso_obligatorio_H_sobre_ket0_da_mitad_y_mitad(self):
        p0, p1 = cero().h().probabilidades()
        self.assertAlmostEqual(p0, 0.5, places=12)
        self.assertAlmostEqual(p1, 0.5, places=12)

    def test_caso_obligatorio_HH_vuelve_a_ket0(self):
        self.assertEqual(cero().h().h(), cero())
        self.assertEqual(uno().h().h(), uno())

    def test_compuertas_son_su_propia_inversa(self):
        for nombre in ("X", "Z", "H"):
            for inicial in (cero(), uno()):
                with self.subTest(compuerta=nombre, inicial=inicial):
                    esperado = Qubit(*inicial.estado)
                    self.assertEqual(inicial.aplicar_circuito(nombre * 2), esperado)

    def test_Z_no_cambia_las_probabilidades(self):
        self.assertEqual(cero().z().probabilidades(), (1.0, 0.0))
        p = cero().h().z().probabilidades()
        self.assertAlmostEqual(p[0], 0.5, places=12)
        self.assertAlmostEqual(p[1], 0.5, places=12)

    def test_HZH_actua_como_X(self):
        q1 = cero().aplicar_circuito("HZH")
        p0, p1 = q1.probabilidades()
        self.assertAlmostEqual(p0, 0.0, places=9)
        self.assertAlmostEqual(p1, 1.0, places=9)

    def test_las_probabilidades_siempre_suman_uno(self):
        rng = random.Random(13)
        for intento in range(40):
            circuito = "".join(rng.choice("XZHI") for _ in range(rng.randint(1, 8)))
            q = cero(rng).aplicar_circuito(circuito)
            p0, p1 = q.probabilidades()
            with self.subTest(circuito=circuito):
                self.assertAlmostEqual(p0 + p1, 1.0, places=9)

    def test_mil_mediciones_de_H_ket0_cerca_del_cincuenta_por_ciento(self):
        q = Qubit(*KET0, rng=random.Random(2026)).h()
        conteo = q.medir_muchas(1000)
        self.assertEqual(conteo[0] + conteo[1], 1000)
        self.assertAlmostEqual(conteo[0] / 1000, 0.5, delta=0.05)

    def test_mediciones_de_estado_definido_son_deterministas(self):
        self.assertEqual(cero(random.Random(1)).medir_muchas(500), {0: 500, 1: 0})
        self.assertEqual(uno(random.Random(1)).medir_muchas(500), {0: 0, 1: 500})

    def test_estado_sesgado_reproduce_sus_probabilidades(self):
        q = Qubit(sqrt(0.25), sqrt(0.75), rng=random.Random(77))
        p0, _ = q.probabilidades()
        self.assertAlmostEqual(p0, 0.25)
        conteo = q.medir_muchas(2000)
        self.assertAlmostEqual(conteo[0] / 2000, 0.25, delta=0.04)

    def test_la_fase_no_cambia_las_probabilidades(self):
        q = Qubit(INV_R2, INV_R2 * 1j)
        p0, p1 = q.probabilidades()
        self.assertAlmostEqual(p0, 0.5, places=12)
        self.assertAlmostEqual(p1, 0.5, places=12)

    def test_colapso_tras_medir(self):
        q = Qubit(*KET0, rng=random.Random(3)).h()
        primera = q.medir()
        self.assertIn(primera, (0, 1))
        self.assertEqual(q.estado, KET0 if primera == 0 else KET1)
        for _ in range(10):                       # ya colapsado: siempre lo mismo
            self.assertEqual(q.medir(), primera)

    def test_normalizacion_automatica(self):
        q = Qubit(3, 4)
        p0, p1 = q.probabilidades()
        self.assertAlmostEqual(p0, 0.36)
        self.assertAlmostEqual(p1, 0.64)
        self.assertAlmostEqual(p0 + p1, 1.0)

    def test_matrices_unitarias(self):
        """Comprueba M * M^dagger = I para X, Z y H (por eso conservan la norma)."""
        for nombre, M in (("X", X), ("Z", Z), ("H", H)):
            for i in range(2):
                for j in range(2):
                    producto = sum(M[i][k] * M[j][k].conjugate() for k in range(2))
                    with self.subTest(compuerta=nombre, i=i, j=j):
                        self.assertAlmostEqual(abs(producto - (1 if i == j else 0)), 0,
                                               places=12)

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            Qubit(0, 0)
        with self.assertRaises(ValueError):
            cero().aplicar_circuito("Q")


if __name__ == "__main__":
    unittest.main(verbosity=2)
