# Taller 3 - Programación discreta

**Matemáticas Discretas I — Universidad Nacional de Colombia**
Criptografía, grafos, álgebra de Boole, Shannon y un primer vistazo cuántico.

- **Integrantes:** Julián Andrés Foglia Wilches
- **Docente:** Jhoan Sebastián Tenjo García
- **Lenguaje:** Python 3.10 o superior (probado en 3.12)
- **Dependencias externas:** ninguna. Solo librería estándar (ver `requirements.txt`)

---

## Cómo ejecutar

Desde la **raíz del repositorio** (importante, para que las rutas e imports funcionen):

```bash
# 1) Ver los 10 puntos con sus ejemplos y verificaciones
python3 run_all.py

# 2) Ejecutar solo algunos puntos
python3 run_all.py 2 7 10
python3 run_all.py --lista          # lista los puntos disponibles

# 3) Ejecutar un punto por su propio archivo (cada módulo es autónomo)
python3 src/cripto/cesar.py
python3 src/cripto/rsa_juguete.py
python3 src/cripto/mpc_promedio.py
python3 src/grafos/dijkstra.py
python3 src/grafos/cierre.py
python3 src/grafos/coloreo.py
python3 src/boole/tablas_verdad.py
python3 src/boole/simplificacion.py
python3 src/info/shannon.py
python3 src/cuantica/qubit.py

# 4) Correr las pruebas automáticas (96 pruebas)
python3 -m unittest discover -s tests          # resumen
python3 -m unittest discover -s tests -v       # detalle prueba por prueba
python3 -m unittest tests.test_boole -v        # solo un bloque
```

No hay que instalar nada ni configurar variables de entorno.

---

## Estructura del repositorio

```
.
├── README.md                  este archivo
├── requirements.txt           explica que no se usan librerías externas
├── run_all.py                 lanzador: ejecuta la demo de los 10 puntos
├── data/
│   └── ciudad.txt             grafo de prueba (10 vértices, 15 aristas)
├── docs/
│   ├── explicacion.md         documento de explicación matemática (los 10 puntos)
│   └── explicacion.pdf        el mismo documento en PDF (generado con pandoc)
├── src/
│   ├── cripto/
│   │   ├── cesar.py           punto 1
│   │   ├── rsa_juguete.py     punto 2
│   │   └── mpc_promedio.py    punto 3
│   ├── grafos/
│   │   ├── grafo.py           estructura de grafo ponderado (compartida)
│   │   ├── dijkstra.py        punto 4
│   │   ├── cierre.py          punto 5
│   │   └── coloreo.py         punto 6
│   ├── boole/
│   │   ├── tablas_verdad.py   punto 7
│   │   └── simplificacion.py  punto 8
│   ├── info/
│   │   └── shannon.py         punto 9
│   └── cuantica/
│       └── qubit.py           punto 10
└── tests/
    ├── test_cripto.py         puntos 1-3
    ├── test_grafos.py         puntos 4-6
    ├── test_boole.py          puntos 7-8
    └── test_info_cuantica.py  puntos 9-10
```

---

## Lista de ejercicios desarrollados

| # | Punto | Archivo | Qué hace |
|---|-------|---------|----------|
| 1 | Cifrado César | `src/cripto/cesar.py` | Cifra, descifra y rompe por fuerza bruta (26 claves, ordenadas por parecido al español) |
| 2 | RSA de juguete | `src/cripto/rsa_juguete.py` | Euclides extendido, inverso modular y exponenciación modular propios; valida `gcd(e, φ(n)) = 1` |
| 3 | MPC básico | `src/cripto/mpc_promedio.py` | Suma secreta con 3 servidores: reparto aditivo módulo `M = 1000003` |
| 4 | Dijkstra | `src/grafos/dijkstra.py` | Ruta mínima y distancia; grafo cargado desde `data/ciudad.txt` |
| 5 | Cierre de estación | `src/grafos/cierre.py` | Tabla origen/destino/antes/después/diferencia/estado en 4 escenarios de cierre |
| 6 | Coloreo de grafos | `src/grafos/coloreo.py` | Voraz con orden Welsh-Powell sobre 12 cursos; verifica validez y compara órdenes |
| 7 | Tablas de verdad | `src/boole/tablas_verdad.py` | Evaluador propio (tokenizador + parser recursivo) para AND, OR, NOT, XOR con A, B, C, D |
| 8 | Simplificación booleana | `src/boole/simplificacion.py` | Quine-McCluskey propio + cubrimiento mínimo exacto; verifica igualdad de tablas |
| 9 | Entropía de Shannon | `src/info/shannon.py` | Frecuencias, probabilidades, `H = -Σ pᵢ log₂ pᵢ`, comparación de textos y Huffman (extensión) |
| 10 | Simulador cuántico | `src/cuantica/qubit.py` | Estado como vector de 2 amplitudes complejas, compuertas X/Z/H, 1000 mediciones |

---

## Resultados de los casos obligatorios del taller

Todos verificados por las pruebas automáticas y visibles al ejecutar `run_all.py`:

| Caso exigido | Resultado obtenido |
|--------------|--------------------|
| César: `HOLA UNAL` con `k = 3` | `KROD XQDO` ✔ |
| RSA: `p=61, q=53, e=17, M=65` | `n = 3233`, `φ(n) = 3120`, `d = 2753`, `C = 2790`, descifrado `65` ✔ |
| MPC: notas `[40, 35, 50, 25]` | suma `150`, promedio `37.5` (los servidores solo publican totales enmascarados) ✔ |
| Dijkstra: grafo con ≥ 8 vértices y ≥ 12 aristas | 10 vértices, 15 aristas ✔ |
| Cierre: ≥ 5 pares origen-destino | 6 pares × 4 escenarios; detecta `DESCONECTADO` ✔ |
| Coloreo: ≥ 10 vértices | 12 cursos, 24 conflictos, 3 franjas, coloreo válido ✔ |
| Tablas de verdad: mínimo 3 expresiones | las 3 del enunciado + una de 4 variables ✔ |
| Simplificación: minterminos `{1,3,5,7}` | `C` (con la misma tabla de verdad que la forma canónica) ✔ |
| Shannon: 2 mensajes (repetitivo vs variado) | `H = 0.2108` vs `H = 3.9931` bits/símbolo ✔ |
| Cuántico: `X\|0⟩ = \|1⟩`, `H\|0⟩ ≈ 50/50`, `HH\|0⟩ = \|0⟩` | los tres se cumplen; 1000 mediciones reportadas ✔ |

---

## Pruebas

```
$ python3 -m unittest discover -s tests
................................................................................................
Ran 96 tests in 0.194s

OK
```

Las pruebas no solo revisan los casos del enunciado; también verifican propiedades
matemáticas: identidad de Bézout en Euclides extendido, desigualdad triangular y
simetría en Dijkstra, comparación de Dijkstra contra Bellman-Ford en grafos
aleatorios, validez del coloreo para 50 órdenes al azar, las 256 funciones
booleanas de 3 variables simplificadas correctamente, la cota `H ≤ L < H+1` de
Huffman y la unitariedad de las compuertas cuánticas.

---

## Documentación

La explicación matemática de cada punto (qué problema resuelve, qué idea
matemática usa, cómo se ejecuta, qué pruebas se hicieron y qué limitaciones
tiene) está en [`docs/explicacion.md`](docs/explicacion.md) y en
[`docs/explicacion.pdf`](docs/explicacion.pdf). El PDF se regenera con:

```bash
pandoc docs/explicacion.md -o docs/explicacion.pdf --pdf-engine=xelatex \
  -V geometry:margin=2.5cm -V mainfont="DejaVu Serif" \
  -V monofont="DejaVu Sans Mono" -V fontsize=10pt --toc
```

Ese documento también responde las preguntas específicas del enunciado
(por qué descifrar usa el desplazamiento contrario, por qué Dijkstra necesita
pesos no negativos, por qué el voraz no garantiza el mínimo de colores, qué es un
mintermino, por qué la entropía mide incertidumbre y no longitud, etc.).

---

## Notas sobre las limitaciones

- El RSA es **de juguete**: primos de dos dígitos, sin relleno (padding) y
  cifrando carácter por carácter. No sirve como seguridad real.
- El MPC es una **simulación** en un solo proceso: no hay red, ni canales
  autenticados, ni servidores maliciosos. Muestra la idea del reparto aditivo.
- El simulador cuántico maneja **un solo qubit**: no hay entrelazamiento ni
  compuertas de dos qubits, y el azar es pseudoaleatorio clásico.
