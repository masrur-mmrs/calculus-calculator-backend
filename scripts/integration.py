import sys
import sympy as sp
import json
from sympy.parsing.latex import parse_latex
from latex2sympy2 import latex2sympy, latex2latex


def integrate(expr, var):
    x = sp.symbols(var)
    f = sp.sympify(expr)
    it = sp.integrate(f, x)
    if "Integral" in str(it.__class__):
        return it.doit()
    else:
        return it

if __name__ == '__main__':
    expr = sys.argv[1]
    expr = latex2sympy(expr)
    var = sys.argv[2]
    try:
        result = integrate(expr, var)
        print(json.dumps({"result": sp.latex(result)}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))