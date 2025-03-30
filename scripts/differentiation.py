import sys
import sympy as sp
import json
from latex2sympy2 import latex2sympy

def differentiate(expr, var, ood):
    x = sp.symbols(var.replace("\\", ""))
    if isinstance(expr, str):
        expr = latex2sympy(expr)
    df = sp.diff(expr, x, ood)
    df = sp.simplify(df)
    return sp.latex(df)

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            variable = request.get("variable", "")
            orderOfDerivative = request.get("orderOfDerivative", "")
            
            result = differentiate(expression, variable, orderOfDerivative)
            
            print(json.dumps({"result": result}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)