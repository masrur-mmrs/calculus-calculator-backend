import sys
import sympy as sp
import json
from sympy.parsing.latex import parse_latex
from latex2sympy2 import latex2sympy, latex2latex

def integrate(expr, var):
    x = sp.symbols(var)
    if isinstance(expr, str):
        expr = latex2sympy(expr)
    f = expr
    it = sp.integrate(f, x)
    if "Integral" in str(it.__class__):
        return sp.latex(it.doit())
    else:
        return sp.latex(it)

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            variable = request.get("variable", "")
            
            result = integrate(expression, variable)
            
            print(json.dumps({"result": result}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)