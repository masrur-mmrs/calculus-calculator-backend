import sys
import json
import sympy as sp
from latex2sympy2 import latex2sympy
import re

def convert_degrees_to_radians(expr: str) -> str:
    degree_pattern = r'(\d+)\s*(\\deg|\\degree|\^\s*\\circ)'
    matches = re.finditer(degree_pattern, expr)
    for match in matches:
        degrees = match.group(1)
        radians_expr = f'\\frac{{{degrees} \\pi}}{{180}}'
        expr = expr.replace(match.group(0), radians_expr)
    return expr

def preprocess_latex(expr: str) -> str:
    expr = expr.replace('%', '/100')
    expr = expr.replace('\\/', '/')
    expr = convert_degrees_to_radians(expr)
    return expr

def evaluate_latex_expression(expr: str):
    expr = preprocess_latex(expr)
    sym_expr = latex2sympy(expr)
    simplified = sp.simplify(sym_expr)
    decimal = simplified.evalf()
    return {
        "exact": sp.latex(simplified),
        "decimal": float(decimal)
    }

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            result = evaluate_latex_expression(expression)
            print(json.dumps({"result": result}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)