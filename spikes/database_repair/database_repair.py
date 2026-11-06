"""Reparación inequívoca con catálogo inmutable y parches de celdas."""

import copy
import json
import multiprocessing
import random
import re
import sqlite3
import time
from contextlib import closing

SCHEMA = "CREATE TABLE products(id INTEGER PRIMARY KEY, sku TEXT UNIQUE, price INTEGER); CREATE TABLE orders(id INTEGER PRIMARY KEY, total INTEGER); CREATE TABLE lines(id INTEGER PRIMARY KEY, order_id INTEGER, sku TEXT, units INTEGER, product_id INTEGER, unit_price INTEGER, amount INTEGER);"
LIMITS = {
    "calls": 4,
    "queries": 3,
    "rows": 40,
    "output_tokens": 4096,
    "tokens_per_call": 1024,
    "context": 4096,
}


def parse(text):
    text = text.strip()
    all_blocks = re.findall(r"```([^\n]*)\n([\s\S]*?)```", text)
    blocks = [
        body
        for language, body in all_blocks
        if language.strip().lower() in ("", "json")
    ]
    if blocks:
        if len({b.strip() for b in blocks}) != 1:
            raise ValueError("ambiguous JSON")
        outside = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text)
        if re.search(
            "^\\s*(?:[-*]\\s*)?(?:(?:otra respuesta|alternativa|respuesta(?: final)?|horario(?: final| alternativo)?|plan(?: final| alternativo)?|o)\\s*:?\\s*)?`?\\s*[\\[{]",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            raise ValueError("additional structured output")
        text = blocks[0].strip()

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(value)

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except RecursionError as error:
        raise ValueError("JSON nesting limit") from error


def _worker(connection, data, sql):
    try:
        result = _execute(data, sql)
        if len(json.dumps(result).encode()) > 64_000:
            result = {"error": "result_limit"}
        connection.send(result)
    finally:
        connection.close()


def query(data, sql):
    """Watchdog de pared: también limita funciones nativas y compilación SQLite."""
    context = multiprocessing.get_context("fork")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(sender, data, sql))
    process.start()
    sender.close()
    try:
        if not receiver.poll(0.2):
            return {"error": "timeout"}
        try:
            return receiver.recv()
        except EOFError:
            return {"error": "query_worker"}
    finally:
        receiver.close()
        process.join(timeout=0.02)
        if process.is_alive():
            process.kill()
            process.join()


def _execute(data, sql):
    if not isinstance(sql, str) or len(sql) > 6000:
        return {"error": "query_limit"}
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.executescript(SCHEMA)
        connection.executemany("INSERT INTO products VALUES(?,?,?)", data["products"])
        connection.executemany("INSERT INTO orders VALUES(?,?)", data["orders"])
        connection.executemany("INSERT INTO lines VALUES(?,?,?,?,?,?,?)", data["lines"])
        connection.commit()
        connection.execute("PRAGMA query_only=ON")
        connection.enable_load_extension(False)
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 50_000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 6000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 40)

        def authorizer(action, arg1, arg2, db, trigger):
            if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
                return sqlite3.SQLITE_OK
            if (
                action == sqlite3.SQLITE_READ
                and db == "main"
                and arg1 in {"products", "orders", "lines"}
            ):
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and arg2 in {
                "count",
                "sum",
                "coalesce",
                "min",
                "max",
                "abs",
            }:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        started, steps = time.monotonic(), 0

        def progress():
            nonlocal steps
            steps += 100
            return int(steps > 50_000 or time.monotonic() - started > 0.1)

        connection.set_authorizer(authorizer)
        connection.set_progress_handler(progress, 100)
        try:
            cursor = connection.execute(sql)
            rows = cursor.fetchmany(LIMITS["rows"] + 1)
            if len(rows) > LIMITS["rows"]:
                return {"error": "row_limit"}
            return {"columns": [c[0] for c in cursor.description], "rows": rows}
        except sqlite3.Error as error:
            return {
                "error": "timeout" if "interrupted" in str(error) else "query",
                "message": str(error),
            }


def expected(data):
    """Derivar todo desde columnas inmutables; no confiar en valores corruptos."""
    result = copy.deepcopy(data)
    catalog = {p[1]: p for p in data["products"]}
    totals = dict.fromkeys((o[0] for o in data["orders"]), 0)
    for line in result["lines"]:
        product = catalog[line[2]]
        line[4], line[5], line[6] = product[0], product[2], product[2] * line[3]
        totals[line[1]] += line[6]
    for order in result["orders"]:
        order[1] = totals[order[0]]
    return result


def patch_status(task, patch):
    if not isinstance(patch, list):
        return "protocol"
    data = copy.deepcopy(task["data"])
    canonical = expected(data)
    columns = {
        "lines": {"product_id": 4, "unit_price": 5, "amount": 6},
        "orders": {"total": 1},
    }
    seen = set()
    for operation in patch:
        if not isinstance(operation, dict) or set(operation) != {
            "table",
            "id",
            "column",
            "value",
        }:
            return "protocol"
        table, key, column, value = (
            operation[k] for k in ("table", "id", "column", "value")
        )
        if (
            not isinstance(table, str)
            or not isinstance(column, str)
            or type(key) is not int
            or type(value) is not int
        ):
            return "protocol"
        if table not in columns or column not in columns[table]:
            return "unauthorized"
        cell = table, key, column
        if cell in seen:
            return "duplicate"
        seen.add(cell)
        row = next((r for r in data[table] if r[0] == key), None)
        if row is None:
            return "unknown_id"
        position = columns[table][column]
        correct = next(r for r in canonical[table] if r[0] == key)[position]
        if row[position] == correct:
            return "unnecessary"
        if value != correct:
            return "repair"
        row[position] = value
    return "correct" if data == canonical else "detection"


def known_patch(task):
    canonical = expected(task["data"])
    result = []
    for table, columns in (
        ("lines", {"product_id": 4, "unit_price": 5, "amount": 6}),
        ("orders", {"total": 1}),
    ):
        for row, target in zip(task["data"][table], canonical[table], strict=True):
            for column, index in columns.items():
                if row[index] != target[index]:
                    result.append(
                        {
                            "table": table,
                            "id": row[0],
                            "column": column,
                            "value": target[index],
                        }
                    )
    return result


def verify(task, completion):
    """Completion serializa trayectoria y parche; replay de herramientas fuera del modelo."""
    try:
        record = parse(completion)
    except (ValueError, TypeError):
        return "unparsed"
    if (
        not isinstance(record, dict)
        or set(record) != {"trajectory", "final"}
        or not isinstance(record["trajectory"], list)
    ):
        return "protocol"
    trajectory = record["trajectory"]
    if len(trajectory) > LIMITS["queries"]:
        return "protocol"
    for turn in trajectory:
        if not isinstance(turn, dict) or set(turn) != {"query", "result"}:
            return "protocol"
        replay = json.loads(json.dumps(query(task["data"], turn["query"])))
        if turn["result"] != replay:
            return "protocol"
        # Errores de consulta consumen presupuesto; recuperarse está permitido.
    final = record["final"]
    if not isinstance(final, dict) or set(final) != {"patch"}:
        return "protocol"
    return patch_status(task, final["patch"])


def tasks(seed=43):
    rng, result = random.Random(seed), []
    for level, n, errors in (("easy", 2, 1), ("medium", 4, 3), ("hard", 7, 6)):
        for index in range(30):
            products = [
                [i, f"SKU{rng.randrange(1000, 9999)}-{i}", rng.randint(2, 30)]
                for i in range(1, 4)
            ]
            orders = [[i, 0] for i in range(1, 2 if level == "easy" else 3)]
            lines = []
            for i in range(1, n + 1):
                product = rng.choice(products)
                lines.append(
                    [
                        i,
                        rng.choice(orders)[0],
                        product[1],
                        rng.randint(1, 6),
                        product[0],
                        product[2],
                        0,
                    ]
                )
            clean = expected({"products": products, "orders": orders, "lines": lines})
            data = copy.deepcopy(clean)
            cells = [("lines", i, j) for i in range(n) for j in (4, 5, 6)] + [
                ("orders", i, 1) for i in range(len(orders))
            ]
            if level == "easy":
                cells = [("lines", i, j) for i in range(n) for j in (5, 6)]
            corrupted = []
            if index % 10:
                for table, row, column in rng.sample(cells, errors):
                    data[table][row][column] += rng.randint(1, 9)
                    corrupted.append([table, data[table][row][0], column])
            key = f"{level}-{index:02}"
            prompt = (
                "Repara la base consultando herramientas. Catálogo products y columnas lines.id/order_id/sku/units "
                "y orders.id son inmutables y correctos. Regla explícita: esta base usa precios actuales de catálogo, "
                "no históricos. SKU identifica un producto inequívoco. lines.product_id=products.id por SKU; "
                "unit_price=products.price; amount=units*unit_price; orders.total=suma de amounts de sus líneas, "
                "cero si no hay líneas. Solo reparar product_id/unit_price/amount de lines y total de orders. "
                "No tocar celdas ya correctas, borrar ni añadir filas. Puede estar limpia. "
                'Responde SOLO JSON {"query":"SELECT ..."} para consultar, o {"patch":[{"table":"lines",'
                '"id":1,"column":"amount","value":2}]} para terminar. Una consulta por turno, máximo tres '
                "consultas de 40 filas; cuarto turno debe ser parche. Máximo 1024 tokens por llamada y 4096 "
                "tokens generados por trayectoria. Parche vacío si está limpia.\n"
                + SCHEMA
                + f"\nInstancia {key}; dataset_seed={seed}."
            )
            result.append(
                {
                    "id": key,
                    "level": level,
                    "data": data,
                    "clean": clean,
                    "corrupted": corrupted,
                    "prompt": prompt,
                }
            )
    return result


def reward(prompt, completion):
    for task in tasks():
        if task["prompt"] == prompt:
            return float(verify(task, completion) == "correct")
    return 0.0
