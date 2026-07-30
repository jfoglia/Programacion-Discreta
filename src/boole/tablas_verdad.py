"""
Punto 7 - Tablas de verdad y circuitos logicos.

Se implementa un evaluador propio de expresiones booleanas: tokenizador +
analizador descendente recursivo (recursive descent) + evaluador. No se usa
eval() de Python ni librerias externas.

Gramatica reconocida (de menor a mayor precedencia):
    or_expr   -> xor_expr ( ('|' | 'OR' | '+') xor_expr )*
    xor_expr  -> and_expr ( ('^' | 'XOR') and_expr )*
    and_expr  -> unario   ( ('&' | 'AND' | '*') unario )*
    unario    -> ('!' | '~' | 'NOT' | '-') unario | atomo
    atomo     -> VARIABLE | '0' | '1' | '(' or_expr ')'

Idea matematica
---------------
Una expresion con n variables define una funcion f: {0,1}^n -> {0,1}.
La tabla de verdad es simplemente esa funcion escrita como tabla: las 2^n
filas son todos los elementos del dominio. Cada conectivo es una operacion
del algebra de Boole: AND = producto, OR = suma booleana, NOT = complemento,
XOR = suma modulo 2. Cada fila corresponde a un estado de las entradas de un
circuito y el resultado es lo que mide la salida.

Ejecucion:
    python3 src/boole/tablas_verdad.py
"""

from itertools import product

# Palabras y simbolos aceptados para cada operador.
OPERADORES = {
    "OR": {"|", "+", "OR"},
    "XOR": {"^", "XOR"},
    "AND": {"&", "*", "AND"},
    "NOT": {"!", "~", "NOT", "-"},
}
SIMBOLOS = "()|+^&*!~-"


# --------------------------------------------------------------- tokenizacion
def tokenizar(expresion: str) -> list[str]:
    """Parte la expresion en tokens: variables, palabras, simbolos y parentesis."""
    tokens: list[str] = []
    i = 0
    texto = expresion.replace("¬", "!").replace("∧", "&").replace("∨", "|").replace("⊕", "^")
    while i < len(texto):
        c = texto[i]
        if c.isspace():
            i += 1
        elif c in SIMBOLOS:
            tokens.append(c)
            i += 1
        elif c.isalnum() or c == "_":
            j = i
            while j < len(texto) and (texto[j].isalnum() or texto[j] == "_"):
                j += 1
            tokens.append(texto[i:j])
            i = j
        else:
            raise ValueError(f"caracter no reconocido en la expresion: {c!r}")
    return tokens


# ---------------------------------------------------- arbol y analizador
class Nodo:
    """Nodo del arbol de sintaxis. tipo: VAR, CONST, NOT, AND, OR, XOR."""

    def __init__(self, tipo: str, valor=None, hijos: list["Nodo"] | None = None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos or []

    def evaluar(self, asignacion: dict[str, int]) -> int:
        """Evalua el nodo con los valores dados. Devuelve 0 o 1."""
        if self.tipo == "CONST":
            return self.valor
        if self.tipo == "VAR":
            if self.valor not in asignacion:
                raise KeyError(f"falta el valor de la variable {self.valor}")
            return 1 if asignacion[self.valor] else 0
        if self.tipo == "NOT":
            return 1 - self.hijos[0].evaluar(asignacion)
        a = self.hijos[0].evaluar(asignacion)
        b = self.hijos[1].evaluar(asignacion)
        if self.tipo == "AND":
            return a & b
        if self.tipo == "OR":
            return a | b
        if self.tipo == "XOR":
            return a ^ b           # suma modulo 2
        raise ValueError(f"tipo de nodo desconocido: {self.tipo}")

    def variables(self) -> set[str]:
        if self.tipo == "VAR":
            return {self.valor}
        return set().union(*(h.variables() for h in self.hijos)) if self.hijos else set()

    def __repr__(self) -> str:
        if self.tipo in ("VAR", "CONST"):
            return str(self.valor)
        if self.tipo == "NOT":
            return f"!{self.hijos[0]!r}"
        simbolo = {"AND": " & ", "OR": " | ", "XOR": " ^ "}[self.tipo]
        return f"({self.hijos[0]!r}{simbolo}{self.hijos[1]!r})"


class Parser:
    """Analizador descendente recursivo para la gramatica de arriba."""

    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def _mirar(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _coincide(self, conjunto: set[str]) -> str | None:
        """Consume el token actual si pertenece al conjunto (sin importar mayusculas)."""
        t = self._mirar()
        if t is not None and t.upper() in conjunto:
            self.pos += 1
            return t
        return None

    def analizar(self) -> Nodo:
        nodo = self._or()
        if self.pos != len(self.tokens):
            raise ValueError(f"token inesperado: {self.tokens[self.pos]!r}")
        return nodo

    def _or(self) -> Nodo:
        nodo = self._xor()
        while self._coincide(OPERADORES["OR"]):
            nodo = Nodo("OR", hijos=[nodo, self._xor()])
        return nodo

    def _xor(self) -> Nodo:
        nodo = self._and()
        while self._coincide(OPERADORES["XOR"]):
            nodo = Nodo("XOR", hijos=[nodo, self._and()])
        return nodo

    def _and(self) -> Nodo:
        nodo = self._unario()
        while self._coincide(OPERADORES["AND"]):
            nodo = Nodo("AND", hijos=[nodo, self._unario()])
        return nodo

    def _unario(self) -> Nodo:
        if self._coincide(OPERADORES["NOT"]):
            return Nodo("NOT", hijos=[self._unario()])
        return self._atomo()

    def _atomo(self) -> Nodo:
        t = self._mirar()
        if t is None:
            raise ValueError("expresion incompleta")
        if t == "(":
            self.pos += 1
            nodo = self._or()
            if self._mirar() != ")":
                raise ValueError("falta cerrar un parentesis")
            self.pos += 1
            return nodo
        if t == ")":
            raise ValueError("parentesis de cierre sin abrir")
        self.pos += 1
        if t in ("0", "1"):
            return Nodo("CONST", int(t))
        if t.upper() in set().union(*OPERADORES.values()):
            raise ValueError(f"operador en posicion de variable: {t!r}")
        return Nodo("VAR", t)


def compilar(expresion: str) -> Nodo:
    """Texto -> arbol de sintaxis listo para evaluar."""
    return Parser(tokenizar(expresion)).analizar()


def evaluar(expresion: str, asignacion: dict[str, int]) -> int:
    """Evalua la expresion en una entrada concreta, p.ej. {'A':1,'B':0,'C':1}."""
    return compilar(expresion).evaluar(asignacion)


# ------------------------------------------------------------ tabla de verdad
def tabla_de_verdad(expresion: str, variables: list[str] | None = None
                    ) -> tuple[list[str], list[tuple[tuple[int, ...], int]]]:
    """Devuelve (variables, filas) donde cada fila es ((valores...), resultado).

    Las filas se generan en orden binario ascendente: 000, 001, 010, ...
    """
    arbol = compilar(expresion)
    if variables is None:
        variables = sorted(arbol.variables())
    filas = []
    for combinacion in product((0, 1), repeat=len(variables)):
        asignacion = dict(zip(variables, combinacion))
        filas.append((combinacion, arbol.evaluar(asignacion)))
    return variables, filas


def vector_salida(expresion: str, variables: list[str] | None = None) -> tuple[int, ...]:
    """Solo la columna de resultados. Dos expresiones son equivalentes si coincide."""
    return tuple(r for _, r in tabla_de_verdad(expresion, variables)[1])


def son_equivalentes(expr1: str, expr2: str, variables: list[str] | None = None) -> bool:
    """True si las dos expresiones tienen la misma tabla de verdad."""
    if variables is None:
        variables = sorted(compilar(expr1).variables() | compilar(expr2).variables())
    return vector_salida(expr1, variables) == vector_salida(expr2, variables)


def minterminos(expresion: str, variables: list[str] | None = None) -> list[int]:
    """Indices de las filas donde la funcion vale 1 (utiles para el punto 8)."""
    variables, filas = tabla_de_verdad(expresion, variables)
    return [i for i, (_, r) in enumerate(filas) if r == 1]


def imprimir_tabla(expresion: str, variables: list[str] | None = None) -> None:
    """Imprime la tabla de verdad completa con encabezado."""
    variables, filas = tabla_de_verdad(expresion, variables)
    print(f"\n  Expresion: {expresion}")
    encabezado = "  ".join(variables)
    print(f"    #  {encabezado} | salida")
    print("    " + "-" * (len(encabezado) + 12))
    for i, (valores, resultado) in enumerate(filas):
        fila = "  ".join(str(v) for v in valores)
        print(f"    {i:2d}  {fila} |   {resultado}")
    unos = sum(r for _, r in filas)
    print(f"    Filas en 1: {unos} de {len(filas)}  -> minterminos "
          f"{minterminos(expresion, variables)}")


# ---------------------------------------------------------------- demostracion
EXPRESIONES_TALLER = [
    "(A & B) | (!C)",       # (A AND B) OR (NOT C)
    "(A ^ B) & C",          # (A XOR B) AND C
    "(A | B) & (!A | C)",    # (A OR B) AND (NOT A OR C)
]


def _demo() -> None:
    print("=" * 72)
    print("PUNTO 7 - TABLAS DE VERDAD Y CIRCUITOS LOGICOS")
    print("=" * 72)

    print("\n[1] Las tres expresiones pedidas en el taller (variables A, B, C)")
    for expr in EXPRESIONES_TALLER:
        imprimir_tabla(expr, ["A", "B", "C"])

    print("\n[2] Una expresion con las cuatro variables A, B, C, D")
    imprimir_tabla("(A & !B) | (C ^ D)", ["A", "B", "C", "D"])

    print("\n[3] Evaluacion en entradas concretas")
    casos = [
        ("(A & B) | (!C)", {"A": 1, "B": 1, "C": 1}),
        ("(A & B) | (!C)", {"A": 0, "B": 1, "C": 0}),
        ("(A ^ B) & C", {"A": 1, "B": 0, "C": 1}),
        ("(A | B) & (!A | C)", {"A": 1, "B": 0, "C": 0}),
        ("A AND NOT B OR C", {"A": 1, "B": 1, "C": 0}),   # sintaxis con palabras
    ]
    for expr, asignacion in casos:
        entrada = ", ".join(f"{k}={v}" for k, v in sorted(asignacion.items()))
        print(f"  {expr:22s} con {entrada:18s} -> {evaluar(expr, asignacion)}")

    print("\n[4] Leyes del algebra de Boole verificadas con las tablas")
    leyes = [
        ("De Morgan",        "!(A & B)", "!A | !B"),
        ("De Morgan (dual)", "!(A | B)", "!A & !B"),
        ("Distributiva",     "A & (B | C)", "(A & B) | (A & C)"),
        ("XOR con AND/OR",   "A ^ B", "(A & !B) | (!A & B)"),
        ("Doble negacion",   "!!A", "A"),
        ("Falsa (control)",  "A & B", "A | B"),
    ]
    for nombre, e1, e2 in leyes:
        print(f"  {nombre:18s} {e1:14s} == {e2:20s} -> {son_equivalentes(e1, e2)}")

    print("\n[5] Errores de sintaxis detectados")
    for mala in ["(A & B", "A & & B", "A $ B"]:
        try:
            compilar(mala)
            print(f"  {mala!r}: NO se detecto (mal)")
        except ValueError as err:
            print(f"  {mala!r}: rechazada -> {err}")


if __name__ == "__main__":
    _demo()
