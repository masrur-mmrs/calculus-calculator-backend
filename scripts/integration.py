import sys
import sympy as sp
import json
from latex2sympy2 import latex2sympy

def integrate(expr, var):
    x = sp.Symbol(var.replace('\\', ''))
    if isinstance(expr, str):
        expr = latex2sympy(expr)
    result = sp.integrate(expr, x)
    return sp.latex(result)

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