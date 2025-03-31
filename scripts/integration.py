import sys
import sympy as sp
import json
from latex2sympy2 import latex2sympy

def integrate(expr, var):
    x = sp.Symbol(var.replace('\\', ''))
    if isinstance(expr, str):
        expr = latex2sympy(expr)
    it = sp.integrate(expr, x)
    it = sp.simplify(it)
    return sp.latex(it)

def integrate_with_bounds(expr, var, ub, lb):
    x = sp.Symbol(var.replace('\\', ''))
    ub = latex2sympy(ub.replace('\\infty', 'oo'))
    lb = latex2sympy(lb.replace('\\infty', 'oo'))
    if isinstance(expr, str):
        expr = latex2sympy(expr)
    it = sp.integrate(expr, (x, lb, ub))
    it = sp.simplify(it)
    return sp.latex(it)

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            variable = request.get("variable", "")
            bound = request.get("bound", {})
            upper_bound = bound.get("upperBound", "")
            lower_bound = bound.get("lowerBound", "")
            if upper_bound == "" and lower_bound == "":
                result = integrate(expression, variable)
            else:
                result = integrate_with_bounds(expression, variable, upper_bound, lower_bound)
            print(json.dumps({"result": result}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)