"""Pruebas del bloque A: Cesar (punto 1), RSA (punto 2), MPC (punto 3).

Ejecucion:  python3 -m unittest discover -s tests -v
"""

import random
import unittest

from src.cripto import cesar, mpc_promedio, rsa_juguete


class TestCesar(unittest.TestCase):
    """Punto 1."""

    def test_ejemplo_minimo_del_taller(self):
        self.assertEqual(cesar.cifrar("HOLA UNAL", 3), "KROD XQDO")

    def test_descifrar_deshace_el_cifrado(self):
        for texto in ["HOLA UNAL", "Matematicas Discretas I", "abc XYZ", ""]:
            for k in range(-30, 31):
                with self.subTest(texto=texto, k=k):
                    self.assertEqual(cesar.descifrar(cesar.cifrar(texto, k), k), texto)

    def test_conserva_espacios_signos_numeros_y_caso(self):
        original = "Ataque al amanecer, 5 tanques! (urgente)"
        cifrado = cesar.cifrar(original, 7)
        self.assertEqual(cifrado, "Hahxbl hs hthuljly, 5 ahuxblz! (bynlual)")
        # Los caracteres no alfabeticos quedan en la misma posicion.
        for a, b in zip(original, cifrado):
            if not a.isalpha():
                self.assertEqual(a, b)
            else:
                self.assertEqual(a.isupper(), b.isupper())

    def test_wrap_around_modulo_26(self):
        self.assertEqual(cesar.cifrar("XYZ", 3), "ABC")
        self.assertEqual(cesar.cifrar("ABC", -1), "ZAB")
        self.assertEqual(cesar.cifrar("UNAL", 26), "UNAL")   # k = 0 mod 26

    def test_fuerza_bruta_lista_las_26_opciones(self):
        candidatos = cesar.fuerza_bruta(cesar.cifrar("PRUEBA", 5))
        self.assertEqual(len(candidatos), 26)
        self.assertEqual(sorted(k for k, _, _ in candidatos), list(range(26)))
        # El texto correcto esta entre los candidatos.
        self.assertIn("PRUEBA", [texto for _, texto, _ in candidatos])

    def test_romper_encuentra_la_clave_en_textos_largos(self):
        mensaje = ("LA CRIPTOGRAFIA CLASICA OCULTA UN MENSAJE MEDIANTE UNA "
                   "TRANSFORMACION REVERSIBLE DE LAS LETRAS DEL ALFABETO")
        for k in (3, 7, 11, 19, 25):
            with self.subTest(k=k):
                k_est, texto = cesar.romper(cesar.cifrar(mensaje, k))
                self.assertEqual(k_est, k)
                self.assertEqual(texto, mensaje)


class TestRSA(unittest.TestCase):
    """Punto 2."""

    def test_caso_obligatorio_del_taller(self):
        llaves = rsa_juguete.generar_llaves(61, 53, 17)
        self.assertEqual(llaves["n"], 3233)
        self.assertEqual(llaves["phi"], 3120)
        self.assertEqual(llaves["d"], 2753)
        C = rsa_juguete.cifrar(65, llaves["publica"])
        self.assertEqual(C, 2790)
        self.assertEqual(rsa_juguete.descifrar(C, llaves["privada"]), 65)

    def test_euclides_extendido_cumple_bezout(self):
        for a, b in [(240, 46), (17, 3120), (35, 64), (0, 5), (7, 7)]:
            g, x, y = rsa_juguete.euclides_extendido(a, b)
            with self.subTest(a=a, b=b):
                self.assertEqual(a * x + b * y, g)
                self.assertEqual(g, __import__("math").gcd(a, b))

    def test_inverso_modular(self):
        self.assertEqual(rsa_juguete.inverso_modular(17, 3120), 2753)
        self.assertEqual(rsa_juguete.inverso_modular(3, 7), 5)
        for a, m in [(7, 26), (5, 12), (11, 100)]:
            with self.subTest(a=a, m=m):
                self.assertEqual((a * rsa_juguete.inverso_modular(a, m)) % m, 1)
        with self.assertRaises(ValueError):      # gcd(4, 8) = 4 != 1
            rsa_juguete.inverso_modular(4, 8)

    def test_potencia_modular_coincide_con_pow(self):
        for base, exp, mod in [(65, 17, 3233), (2, 100, 1000), (7, 0, 13), (0, 5, 7)]:
            with self.subTest(base=base, exp=exp, mod=mod):
                self.assertEqual(rsa_juguete.potencia_modular(base, exp, mod),
                                 pow(base, exp, mod))

    def test_ida_y_vuelta_para_todos_los_mensajes(self):
        llaves = rsa_juguete.generar_llaves(17, 11, 7)   # n = 187
        for m in range(llaves["n"]):
            with self.subTest(m=m):
                C = rsa_juguete.cifrar(m, llaves["publica"])
                self.assertEqual(rsa_juguete.descifrar(C, llaves["privada"]), m)

    def test_texto_completo(self):
        llaves = rsa_juguete.generar_llaves(101, 103, 7)
        texto = "UNAL 2026 - Discretas I"
        bloques = rsa_juguete.cifrar_texto(texto, llaves["publica"])
        self.assertEqual(rsa_juguete.descifrar_texto(bloques, llaves["privada"]), texto)

    def test_avisa_cuando_e_no_es_valido(self):
        with self.assertRaises(ValueError):     # gcd(13, 3120) = 13
            rsa_juguete.generar_llaves(61, 53, 13)
        with self.assertRaises(ValueError):     # p no primo
            rsa_juguete.generar_llaves(60, 53, 17)
        with self.assertRaises(ValueError):     # p == q
            rsa_juguete.generar_llaves(61, 61, 17)
        with self.assertRaises(ValueError):     # e fuera de rango
            rsa_juguete.generar_llaves(61, 53, 999_999)

    def test_mensaje_fuera_de_rango(self):
        llaves = rsa_juguete.generar_llaves(61, 53, 17)
        with self.assertRaises(ValueError):
            rsa_juguete.cifrar(llaves["n"], llaves["publica"])
        with self.assertRaises(ValueError):
            rsa_juguete.cifrar(-1, llaves["publica"])


class TestMPC(unittest.TestCase):
    """Punto 3."""

    def test_ejemplo_minimo_del_taller(self):
        suma, promedio, _ = mpc_promedio.protocolo_suma_secreta([40, 35, 50, 25])
        self.assertEqual(suma, 150)
        self.assertAlmostEqual(promedio, 37.5)

    def test_las_partes_reconstruyen_el_valor(self):
        rng = random.Random(1)
        for valor in range(0, 51):
            partes = mpc_promedio.repartir(valor, rng=rng)
            with self.subTest(valor=valor):
                self.assertEqual(len(partes), 3)
                self.assertEqual(sum(partes) % mpc_promedio.MODULO, valor)

    def test_ninguna_parte_sola_revela_la_nota(self):
        """Dos partes cualesquiera no determinan el valor: falta la tercera."""
        rng = random.Random(2)
        partes_a = mpc_promedio.repartir(10, rng=rng)
        partes_b = mpc_promedio.repartir(50, rng=rng)
        # Las partes individuales pueden ser cualquier numero del rango.
        for parte in partes_a + partes_b:
            self.assertTrue(0 <= parte < mpc_promedio.MODULO)
        # Con las dos primeras partes de A se puede "explicar" cualquier nota:
        # basta cambiar la tercera. Es decir, no hay informacion en 2 partes.
        for nota_hipotetica in range(51):
            tercera = (nota_hipotetica - partes_a[0] - partes_a[1]) % mpc_promedio.MODULO
            self.assertEqual((partes_a[0] + partes_a[1] + tercera) % mpc_promedio.MODULO,
                             nota_hipotetica)

    def test_ningun_servidor_ve_la_lista_original(self):
        notas = [40, 35, 50, 25]
        _, _, servidores = mpc_promedio.protocolo_suma_secreta(notas)
        self.assertEqual(len(servidores), 3)
        for s in servidores:
            self.assertEqual(len(s.partes_vistas), len(notas))
            # Es practicamente imposible que las partes coincidan con las notas.
            self.assertNotEqual(s.partes_vistas, notas)

    def test_listas_de_cualquier_tamano(self):
        rng = random.Random(3)
        for n in (1, 2, 7, 100, 500):
            notas = [rng.randint(0, 50) for _ in range(n)]
            suma, promedio, _ = mpc_promedio.protocolo_suma_secreta(notas)
            with self.subTest(n=n):
                self.assertEqual(suma, sum(notas))
                self.assertAlmostEqual(promedio, sum(notas) / n)

    def test_validaciones(self):
        for invalida in ([], [51], [-1], [10, 3.5]):
            with self.subTest(notas=invalida), self.assertRaises(ValueError):
                mpc_promedio.protocolo_suma_secreta(invalida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
