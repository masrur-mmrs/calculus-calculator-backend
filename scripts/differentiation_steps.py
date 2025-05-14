import json
import sys
import sympy as sp
from latex2sympy2 import latex2sympy

# dont ask why I need this, but I need this
x, y, z, theta = sp.symbols('x y z theta')

def calculate_derivative(expr, var):
    try:
        derivative = sp.diff(expr, var)
        return derivative
    except Exception as e:
        return f"Error: {e}"

def classify_differentiation(input, chain_flag=True):
    if input.is_Add:
        if any(term.could_extract_minus_sign() for term in input.args[1:]):
            return "difference"
        return "sum"
    elif isinstance(input, sp.Mul):
        has_negative_exp = any(isinstance(arg, sp.Pow) and arg.exp.is_Number and arg.exp < 0 for arg in input.args)
        if has_negative_exp:
            return "quotient"
        if len(input.args) > 1:
            return "product"
    elif input.is_Pow:
        base, exp = input.args
        if not (base.is_Symbol or base.is_Number) and chain_flag:
            return "chain"
        return "power"
    elif input.is_Function:
        arg = input.args[0]
        if arg.is_Function or not (arg.is_Symbol or arg.is_Number) and chain_flag:
            return "chain"
        return input.func.__name__
    elif input.is_Number:
        return "constant"
    elif input.is_Symbol:
        return "power_1"
    return "unknown"

def quotient_extract_u_v(expression):
    if isinstance(expression, str):
        expr = latex2sympy(expression)
    else:
        expr = expression
    if isinstance(expr, sp.Mul):
        for term in expr.args:
            if isinstance(term, sp.Pow) and term.exp.is_Number and term.exp == -1:
                v = term.base
                u_terms = [t for t in expr.args if t != term]  
                u = sp.Mul(*u_terms) if u_terms else 1                
                return u, v
    elif isinstance(expr, sp.Pow) and expr.exp.is_Number and expr.exp < 0:
        return 1, expr.base
    if hasattr(expr, 'args') and len(expr.args) == 2:
        return expr.args[0], expr.args[1]
    return None, None

def product_extract_u_v(expression):
    if isinstance(expression, str):
        expr = latex2sympy(expression)
    else:
        expr = expression
    if isinstance(expr, sp.Mul):
        terms = expr.args
        if len(terms) >= 2:
            u = terms[0]
            v = sp.Mul(*terms[1:])
            return u, v
    return None, None

def sumdiff_extract_u_v(expression):
    if isinstance(expression, str):
        expr = latex2sympy(expression)
    else:
        expr = expression
    if isinstance(expr, sp.Add):
        args = expr.args
        if len(args) >= 2:
            u = args[0]
            v = sp.Add(*args[1:])
            return u, v
    return None, None

def chain_extract_u_v(expression):
    if isinstance(expression, str):
        expr = latex2sympy(expression)
    else:
        expr = expression
    if isinstance(expr, sp.Pow):
        outer = expr
        inner = expr.base
        return outer, inner
    elif isinstance(expr, sp.Function):
        outer = expr
        inner = expr.args[0]
        return outer, inner

    return None, None

def format_latex_expr(expr):
    latex_expr = sp.latex(expr)
    return latex_expr

def generate_steps(expr, var, current_depth=0, max_depth=2):
    steps = []
    step_number = 1
    if current_depth >= max_depth:
        derivative = calculate_derivative(expr, var)
        steps.append({
            "number": step_number,
            "text": f"Computing the derivative directly:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{format_latex_expr(expr)}] = {format_latex_expr(derivative)}"
        })
        return steps
    expr_type = classify_differentiation(expr)
    expr_latex = format_latex_expr(expr)
    steps.append({
        "number": step_number,
        "text": f"To find the derivative of ${expr_latex}$, we need to identify what rule to use.",
        "math": f"\\frac{{d}}{{d{str(var)}}}[{expr_latex}"
    })
    step_number += 1
    if expr_type == "power_1" and expr == x:
        steps.append({
            "number": step_number,
            "text": f"This is just ${var}$, so the derivative is $1$.",
            "math": f"\\frac{{d}}{{d{var}}}({var}) = 1"
        })
        return steps
    elif expr_type == "constant" or (expr_type == "power_1" and expr != x):
        const_latex = format_latex_expr(expr)
        steps.append({
            "number": step_number,
            "text": f"This is a constant with respect to ${var}$, so the derivative is 0.",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{const_latex}] = 0"
        })
        return steps
    if expr_type == "quotient":
        u, v = quotient_extract_u_v(expr)
        u_latex = format_latex_expr(u)
        v_latex = format_latex_expr(v)
        steps.append({
            "number": step_number,
            "text": f"This is a quotient of the form $\\frac{{f(x)}}{{g(x)}}$, so we'll use the quotient rule: $\\frac{{d}}{{dx}}[\\frac{{f(x)}}{{g(x)}}] = \\frac{{g(x) \\cdot f'(x) - f(x) \\cdot g'(x)}}{{g(x)^{{2}}}}$",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[\\frac{{{u_latex}}}{{{v_latex}}}\\right] = \\frac{{{v_latex} \\cdot \\frac{{d}}{{dx}}({u_latex}) - {u_latex} \\cdot \\frac{{d}}{{dx}}({v_latex})}}{{({v_latex})^2}}"
        })
        step_number += 1
        f_prime = calculate_derivative(u, var)
        g_prime = calculate_derivative(v, var)
        f_prime_latex = format_latex_expr(f_prime)
        g_prime_latex = format_latex_expr(g_prime)
        if current_depth < max_depth - 1:
            steps.append({
                "number": step_number,
                "text": "Let's find the derivative of the numerator:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}]"
            })
            step_number += 1
            numerator_steps = generate_steps(u, var, current_depth + 1, max_depth)
            if numerator_steps:
                last_step = numerator_steps[-1]
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the numerator is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}"
                })
                step_number += 1
            steps.append({
                "number": step_number,
                "text": "Now let's find the derivative of the denominator:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}]"
            })
            step_number += 1
            denominator_steps = generate_steps(v, var, current_depth + 1, max_depth)
            if denominator_steps:
                last_step = denominator_steps[-1]
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the denominator is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
                })
                step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": f"The derivatives of the numerator and denominator are:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}, \\quad \\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
            })
            step_number += 1
        steps.append({
            "number": step_number,
            "text": "Now substitute these derivatives into the quotient rule formula $\\frac{{d}}{{dx}}[\\frac{{f(x)}}{{g(x)}}] = \\frac{{g(x) \\cdot f'(x) - f(x) \\cdot g'(x)}}{{g(x)^{{2}}}}$:",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[\\frac{{{u_latex}}}{{{v_latex}}}\\right] = \\frac{{{v_latex} \\cdot ({f_prime_latex}) - {u_latex} \\cdot ({g_prime_latex})}}{{({v_latex})^2}}"
        })
        step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "The final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[\\frac{{{u_latex}}}{{{v_latex}}}\\right] = {final_derivative_latex}"
        })
    elif expr_type == "product":
        u, v = product_extract_u_v(expr)
        u_latex = format_latex_expr(u)
        v_latex = format_latex_expr(v)
        steps.append({
            "number": step_number,
            "text": f"This is a product of the form $f(x) \\cdot g(x)$, so we'll use the product rule: $\\frac{{d}}{{dx}}[f(x) \\cdot g(x)] = f(x) \\cdot g'(x) + g(x) \\cdot f'(x)$",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} \\cdot {v_latex}] = {u_latex} \\cdot \\frac{{d}}{{d{str(var)}}}[{v_latex}] + {v_latex} \\cdot \\frac{{d}}{{d{str(var)}}}[{u_latex}]"
        })
        step_number += 1
        f_prime = calculate_derivative(u, var)
        g_prime = calculate_derivative(v, var)
        f_prime_latex = format_latex_expr(f_prime)
        g_prime_latex = format_latex_expr(g_prime)
        if current_depth < max_depth - 1:
            steps.append({
                "number": step_number,
                "text": "Let's find the derivative of the first factor:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}]"
            })
            step_number += 1
            first_factor_steps = generate_steps(u, var, current_depth + 1, max_depth)
            steps.append({
                "number": step_number,
                "text": f"The derivative of the first factor is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}"
            })
            step_number += 1
            steps.append({
                "number": step_number,
                "text": "Now let's find the derivative of the second factor:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}]"
            })
            step_number += 1
            second_factor_steps = generate_steps(v, var, current_depth + 1, max_depth)
            steps.append({
                "number": step_number,
                "text": f"The derivative of the second factor is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
            })
            step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": f"The derivatives of the factors are:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}, \\quad \\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
            })
            step_number += 1
        steps.append({
            "number": step_number,
            "text": "Now substitute these derivatives into the product rule formula:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} \\cdot {v_latex}] = {u_latex} \\cdot ({g_prime_latex}) + {v_latex} \\cdot ({f_prime_latex})"
        })
        step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "The final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} \\cdot {v_latex}] = {final_derivative_latex}"
        })
    elif expr_type in ["sum", "difference"]:
        u, v = sumdiff_extract_u_v(expr)
        u_latex = format_latex_expr(u)
        v_latex = format_latex_expr(v)
        operation = "+" if expr_type == "sum" else "-"
        rule_name = "sum" if expr_type == "sum" else "difference"
        steps.append({
            "number": step_number,
            "text": f"This is a ${rule_name}$ of the form $f(x) {operation} g(x)$, so we'll use the ${rule_name}$ rule: $\\frac{{d}}{{dx}}[f(x) {operation} g(x)] = f'(x) {operation} g'(x)$",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} {operation} {v_latex}] = \\frac{{d}}{{d{str(var)}}}[{u_latex}] {operation} \\frac{{d}}{{d{str(var)}}}[{v_latex}]"
        })
        step_number += 1
        f_prime = calculate_derivative(u, var)
        g_prime = calculate_derivative(v, var)
        f_prime_latex = format_latex_expr(f_prime)
        g_prime_latex = format_latex_expr(g_prime)
        if current_depth < max_depth - 1:
            steps.append({
                "number": step_number,
                "text": "Let's differentiate the first part:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}]"
            })
            step_number += 1
            u_steps = generate_steps(u, var, current_depth + 1, max_depth)
            if u_steps:
                last_step = u_steps[-1]
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the first part is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}"
                })
                step_number += 1
            steps.append({
                "number": step_number,
                "text": "Now differentiate the second part:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}]"
            })
            step_number += 1
            v_steps = generate_steps(v, var, current_depth + 1, max_depth)
            if v_steps:
                last_step = v_steps[-1]
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the second part is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
                })
                step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": f"The derivatives of the parts are:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex}] = {f_prime_latex}, \\quad \\frac{{d}}{{d{str(var)}}}[{v_latex}] = {g_prime_latex}"
            })
            step_number += 1
        steps.append({
            "number": step_number,
            "text": "Now substitute these into the rule:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} {operation} {v_latex}] = {f_prime_latex} {operation} {g_prime_latex}"
        })
        step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "The final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{u_latex} {operation} {v_latex}] = {final_derivative_latex}"
        })
    elif expr_type == "chain":
        outer, inner = chain_extract_u_v(expr)
        outer_latex = format_latex_expr(outer)
        inner_latex = format_latex_expr(inner)
        if isinstance(expr, sp.Pow):
            base = expr.base
            exponent = expr.exp
            base_latex = format_latex_expr(base)
            steps.append({
                "number": step_number,
                "text": f"This is a composite function of the form $g(x)^{exponent}$, so we'll use the chain rule with power rule $\\frac{{d}}{{dx}}[(f(x))^{{n}}] = n(f(x))^{{n-1}} \\cdot f'(x)$:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[({base_latex})^{{{exponent}}}] = {exponent} \\cdot ({base_latex})^{{{exponent-1}}} \\cdot \\frac{{d}}{{d{str(var)}}}[{base_latex}]"
            })
            step_number += 1
            g_prime = calculate_derivative(base, var)
            g_prime_latex = format_latex_expr(g_prime)
            if current_depth < max_depth - 1:
                steps.append({
                    "number": step_number,
                    "text": "Let's find the derivative of the inner function:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{base_latex}]"
                })
                step_number += 1
                inner_steps = generate_steps(base, var, current_depth + 1, max_depth)
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the inner function is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{base_latex}] = {g_prime_latex}"
                })
                step_number += 1
            else:
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of the inner function is:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{base_latex}] = {g_prime_latex}"
                })
                step_number += 1
            steps.append({
                "number": step_number,
                "text": "Now substitute this derivative into the chain rule with power rule formula $\\frac{{d}}{{dx}}[(f(x))^{{n}}] = n(f(x))^{{n-1}} \\cdot f'(x)$:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[({base_latex})^{{{exponent}}}] = {exponent} \\cdot ({base_latex})^{{{exponent-1}}} \\cdot ({g_prime_latex})"
            })
            step_number += 1
            final_derivative = calculate_derivative(expr, var)
            final_derivative_latex = format_latex_expr(final_derivative)
            steps.append({
                "number": step_number,
                "text": "The final derivative is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[({base_latex})^{{{exponent}}}] = {final_derivative_latex}"
            })
        elif isinstance(outer, sp.Function):
            function_name = outer.func.__name__
            steps.append({
                "number": step_number,
                "text": f"This is a composite function of the form ${function_name}(g(x))$, so we'll use the chain rule $\\frac{{d}}{{dx}}[f(g(x))] = f'(g(x)) \\cdot g'(x)$:",
                "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right] = f'\\left({inner_latex}\\right) \\cdot \\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right]"
            })
            step_number += 1
            
            if function_name == "cos":
                outer_derivative = f"-\\sin\\left({inner_latex}\\right)"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\cos(u)$ is $-\\sin(u)$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "sin":
                outer_derivative = f"\\cos\\left({inner_latex}\\right)"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\sin(u)$ is $\\cos(u)$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "tan":
                outer_derivative = f"\\sec^2\\left({inner_latex}\\right)"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\tan(u)$ is $\\sec^2(u)$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "exp":
                outer_derivative = f"\\exp\\left({inner_latex}\\right)"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\exp(u)$ is $\\exp(u)$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "log":
                outer_derivative = f"\\frac{{1}}{{{inner_latex}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\log(u)$ is $\\frac{{1}}{{u}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "sqrt":
                outer_derivative = f"\\frac{{1}}{{2\\sqrt{{{inner_latex}}}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\sqrt{{u}}$ is $\\frac{{1}}{{2\\sqrt{{u}}}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "ln":
                outer_derivative = f"\\frac{{1}}{{{inner_latex}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\ln(u)$ is $\\frac{{1}}{{u}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "atan":
                outer_derivative = f"\\frac{{1}}{{1+{inner_latex}^{{2}}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\operatorname{{atan}}(u)$ is $\\frac{{1}}{{1+u^{{2}}}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "asin":
                outer_derivative = f"\\frac{{1}}{{\\sqrt{{1-{inner_latex}^2}}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\operatorname{{asin}}(u)$ is $\\frac{{1}}{{\\sqrt{{1-u^{{2}}}}}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            elif function_name == "acos":
                outer_derivative = f"-\\frac{{1}}{{\\sqrt{{1-{inner_latex}^2}}}}"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\operatorname{{acos}}(u)$ is $-\\frac{{1}}{{\\sqrt{{1-u^{{2}}}}}}$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            else:
                outer_derivative = f"f'\\left({inner_latex}\\right)"
                steps.append({
                    "number": step_number,
                    "text": f"The derivative of $\\{function_name}(u)$ is $\\{function_name}'(u)$:",
                    "math": f"f'\\left({inner_latex}\\right) = {outer_derivative}"
                })
            step_number += 1
            
            inner_derivative = calculate_derivative(inner, var)
            inner_derivative_latex = format_latex_expr(inner_derivative)
            steps.append({
                "number": step_number,
                "text": f"The derivative of the inner function is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{inner_latex}\\right] = {inner_derivative_latex}"
            })
            step_number += 1
            
            final_derivative = calculate_derivative(expr, var)
            final_derivative_latex = format_latex_expr(final_derivative)
            steps.append({
                "number": step_number,
                "text": "The final derivative by the chain rule is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right] = {final_derivative_latex}"
            })
        else:
            final_derivative = calculate_derivative(expr, var)
            final_derivative_latex = format_latex_expr(final_derivative)
            steps.append({
                "number": step_number,
                "text": f"This is a composite function, so we apply the chain rule: $\\frac{{d}}{{dx}}[f(g(x))] = f'(g(x)) \\cdot g'(x)$:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{expr_latex}] = {final_derivative_latex}"
            })
    elif expr_type == "power":
        if isinstance(expr, sp.Pow):
            base = expr.args[0]  
            exponent = expr.args[1]
            base_latex = format_latex_expr(base)
            if base.is_Symbol and (base == x or base == y or base == z):
                steps.append({
                    "number": step_number,
                    "text": f"This is a power function of the form ${str(var)}^{exponent}$, so we'll use the power rule $\\frac{{d}}{{dx}}[x^{{n}}] = n \\cdot x^{{(n-1)}}$:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{base_latex}^{{{exponent}}}] = {exponent} \\cdot {base_latex}^{{{exponent-1}}}"
                })
                step_number += 1
                final_derivative = calculate_derivative(expr, var)
                final_derivative_latex = format_latex_expr(final_derivative)
                steps.append({
                    "number": step_number, 
                    "text": "The final derivative is:", 
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{base_latex}^{{{exponent}}}] = {final_derivative_latex}"
                })
            else:
                final_derivative = calculate_derivative(expr, var)
                final_derivative_latex = format_latex_expr(final_derivative)
                steps.append({
                    "number": step_number,
                    "text": f"For this power expression with a non-${str(var)}$ base, we need a combination of power rule and chain rule:",
                    "math": f"\\frac{{d}}{{d{str(var)}}}[{expr_latex}] = {final_derivative_latex}"
                })
    elif expr_type in ["sin", "cos", "tan", "csc", "sec", "cot"]:
        outer, inner = chain_extract_u_v(expr)
        outer_latex = format_latex_expr(outer)
        inner_latex = format_latex_expr(inner)
        rule = "trig rule"
        if outer.func.__name__ == "sin":
            rule = "\\frac{{d}}{{dx}}(sin(x)) = cos(x)"
        elif outer.func.__name__ == "cos":
            rule = "\\frac{{d}}{{dx}}(cos(x)) = -sin(x)"
        elif outer.func.__name__ == "tan":
            rule = "\\frac{{d}}{{dx}}(tan(x)) = sec^{{2}}(x)"
        elif outer.func.__name__ == "csc":
            rule = "\\frac{{d}}{{dx}}(csc(x)) = -csc(x) \\cdot cot(x)"
        elif outer.func.__name__ == "sec":
            rule = "\\frac{{d}}{{dx}}(sec(x)) = sec(x) \\cdot tan(x)"
        elif outer.func.__name__ == "cot":
            rule = "\\frac{{d}}{{dx}}(cot(x)) = -csc^{{2}}(x)"
        steps.append({
            "number": step_number,
            "text": f"This is a trigonometric function ${outer.func.__name__}({str(var)})$. Its derivative follows standard rules ${rule}$:",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right] = \\text{{derivative of}}\\ {outer.func.__name__}({str(var)})\\ \\times\\ \\frac{{d}}{{d{str(var)}}}[{inner_latex}]"
        })
        step_number += 1
        outer_derivatives = {
            "sin": "cos",
            "cos": "-sin",
            "tan": "sec^2",
            "csc": "-csc(x)cot(x)",
            "sec": "sec(x)tan(x)",
            "cot": "-csc^2",
        }
        outer_derivative_text = outer_derivatives.get(outer.func.__name__, "unknown")
        steps.append({
            "number": step_number,
            "text": f"The derivative of ${outer.func.__name__}({str(var)})$ is ${outer_derivative_text}$.",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = {outer_derivative_text}({inner_latex}) \\times \\frac{{d}}{{d{str(var)}}}[{inner_latex}]"
        })
        step_number += 1
        inner_derivative = calculate_derivative(inner, var)
        inner_derivative_latex = format_latex_expr(inner_derivative)
        if current_depth < max_depth - 1:
            inner_steps = generate_steps(inner, var, current_depth + 1, max_depth)
            steps.append({
                "number": step_number,
                "text": "Now, find the derivative of the inside function:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": f"The derivative of the inside is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "Applying the chain rule, the final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = {final_derivative_latex}"
        })
    elif expr_type in ["asin", "acos", "atan", "acsc", "asec", "acot"]:
        outer, inner = chain_extract_u_v(expr)
        outer_latex = format_latex_expr(outer)
        inner_latex = format_latex_expr(inner)
        rule = "inverse trig rule"
        if outer.func.__name__ == "asin":
            rule = f"\\frac{{d}}{{dx}}[asin(x)] = \\frac{{1}}{{\\sqrt{{1-x^{{2}}}}}}"
        elif outer.func.__name__ == "acos":
            rule = f"\\frac{{d}}{{dx}}[acos(x)] = -\\frac{{1}}{{\\sqrt{{1-x^{{2}}}}}}"
        elif outer.func.__name__ == "atan":
            rule = f"\\frac{{d}}{{dx}}[atan(x)] = \\frac{{1}}{{1+x^{{2}}}}"
        elif outer.func.__name__ == "acsc":
            rule = f"\\frac{{d}}{{dx}}[acsc(x)] = -\\frac{{1}}{{|x|\\sqrt{{x^{{2}}-1}}}}"
        elif outer.func.__name__ == "asec":
            rule = f"\\frac{{d}}{{dx}}[asec(x)] = \\frac{{1}}{{|x|\\sqrt{{x^{{2}}-1}}}}"
        elif outer.func.__name__ == "acot":
            rule = f"\\frac{{d}}{{dx}}[acot(x)] = -\\frac{{1}}{{1+x^{{2}}}}"
        steps.append({
            "number": step_number,
            "text": f"This is an inverse trigonometric function $\\operatorname{{{outer.func.__name__}}}({str(var)})$. We'll differentiate using its standard rule ${rule}$:",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right] = \\text{{derivative of}}\\ {outer.func.__name__}({str(var)})\\ \\times\\ \\frac{{d}}{{d{str(var)}}}[{inner_latex}]"
        })
        step_number += 1
        inverse_trig_derivatives = {
            "asin": f"\\frac{{1}}{{\\sqrt{{1-x^{{2}}}}}}",
            "acos": f"-\\frac{{1}}{{\\sqrt{{1-x^{{2}}}}}}",
            "atan": f"\\frac{{1}}{{1+x^2}}",
            "acsc": f"-\\frac{{1}}{{|x|\\sqrt{{x^{{2}}-1}}}}",
            "asec": f"\\frac{{1}}{{|x|\\sqrt{{x^{{2}}-1}}}}",
            "acot": f"-\\frac{{1}}{{1+x^{{2}}}}",
        }
        outer_derivative_text = inverse_trig_derivatives.get(outer.func.__name__, "unknown")
        steps.append({
            "number": step_number,
            "text": f"The derivative of $\\operatorname{{{outer.func.__name__}}}({str(var)})$ is ${outer_derivative_text}$.",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = {outer_derivative_text} \\times \\frac{{d}}{{d{str(var)}}}[{inner_latex}]"
        })
        step_number += 1
        inner_derivative = calculate_derivative(inner, var)
        inner_derivative_latex = format_latex_expr(inner_derivative)
        if current_depth < max_depth - 1:
            inner_steps = generate_steps(inner, var, current_depth + 1, max_depth)
            steps.append({
                "number": step_number,
                "text": "Now, differentiate the inside function:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": "The derivative of the inside function is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "Using the chain rule, the final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = {final_derivative_latex}"
        })
    elif expr_type == "log":
        outer, inner = chain_extract_u_v(expr)
        outer_latex = format_latex_expr(outer)
        inner_latex = format_latex_expr(inner)
        steps.append({
            "number": step_number,
            "text": f"This is a natural logarithm function $\\ln(x)$. We'll use the rule $\\frac{{d}}{{dx}}[ln(x)] = \\frac{{1}}{{x}}$:",
            "math": f"\\frac{{d}}{{d{str(var)}}}\\left[{outer_latex}\\right]"
        })
        step_number += 1
        steps.append({
            "number": step_number,
            "text": f"The derivative of $\\ln(x)$ is $\\frac{{1}}{{x}}$, so we apply the chain rule with the inside function:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = \\frac{{1}}{{{inner_latex}}} \\times \\frac{{d}}{{d{str(var)}}}[{inner_latex}]"
        })
        step_number += 1
        inner_derivative = calculate_derivative(inner, var)
        inner_derivative_latex = format_latex_expr(inner_derivative)
        if current_depth < max_depth - 1:
            inner_steps = generate_steps(inner, var, current_depth + 1, max_depth)
            steps.append({
                "number": step_number,
                "text": "Now, find the derivative of the inside function:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        else:
            steps.append({
                "number": step_number,
                "text": "The derivative of the inside function is:",
                "math": f"\\frac{{d}}{{d{str(var)}}}[{inner_latex}] = {inner_derivative_latex}"
            })
            step_number += 1
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": "Thus, the final derivative is:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{outer_latex}] = {final_derivative_latex}"
        })
    else:
        final_derivative = calculate_derivative(expr, var)
        final_derivative_latex = format_latex_expr(final_derivative)
        steps.append({
            "number": step_number,
            "text": f"Taking the derivative directly:",
            "math": f"\\frac{{d}}{{d{str(var)}}}[{expr_latex}] = {final_derivative_latex}"
        })
    return steps

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            request = json.loads(line)
            expression = request.get("expression", "")
            variable = request.get("variable", "")
            orderOfDerivative = request.get("orderOfDerivative", "")
            variable = sp.symbols(variable.replace("\\", ""))

            simplified = sp.simplify(latex2sympy(expression))
            steps = generate_steps(simplified, variable)
            result = sp.latex(calculate_derivative(simplified, variable))

            print(json.dumps({"simplified": sp.latex(simplified), "steps": steps, "result": result}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)