#!/usr/bin/env python3
"""Interfaz local de revisión humana para los JSONL de audits/reviewed/.

Solo escribe reviewer_type, judgment y reason de la línea indicada; verifica
que el resto del registro quede idéntico y reescribe el archivo de forma atómica.

Uso: python scripts/audit_review_server.py grpo hybrid [--root RUTA_REPO]
Abre la URL que imprime (puerto 8765 o el siguiente libre).
"""
import argparse
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import audit_calc as calc

_args = argparse.ArgumentParser(description="Interfaz local de auditoría humana E2")
_args.add_argument("names", nargs="+", help="prefijos de reviewed/, p. ej. grpo hybrid")
_args.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
_opts = _args.parse_args()
ROOT = _opts.root.resolve()
NAMES = _opts.names
DIR = ROOT / "data/units/project-e2/audits/reviewed"
FILES = {n: DIR / f"{n}-human-reviewed.jsonl" for n in NAMES}
_missing = [str(f) for f in FILES.values() if not f.exists()]
if _missing:
    sys.exit("No encuentro: " + ", ".join(_missing) + "\nPasa la ruta del repo como primer argumento.")
EDITABLE = ("reviewer_type", "judgment", "reason")
JUDGMENTS = ("keep", "reject", "uncertain")


def load(name):
    text = FILES[name].read_text(encoding="utf-8")
    lines = text.split("\n")
    assert lines[-1] == "", "se esperaba salto de línea final"
    return lines[:-1]


def analysis(r):
    data, si, target = calc.expected_from_prompt(r)
    exp_t = si / calc.U[target]
    val, unit = calc.final_answer(r["completion"])
    rel = abs(val - exp_t) / abs(exp_t) if val is not None else None
    return {
        "data_si": {k: v for k, v in data.items()},
        "expected": exp_t, "target": target,
        "ref_ok": abs(si - r["reference_si"]) <= 1e-9 * abs(si),
        "final": val, "final_unit": unit, "rel": rel,
        "unit_ok": (calc.canon(unit) if unit else None) == target,
        "checks": [{"flag": f, "kind": k, "frag": fr, "l": l, "r": rr, "rel": rel_}
                   for f, k, fr, l, rr, rel_ in calc.check_equalities(r["completion"])],
    }


def cases():
    out = []
    for name in NAMES:
        for i, line in enumerate(load(name)):
            r = json.loads(line)
            out.append({"file": name, "idx": i, "candidate_id": r["candidate_id"],
                        "task_id": r["task_id"], "family": r["family"], "level": r["level"],
                        "prompt": r["prompt"], "completion": r["completion"],
                        "auditor": r["auditor"], "reviewer_type": r["reviewer_type"],
                        "judgment": r["judgment"], "reason": r["reason"], "calc": analysis(r)})
    return out


def save(body):
    name, idx, cid = body["file"], int(body["idx"]), body["candidate_id"]
    judgment, reason = body.get("judgment"), (body.get("reason") or "").strip()
    clear = judgment is None
    if not clear:
        if judgment not in JUDGMENTS:
            raise ValueError("judgment inválido")
        if not reason:
            raise ValueError("el motivo es obligatorio")
    lines = load(name)
    old = json.loads(lines[idx])
    if old["candidate_id"] != cid:
        raise ValueError("candidate_id no coincide con la línea")
    new = dict(old)
    new.update({"reviewer_type": None, "judgment": None, "reason": None} if clear else
               {"reviewer_type": "human", "judgment": judgment, "reason": reason})
    # invariante: solo cambian los campos editables y el orden de claves se conserva
    assert list(new) == list(old)
    assert all(new[k] == old[k] for k in old if k not in EDITABLE)
    lines[idx] = json.dumps(new, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(dir=DIR, prefix=".tmp-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    os.replace(tmp, FILES[name])
    return {k: new[k] for k in EDITABLE}


class H(BaseHTTPRequestHandler):
    def _send(self, code, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, (Path(__file__).parent / "audit_review_ui.html").read_bytes(), "text/html")
        elif self.path == "/api/cases":
            self._send(200, cases())
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/save":
            return self._send(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self._send(200, save(body))
        except Exception as e:  # noqa: BLE001
            self._send(400, {"error": str(e)})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    for p in range(port, port + 50):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", p), H)
            break
        except OSError:
            continue
    else:
        sys.exit("No hay puertos libres")
    print(f"Revisión en http://127.0.0.1:{p}  ({', '.join(str(f) for f in FILES.values())})", flush=True)
    srv.serve_forever()
