#!/usr/bin/env python3
"""Calculadora determinista para la auditoría humana de E2.

No emite dictámenes: recalcula el resultado esperado a partir de los datos del
prompt y comprueba cada igualdad aritmética / conversión que aparece en la
respuesta del modelo. Lee JSONL por stdin o por ruta; escribe Markdown.

Uso: python scripts/audit_calc.py archivo.jsonl [...] > hoja.md
"""
import ast
import json
import math
import operator
import re
import sys

PI = math.pi
# factor a SI de cada unidad
U = {
    "km": 1e3, "m": 1.0, "cm": 1e-2, "s": 1.0, "min": 60.0, "h": 3600.0,
    "kg": 1.0, "g": 1e-3, "m/s": 1.0, "km/h": 1 / 3.6, "km/s": 1e3,
    "m^3": 1.0, "L": 1e-3, "cm^3": 1e-6, "kg/m^3": 1.0, "g/cm^3": 1e3, "g/L": 1.0,
    "m^2": 1.0, "cm^2": 1e-4, "N": 1.0, "kN": 1e3, "Pa": 1.0, "kPa": 1e3,
    "J": 1.0, "kJ": 1e3, "W": 1.0, "erg/s": 1e-7, "W/m^2": 1.0, "erg/s/cm^2": 1e-3,
    "A": 1.0, "mA": 1e-3, "ohm": 1.0, "kohm": 1e3, "V": 1.0, "mV": 1e-3,
}
DIM = {  # dimensión, para comparar conversiones solo entre unidades compatibles
    "km": "L", "m": "L", "cm": "L", "s": "T", "min": "T", "h": "T", "kg": "M", "g": "M",
    "m/s": "v", "km/h": "v", "km/s": "v", "m^3": "V", "L": "V", "cm^3": "V", "kg/m^3": "rho",
    "g/cm^3": "rho", "g/L": "rho", "m^2": "A", "cm^2": "A", "N": "F", "kN": "F", "Pa": "P",
    "kPa": "P", "J": "E", "kJ": "E", "W": "Pw", "erg/s": "Pw", "W/m^2": "flux",
    "erg/s/cm^2": "flux", "A": "I", "mA": "I", "ohm": "R", "kohm": "R", "V": "U", "mV": "U",
}
UNIT_ALIASES = {"Ω": "ohm", "kΩ": "kohm", "ohmios": "ohm", "ohms": "ohm", "kohms": "kohm",
                "m²": "m^2", "m³": "m^3", "cm²": "cm^2", "cm³": "cm^3", "kg/m³": "kg/m^3",
                "g/cm³": "g/cm^3", "W/m²": "W/m^2", "erg/s/cm²": "erg/s/cm^2", "l": "L",
                "Pa": "Pa", "seg": "s", "segundos": "s", "minutos": "min", "metros": "m",
                "kilómetros": "km", "gramos": "g", "kilogramos": "kg", "litros": "L",
                "N/m^2": "Pa", "N/m²": "Pa", "kg·m/s^2": "N"}
ALL_UNITS = sorted(set(U) | set(UNIT_ALIASES), key=len, reverse=True)
UNIT_RE = "|".join(re.escape(u) for u in ALL_UNITS)


def canon(u):
    return UNIT_ALIASES.get(u, u)


# ---------- resultado esperado a partir del prompt ----------
def expected_from_prompt(r):
    p = r["prompt"]
    data = {}
    for name, val, unit in re.findall(r"(\w+)=([\d.eE+-]+) ([^;\n]+)", re.search(r"Datos: (.*)", p).group(1)):
        data[name] = float(val) * U[unit.strip()]
    s = lambda k: data[k] if k in data else data[k + "1"] + data[k + "2"]
    fam = r["family"]
    if fam == "speed":
        si = s("d") / data["t"]
    elif fam == "density":
        si = s("m") / data["V"]
    elif fam == "pressure":
        si = s("F") / data["A"]
    elif fam == "energy":
        si = s("m") * data["v"] ** 2 / 2
    elif fam == "voltage":
        si = data["I"] * s("R")
    elif fam == "luminosity":
        si = 4 * PI * data["d"] ** 2 * s("F")
    else:
        raise ValueError(fam)
    target = re.search(r"Expresa el resultado en (\S+?)\.\s", p).group(1)
    return data, si, target


def final_answer(c):
    m = re.findall(r'\{\s*"value"\s*:\s*([-\d.eE+]+)\s*,\s*"unit"\s*:\s*"([^"]*)"\s*\}', c)
    if m:
        return float(m[-1][0]), m[-1][1]
    m = re.findall(r"([-\d.]+(?:e[-+]?\d+)?)\s*(" + UNIT_RE + r")\b", c)
    return (float(m[-1][0]), m[-1][1]) if m else (None, None)


# ---------- comprobación de igualdades en la respuesta ----------
def normalize(c):
    t = c
    t = re.sub(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", lambda m: m[0].replace(",", ""), t)
    t = re.sub(r"\\text\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", t)
    for _ in range(3):
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", t)
    t = t.replace("\\left", "").replace("\\right", "")
    t = re.sub(r"\\(cdot|times)", "*", t)
    t = t.replace("×", "*").replace("·", "*").replace("÷", "/").replace("−", "-")
    t = re.sub(r"\\(approx|simeq)", "≈", t)
    t = re.sub(r"\\[,;! ]", " ", t)
    t = t.replace("\\pi", "π").replace("$", " ").replace("\\[", " ").replace("\\]", " ")
    t = t.replace("\\(", " ").replace("\\)", " ")
    t = t.replace("^{2}", "^2").replace("^{3}", "^3").replace("²", "^2").replace("³", "^3")
    t = re.sub(r"\^\{(-?\d+)\}", r"^\1", t)
    t = re.sub(r"(\d)\s*[x]\s*10\^", r"\1e", t)  # 3 x 10^4 -> 3e4 (aprox.)
    t = re.sub(r"\*\*", "^", t)
    t = t.replace("{", "(").replace("}", ")")
    return t


NUM = r"\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
TOKEN = re.compile(r"\s*(?:(" + NUM + r")|(" + UNIT_RE + r")(?![A-Za-z])|(π|pi)|([-+*/^()])|(=|≈))")


def chains(text):
    """Devuelve listas de lados [(expr_str, unit_or_None, raw)] separados por = o ≈."""
    # Una misma variable puede encadenar sus cálculos en líneas separadas.
    joined, previous = [], None
    for line in text.splitlines():
        assignment = re.match(r"\s*([A-Za-z]\w*)\s*([=≈])\s*(.+)", line)
        if assignment:
            symbol, operator, expression = assignment.groups()
            if symbol == previous:
                joined[-1] += f" {operator} {expression}"
            else:
                joined.append(line)
            previous = symbol
        elif line.strip():
            joined.append(line)
            previous = None
    text = "\n".join(joined)
    out = []
    for line in re.split(r"[\n;]|(?<=[a-z\)])\.\s|,\s(?=[A-Za-zÁÉÍÓÚáéíóú])", text):
        i = 0
        while i < len(line):
            if line[i].isspace():
                i += 1  # comprobar el contexto desde el propio token, no desde el espacio previo
                continue
            m = TOKEN.match(line, i)
            if (not m or not (m.group(1) or m.group(3) or m.group(4) == "(")
                    or (i > 0 and (line[i - 1].isalpha() or line[i - 1] in "_.^\\"))):
                i = m.end() if (m and m.group(1)) else i + 1  # no empezar en subíndices (m1, F_2)
                continue
            back = line[:i].rstrip()
            prev_op = back.rstrip("+-").rstrip()
            if back and (back[-1] in "*/^" or (back[-1] in "+-" and prev_op and (prev_op[-1].isalnum() or prev_op[-1] == ")"))):
                i = m.end()  # no empezar a mitad de una expresión con variables (v^2 / 2 = ...)
                continue
            sides, cur, j = [], [], i
            while True:
                m = TOKEN.match(line, j)
                if not m:
                    break
                if m.group(1) and m.start(1) > 0 and (line[m.start(1) - 1].isalpha() or line[m.start(1) - 1] == "_"):
                    break  # subíndice pegado a una variable: corta la cadena
                if m.group(5):
                    sides.append(cur)
                    cur = []
                else:
                    kind = "n" if m.group(1) else "u" if m.group(2) else "p" if m.group(3) else "o"
                    val = m.group(1) or m.group(2) or m.group(3) or m.group(4)
                    cur.append((kind, val))
                j = m.end()
            sides.append(cur)
            if len([s for s in sides if any(k in "np" for k, _ in s)]) >= 2:
                out.append((sides, line[i:j].strip()))
            i = max(j, i + 1)
    return out


def arithmetic(node):
    """Evalúa solo números y operadores aritméticos, sin ejecutar código."""
    operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                  ast.Div: operator.truediv, ast.Pow: operator.pow}
    if isinstance(node, ast.Expression):
        return arithmetic(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = arithmetic(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in operations:
        return operations[type(node.op)](arithmetic(node.left), arithmetic(node.right))
    raise ValueError("Solo se admiten números y operadores aritméticos")


def side_value(side):
    """Evalúa un lado. Devuelve (valor, unidad_si_es_cantidad_simple, es_expresion)."""
    toks = [(k, v) for k, v in side]
    while toks and toks[-1][0] == "o" and toks[-1][1] in "+-*/^(":
        toks.pop()
    while toks and toks[0][0] == "o" and toks[0][1] in "*/^)":
        toks.pop(0)
    nums = [t for t in toks if t[0] in "np"]
    units = [canon(v) for k, v in toks if k == "u"]
    if not nums:
        return None
    if len(nums) == 1 and len([t for t in toks if t[0] == "o" and t[1] in "+*/^"]) == 0:
        val = PI if nums[0][0] == "p" else float(nums[0][1])
        if toks and toks[0] == ("o", "-"):
            val = -val
        return val, (units[0] if units else None), False
    expr = ""
    prev = None
    for k, v in toks:
        if k == "u":
            continue
        piece = {"p": repr(PI)}.get(k, v)
        if piece == "^":
            piece = "**"
        if prev in ("n", "p", ")") and (k in "np" or v == "("):
            expr += "*"  # multiplicación implícita
        expr += piece
        prev = ")" if v == ")" else k
    expr = expr.strip()
    bal = expr.count("(") - expr.count(")")
    if bal > 0:
        expr += ")" * bal
    elif bal < 0:
        expr = "(" * -bal + expr
    try:
        return float(arithmetic(ast.parse(expr, mode="eval"))), None, True
    except (SyntaxError, ValueError, TypeError, ArithmeticError, RecursionError):
        return None


def digits_tol(raw_side):
    """Tolerancia de redondeo según los decimales mostrados en el lado derecho."""
    nums = [v for k, v in raw_side if k == "n"]
    if len(nums) != 1:
        return 0
    n = nums[0]
    if "e" in n.lower():
        mant, exp = n.lower().split("e")
        dec = len(mant.split(".")[1]) if "." in mant else 0
        return 0.5 * 10 ** (int(exp) - dec)
    dec = len(n.split(".")[1]) if "." in n else 0
    return 0.5 * 10 ** (-dec)


def is_trunc(exact, written, half_step):
    """True si `written` es `exact` truncado hacia cero en los decimales mostrados."""
    if not half_step:
        return False
    step = 2 * half_step
    t = math.trunc(exact / step + 1e-9 * (1 if exact >= 0 else -1)) * step
    return abs(t - written) <= 1e-6 * step


def check_equalities(c):
    rows = []
    for sides, raw in chains(normalize(c)):
        vals = [side_value(s) for s in sides]
        pending_q = None  # cantidad con unidad seguida de una expresión sin unidad
        for a in range(len(sides) - 1):
            L, R = vals[a], vals[a + 1]
            if L is None or R is None:
                continue
            (lv, lu, lex), (rv, ru, rex) = L, R
            if not lex and lu and rex:
                pending_q = (lv, lu, a)  # "7.2 km/h = 7.2 / 3.6 = 2 m/s": conversión en varios pasos
                continue
            if pending_q and not rex and ru and ru != pending_q[1] and DIM.get(ru) == DIM.get(pending_q[1]):
                qv, qu, qa = pending_q
                pending_q = None
                a_lv, a_rv = qv * U[qu], rv * U[ru]
                tol = max(1e-9 * abs(a_lv), digits_tol(sides[a + 1]) * U[ru])
                d = abs(a_lv - a_rv); rr = d / abs(a_lv) if a_lv else 0
                flag = "OK" if d <= tol * 1.0001 else "DESVIO" if rr <= 5e-3 else "ERROR"
                rows.append((flag, f"conversión {qu}→{ru}", f"{side_text(sides[qa])} → {side_text(sides[a + 1])}", a_lv, a_rv, rr))
            if not lex and not rex and lu and ru and lu != ru:
                if DIM.get(lu) and DIM.get(lu) == DIM.get(ru):
                    lv, rv = lv * U[lu], rv * U[ru]
                    kind = f"conversión {lu}→{ru}"
                else:
                    continue
            elif not lex and not rex:
                if ((lu == ru or lu is None or ru is None)
                        and abs(lv - rv) <= 1e-12 * max(1, abs(lv))):
                    continue  # identidad trivial (p. ej. repetir un dato)
                kind = "igualdad"
            else:
                kind = "operación"
            # tolerancia: redondeo según decimales mostrados en el lado derecho
            if kind.startswith("conversión"):
                tol = max(1e-9 * abs(lv), digits_tol(sides[a + 1]) * U[ru])
            else:
                tol = max(1e-9 * abs(lv), digits_tol(sides[a + 1]), digits_tol(sides[a]))
            diff = abs(lv - rv)
            rel = diff / abs(lv) if lv else (0 if diff == 0 else math.inf)
            if diff <= tol * 1.0001:
                flag = "OK"
            elif is_trunc(lv, rv, digits_tol(sides[a + 1])):
                flag = "TRUNC"  # truncamiento exacto (hacia cero) en los decimales mostrados
            elif rel <= 5e-3:
                flag = "DESVIO"
            else:
                flag = "ERROR"
            rows.append((flag, kind, f"{side_text(sides[a])} = {side_text(sides[a + 1])}", lv, rv, rel))
    return rows


def side_text(side):
    return " ".join(v for _, v in side).replace("( ", "(").replace(" )", ")")


def fmt(x):
    return "—" if x is None else f"{x:.10g}"


def report(path_label, rows):
    out = [f"# Hoja de cálculo · `{path_label}`\n",
           ("Generada por una calculadora determinista. **No es un dictamen**: "
            "el auditor debe leer los pasos y decidir `keep`/`reject`/`uncertain`.\n"),
           ("Banderas: `OK` coincide dentro del redondeo de los decimales mostrados · "
           "`DESVÍO` difiere más que ese redondeo pero <0.5 % (decidir si es un truncamiento "
           "coherente de un valor intermedio o una operación mal hecha) · `ERROR` difiere ≥0.5 %. "
           "El analizador puede pasar por alto pasos en prosa o malinterpretar alguno: "
           "ante la duda, recalcula a mano.\n")]
    summary = []
    for idx, r in enumerate(rows, 1):
        data, si, target = expected_from_prompt(r)
        exp_t = si / U[target]
        ref_t = r["reference_si"] / U[target]
        ref_ok = abs(si - r["reference_si"]) <= 1e-9 * abs(si)
        val, unit = final_answer(r["completion"])
        unit_c = canon(unit) if unit else None
        rel = abs(val - exp_t) / abs(exp_t) if val is not None else None
        eq = check_equalities(r["completion"])
        n_err = sum(1 for e in eq if e[0] == "ERROR")
        n_round = sum(1 for e in eq if e[0] == "DESVIO")
        unit_flag = "" if unit_c == target else f" ⚠️ unidad final `{unit}` ≠ `{target}`"
        summary.append((idx, r["family"], r["level"], rel, n_err, n_round, unit_c != target))
        out.append(f"\n---\n\n## {idx}. {r['family']} · {r['level']} · `{r['candidate_id']}`\n")
        out.append("**Prompt**\n\n```\n" + r["prompt"] + "\n```\n")
        out.append("**Datos en SI:** " + ", ".join(f"{k}={v:.10g}" for k, v in data.items()))
        out.append(f"\n**Esperado:** {fmt(exp_t)} {target}"
                   + ("" if ref_ok else f" ⚠️ difiere de reference_si convertido ({fmt(ref_t)})"))
        out.append(f"\n**Respuesta final del modelo:** {fmt(val)} {unit or ''}"
                   + (f" · error relativo {rel*100:.4f} %" if rel is not None else "") + unit_flag + "\n")
        if eq:
            out.append("| bandera | tipo | fragmento | lado izq. | lado der. | dif. rel. |\n|---|---|---|---:|---:|---:|")
            for flag, kind, raw, lv, rv, rr in eq:
                frag = raw.replace("|", "\\|")
                frag = frag if len(frag) <= 90 else frag[:87] + "…"
                badge = {"OK": "OK", "TRUNC": "≈ trunc.", "DESVIO": "⚠️ DESVÍO", "ERROR": "❌ ERROR"}[flag]
                out.append(f"| {badge} | {kind} | `{frag}` | {fmt(lv)} | {fmt(rv)} | {rr*100:.3f} % |")
        else:
            out.append("_No se detectaron igualdades numéricas: revisar a mano._")
        out.append("\n**Respuesta del modelo**\n\n```\n" + r["completion"] + "\n```\n")
        out.append("**Tu dictamen:** keep / reject / uncertain — motivo: …\n")
    head = ["\n## Resumen\n", "| # | familia | nivel | err. final | ERROR | DESVÍO | unidad |",
            "|---:|---|---|---:|---:|---:|---|"]
    for idx, fam, lvl, rel, ne, nr, ub in summary:
        head.append(f"| {idx} | {fam} | {lvl} | {'—' if rel is None else f'{rel*100:.3f} %'} | "
                    f"{ne or ''} | {nr or ''} | {'⚠️' if ub else ''} |")
    return "\n".join(out[:3] + head + out[3:]) + "\n"


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as source:
            rows = [json.loads(line) for line in source if line.strip()]
        sys.stdout.write(report(path.split("/")[-1], rows))
