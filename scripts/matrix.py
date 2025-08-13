import sys
import sympy as sp
import json
import re
from sympy import Matrix, latex, simplify, Rational

def parse_and_evaluate_matrix_expression(expression):
    """
    Parse and evaluate matrix expressions step by step to handle mixed types properly
    """
    try:
        # Create a safe namespace
        safe_globals = {
            '__builtins__': {},
            'Matrix': Matrix,
            'Rational': Rational,
        }
        
        processed_expr = expression
    
        result = eval(processed_expr, safe_globals)
        
        if isinstance(result, Matrix):
            latex_result = latex(result, mat_str='pmatrix')
            return latex_result
        elif hasattr(result, 'is_number') and result.is_number:
            return latex(simplify(result))
        else:
            return latex(simplify(result))
            
    except Exception as e:
        raise Exception(f"Error evaluating matrix expression: {str(e)}")

def process_matrix_operations(expression):
    """
    Process matrix operations and return LaTeX formatted result
    """
    try:
        result = parse_and_evaluate_matrix_expression(expression)
        return result
    except Exception as e:
        raise Exception(f"Matrix operation failed: {str(e)}")

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            
            if not expression:
                print(json.dumps({"error": "No expression provided"}), flush=True)
                continue
            
            result = process_matrix_operations(expression)
            print(json.dumps({"result": result}), flush=True)
            
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)