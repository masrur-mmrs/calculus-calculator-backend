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

def classify_differentiation(input):
    if input.is_Add:
        return "sum"
    elif isinstance(input, sp.Mul):
        has_negative_exp = any(isinstance(arg, sp.Pow) and arg.exp.is_Number and arg.exp < 0 for arg in input.args)
        if has_negative_exp:
            return "quotient"
        if len(input.args) > 1:
            return "product"
    elif input.is_Pow:
        return "power"
    elif input.is_Function:
        return input.func.__name__
    elif input.is_Div:
        return "quotient"
    return "unknown"

def quotient_extract_u_v(input):
    if isinstance(input, sp.Mul):
        for term in input.args:
            if isinstance(term, sp.Pow) and term.exp.is_Number and term.exp == -1:
                v=term.base
                u_terms = [t for t in input.args if t != term]  
                u = sp.Mul(*u_terms) if u_terms else 1                
                return u, v
    return None, None


if __name__ == '__main__':
    command = sys.argv[1]
    expression = sys.argv[2]
    expr = latex2sympy(expression)
    
    if command == "classify_differentiation":
        type = classify_differentiation(expr)
        print(json.dumps({"type": type}), flush=True)
    # for line in sys.stdin:
    #     try:
    #         request = json.loads(line)
    #         expression = request.get("expression", "")
    #         variable = request.get("variable", "")
    #         orderOfDerivative = request.get("orderOfDerivative", "")
            
    #         result = differentiate(expression, variable, orderOfDerivative)
            
    #         print(json.dumps({"result": result}), flush=True)
    #     except Exception as e:
    #         print(json.dumps({"error": str(e)}), flush=True)
