"""Pruebas del bloque C (parte logica): tablas de verdad (7) y simplificacion (8).

Ejecucion:  python3 -m unittest discover -s tests -v
"""

import unittest

from src.boole.simplificacion import (a_cubo, combinar, cubrimiento_minimo,
                                      implicantes_primos, minterminos_de_cubo,
                                      simplificar, verificar)
from src.boole.tablas_verdad import (EXPRESIONES_TALLER, compilar, evaluar,
                                     minterminos, son_equivalentes,
                                     tabla_de_verdad, vector_salida)

VARS3 = ["A", "B", "C"]
VARS4 = ["A", "B", "C", "D"]


class TestTablasDeVerdad(unittest.TestCase):
    """Punto 7."""

    def test_tamano_de_la_tabla(self):
        for variables in (["A"], VARS3, VARS4):
            _, filas = tabla_de_verdad("A", variables)
            with self.subTest(n=len(variables)):
                self.assertEqual(len(filas), 2 ** len(variables))

    def test_conectivos_basicos(self):
        self.assertEqual(vector_salida("A & B", ["A", "B"]), (0, 0, 0, 1))
        self.assertEqual(vector_salida("A | B", ["A", "B"]), (0, 1, 1, 1))
        self.assertEqual(vector_salida("A ^ B", ["A", "B"]), (0, 1, 1, 0))
        self.assertEqual(vector_salida("!A", ["A"]), (1, 0))

    def test_expresiones_del_taller(self):
        # (A & B) | !C : vale 1 si C=0, o si A=B=1.
        self.assertEqual(vector_salida(EXPRESIONES_TALLER[0], VARS3),
                         (1, 0, 1, 0, 1, 0, 1, 1))
        # (A ^ B) & C : 1 solo cuando A != B y C = 1.
        self.assertEqual(vector_salida(EXPRESIONES_TALLER[1], VARS3),
                         (0, 0, 0, 1, 0, 1, 0, 0))
        # (A | B) & (!A | C)
        self.assertEqual(vector_salida(EXPRESIONES_TALLER[2], VARS3),
                         (0, 0, 1, 1, 0, 1, 0, 1))

    def test_evaluacion_en_entradas_concretas(self):
        casos = [
            ("(A & B) | (!C)", {"A": 1, "B": 1, "C": 1}, 1),
            ("(A & B) | (!C)", {"A": 0, "B": 0, "C": 1}, 0),
            ("(A & B) | (!C)", {"A": 0, "B": 1, "C": 0}, 1),
            ("(A ^ B) & C", {"A": 1, "B": 0, "C": 1}, 1),
            ("(A ^ B) & C", {"A": 1, "B": 1, "C": 1}, 0),
            ("(A | B) & (!A | C)", {"A": 1, "B": 0, "C": 0}, 0),
            ("(A | B) & (!A | C)", {"A": 1, "B": 0, "C": 1}, 1),
        ]
        for expr, asignacion, esperado in casos:
            with self.subTest(expr=expr, asignacion=asignacion):
                self.assertEqual(evaluar(expr, asignacion), esperado)

    def test_sintaxis_alternativa_con_palabras_y_simbolos(self):
        equivalentes = [
            ("A & B", "A AND B"), ("A & B", "A * B"),
            ("A | B", "A OR B"), ("A | B", "A + B"),
            ("!A", "NOT A"), ("!A", "~A"),
            ("A ^ B", "A XOR B"),
            ("(A & B) | (!C)", "(A ∧ B) ∨ (¬C)"),   # simbolos del enunciado
            ("(A ^ B) & C", "(A ⊕ B) ∧ C"),
        ]
        for e1, e2 in equivalentes:
            with self.subTest(e1=e1, e2=e2):
                self.assertTrue(son_equivalentes(e1, e2, VARS3))

    def test_precedencia_de_operadores(self):
        # NOT > AND > XOR > OR
        self.assertTrue(son_equivalentes("!A & B", "(!A) & B", ["A", "B"]))
        self.assertTrue(son_equivalentes("A | B & C", "A | (B & C)", VARS3))
        self.assertTrue(son_equivalentes("A ^ B & C", "A ^ (B & C)", VARS3))
        self.assertFalse(son_equivalentes("A | B & C", "(A | B) & C", VARS3))

    def test_leyes_del_algebra_de_boole(self):
        leyes = [
            ("!(A & B)", "!A | !B"),          # De Morgan
            ("!(A | B)", "!A & !B"),
            ("A & (B | C)", "(A & B) | (A & C)"),
            ("A | (B & C)", "(A | B) & (A | C)"),
            ("A ^ B", "(A & !B) | (!A & B)"),
            ("!!A", "A"),
            ("A & (A | B)", "A"),             # absorcion
            ("A | (A & B)", "A"),
            ("A & !A", "0"),
            ("A | !A", "1"),
        ]
        for e1, e2 in leyes:
            with self.subTest(e1=e1, e2=e2):
                self.assertTrue(son_equivalentes(e1, e2, VARS3))

    def test_minterminos(self):
        self.assertEqual(minterminos("C", VARS3), [1, 3, 5, 7])
        self.assertEqual(minterminos("A & B & C", VARS3), [7])
        self.assertEqual(minterminos("0", VARS3), [])
        self.assertEqual(minterminos("1", VARS3), list(range(8)))

    def test_variable_faltante_y_errores_de_sintaxis(self):
        with self.assertRaises(KeyError):
            evaluar("A & B", {"A": 1})
        for mala in ["(A & B", "A & & B", "A $ B", "A B )", "", "&A"]:
            with self.subTest(expr=mala), self.assertRaises(ValueError):
                compilar(mala)


class TestSimplificacion(unittest.TestCase):
    """Punto 8."""

    def test_piezas_de_quine_mccluskey(self):
        self.assertEqual(a_cubo(5, 3), "101")
        self.assertEqual(combinar("000", "001"), "00-")
        self.assertIsNone(combinar("000", "011"))     # difieren en 2 bits
        self.assertIsNone(combinar("000", "000"))     # no difieren
        self.assertEqual(minterminos_de_cubo("--1"), {1, 3, 5, 7})
        self.assertEqual(minterminos_de_cubo("101"), {5})

    def test_caso_sugerido_del_taller(self):
        r = simplificar({1, 3, 5, 7}, VARS3)
        self.assertEqual(r["primos"], ["--1"])
        self.assertEqual(r["simplificada"], "C")
        self.assertTrue(son_equivalentes(r["simplificada"], "C", VARS3))
        self.assertTrue(verificar(r))

    def test_implicantes_primos_conocidos(self):
        # f = suma de minterminos 0,1,2,3 con 3 variables  ->  !A
        self.assertEqual(implicantes_primos({0, 1, 2, 3}, 3), ["0--"])
        # minterminos 0 y 7 no se pueden combinar: quedan los dos como primos.
        self.assertEqual(implicantes_primos({0, 7}, 3), ["000", "111"])

    def test_misma_tabla_de_verdad_que_la_original(self):
        casos = [
            ({1, 3, 5, 7}, VARS3),
            ({0, 1, 2, 5, 6, 7}, VARS3),
            ({0, 7}, VARS3),
            ({1, 2, 5, 6}, VARS3),
            ({0, 1, 2, 5, 6, 7, 8, 9, 10, 14}, VARS4),
            ({4, 8, 9, 10, 11, 12, 14, 15}, VARS4),
            ({0, 1, 4, 5, 8, 9, 12, 13}, VARS4),
        ]
        for minterms, variables in casos:
            r = simplificar(minterms, variables)
            with self.subTest(minterms=sorted(minterms)):
                self.assertTrue(verificar(r))
                self.assertEqual(set(minterminos(r["simplificada"], variables)),
                                 set(minterms))

    def test_casos_constantes(self):
        r0 = simplificar(set(), VARS3)
        self.assertEqual(r0["simplificada"], "0")
        self.assertTrue(verificar(r0))
        r1 = simplificar(set(range(8)), VARS3)
        self.assertEqual(r1["simplificada"], "1")
        self.assertTrue(verificar(r1))

    def test_la_simplificada_nunca_usa_mas_literales(self):
        for mascara in range(256):
            minterms = {i for i in range(8) if (mascara >> i) & 1}
            r = simplificar(minterms, VARS3)
            with self.subTest(mascara=mascara):
                self.assertLessEqual(r["literales_simplificada"],
                                     r["literales_canonica"])

    def test_exhaustivo_todas_las_funciones_de_tres_variables(self):
        """256 funciones posibles: la simplificacion debe conservar la tabla."""
        for mascara in range(256):
            minterms = {i for i in range(8) if (mascara >> i) & 1}
            r = simplificar(minterms, VARS3)
            with self.subTest(mascara=mascara):
                self.assertTrue(verificar(r))

    def test_muestra_de_funciones_de_cuatro_variables(self):
        for mascara in range(0, 65536, 137):
            minterms = {i for i in range(16) if (mascara >> i) & 1}
            r = simplificar(minterms, VARS4)
            with self.subTest(mascara=mascara):
                self.assertTrue(verificar(r))

    def test_cubrimiento_minimo_elige_lo_esencial(self):
        primos = implicantes_primos({0, 1, 2, 3, 4, 5}, 3)
        elegidos = cubrimiento_minimo(primos, {0, 1, 2, 3, 4, 5})
        cubiertos = set()
        for cubo in elegidos:
            cubiertos |= minterminos_de_cubo(cubo)
        self.assertTrue({0, 1, 2, 3, 4, 5} <= cubiertos)
        self.assertLessEqual(len(elegidos), len(primos))

    def test_mintermino_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            simplificar({8}, VARS3)      # con 3 variables solo hay 0..7


if __name__ == "__main__":
    unittest.main(verbosity=2)
