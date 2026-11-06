"""Text-to-SQL sobre cuatro bases finitas; sandbox SQLite de solo lectura."""

import collections
import json
import math
import multiprocessing
import random
import re
import sqlite3
import time
from contextlib import closing

SCHEMA = "CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, region TEXT); CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), amount INTEGER, ordered_at TEXT);"
MAX_ROWS = 200
MAX_STEPS = 100_000
TIMEOUT = 0.15


def database(data):
    connection = sqlite3.connect(":memory:")
    connection.executescript(SCHEMA)
    connection.executemany("INSERT INTO customers VALUES(?,?,?)", data["customers"])
    connection.executemany("INSERT INTO orders VALUES(?,?,?,?)", data["orders"])
    connection.commit()
    return connection


def _worker(connection, data, sql):
    try:
        result = _execute(data, sql)
        if len(json.dumps(result).encode()) > 64_000:
            result = ("limit", None)
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
        if not receiver.poll(0.25):
            return ("timeout", None)
        try:
            return receiver.recv()
        except EOFError:
            return ("execution", None)
    finally:
        receiver.close()
        process.join(timeout=0.02)
        if process.is_alive():
            process.kill()
            process.join()


def _execute(data, sql):
    """execute impide múltiples sentencias; authorizer niega todo salvo lectura."""
    with closing(database(data)) as connection:
        connection.enable_load_extension(False)
        connection.execute("PRAGMA query_only=ON")
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 100_000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 12_000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 50)
        allowed_functions = {
            "count",
            "sum",
            "avg",
            "min",
            "max",
            "coalesce",
            "ifnull",
            "abs",
            "round",
            "length",
            "lower",
            "upper",
            "substr",
            "total",
            "nullif",
            "like",
        }

        def authorizer(action, arg1, arg2, db, trigger):
            if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
                return sqlite3.SQLITE_OK
            if (
                action == sqlite3.SQLITE_READ
                and db == "main"
                and arg1 in {"customers", "orders"}
            ):
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and arg2 in allowed_functions:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        connection.set_authorizer(authorizer)
        started = time.monotonic()
        steps = 0

        def progress():
            nonlocal steps
            steps += 100
            return int(steps > MAX_STEPS or time.monotonic() - started > TIMEOUT)

        connection.set_progress_handler(progress, 100)
        try:
            cursor = connection.execute(sql)
            if cursor.description is None:
                return "execution", None
            rows = cursor.fetchmany(MAX_ROWS + 1)
            if len(rows) > MAX_ROWS:
                return "limit", None
            return "ok", rows
        except sqlite3.Error as error:
            message = str(error)
            if "interrupted" in message:
                return "timeout", None
            if (
                "syntax" in message
                or "one statement" in message
                or "incomplete input" in message
                or "unrecognized token" in message
            ):
                return "syntax", None
            return "execution", None
        finally:
            connection.set_authorizer(None)
            connection.set_progress_handler(None, 0)
            connection.close()


def extract(completion):
    text = completion.strip()
    all_blocks = re.findall(r"```([^\n]*)\n([\s\S]*?)```", text)
    blocks = [
        body
        for language, body in all_blocks
        if language.strip().lower() in ("", "sql", "sqlite")
    ]
    if blocks:
        if len({block.strip() for block in blocks}) != 1:
            return None
        outside = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text, flags=re.IGNORECASE)
        if re.search(
            r"^\s*;?\s*(?:[-*]\s*)?(?:(?:o|alternativa|consulta|respuesta)\s*:?\s*)?(select|with|insert|update|delete|attach|pragma|create|drop|replace)\b",
            outside,
            re.IGNORECASE | re.MULTILINE,
        ):
            return None
        text = blocks[0].strip()
    if (
        not text
        or len(text) > 12_000
        or not re.match(
            r"^(select|with|values|explain|pragma|attach|insert|update|delete|create|drop|alter|replace)\b",
            text,
            re.IGNORECASE,
        )
    ):
        return None
    return text


def bag(rows):
    """NULL/texto/bytes distintos; enteros y reales finitos comparados exactamente."""

    def cell(value):
        if value is None:
            return ("null", None)
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                raise ValueError("nonfinite result")
            return ("number", value)
        return (type(value).__name__, value)

    return collections.Counter(tuple(cell(v) for v in row) for row in rows)


def details(task, completion):
    sql = extract(completion)
    if sql is None:
        return {"status": "unparsed", "visible_pass": False, "hidden_failure": False}
    matches = []
    for data in task["databases"]:
        status, rows = query(data, sql)
        if status != "ok":
            return {
                "status": status,
                "visible_pass": bool(matches and matches[0]),
                "hidden_failure": bool(matches and matches[0]),
            }
        ref_status, expected = query(data, task["reference"])
        if ref_status != "ok":
            raise ValueError("reference cannot execute")
        try:
            matches.append(bag(rows) == bag(expected))
        except ValueError:
            matches.append(False)
    return {
        "status": "correct" if all(matches) else "semantic",
        "visible_pass": matches[0],
        "hidden_failure": matches[0] and not all(matches[1:]),
    }


def verify(task, completion):
    return details(task, completion)["status"]


def tasks(seed=43):
    result = []
    rng = random.Random(seed)
    for level in ("easy", "medium", "hard"):
        for index in range(30):
            region = rng.choice(["Norte", "Sur", "Centro"])
            threshold = rng.randint(8, 35)
            date = f"2026-10-{rng.randint(2, 25):02}"
            # SQL de referencia solo interpola enteros y opciones sintéticas cerradas.
            if level == "easy":
                family = "filter"
                question = f"Devuelve id y amount de cada pedido con amount >= {threshold} y ordered_at >= '{date}' (ambos límites incluidos)."
                reference = f"SELECT id, amount FROM orders WHERE amount >= {threshold} AND ordered_at >= '{date}'"  # nosec B608
            elif level == "medium" and index % 2 == 0:
                family = "join"
                question = f"Devuelve name del cliente por cada pedido con importe >= {threshold} de clientes de región '{region}'. Conserva nombres duplicados y una fila por pedido."
                reference = f"SELECT c.name FROM customers c JOIN orders o ON c.id=o.customer_id WHERE c.region='{region}' AND o.amount >= {threshold}"  # nosec B608
            elif level == "medium":
                family = "having"
                question = f"Devuelve id del cliente y suma de importes no NULL para clientes con suma estrictamente mayor que {threshold}. Clientes sin importes no NULL quedan excluidos. Agrupa por id, no por nombre."
                reference = f"SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id HAVING SUM(amount) > {threshold}"  # nosec B608
            else:
                family = "subquery"
                question = f"Devuelve id y name de TODOS los clientes de región '{region}' cuya cantidad de pedidos (incluidos importes NULL) sea la máxima entre clientes de esa región, incluyendo empates. Clientes sin pedidos cuentan cero; sin clientes de esa región devuelve cero filas."
                reference = f"SELECT c.id,c.name FROM customers c WHERE c.region='{region}' AND (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) = (SELECT MAX(n) FROM (SELECT COUNT(o.id) n FROM customers x LEFT JOIN orders o ON x.id=o.customer_id WHERE x.region='{region}' GROUP BY x.id))"  # nosec B608
            databases = []
            for variant in range(4):
                # Ocultas incluyen NULL, nombres iguales, ceros, fechas e importes límite y empates.
                customers = [
                    [
                        i,
                        "Ana" if i <= 2 else f"Cliente{i}",
                        region if i <= 3 else rng.choice(["Norte", "Sur", "Centro"]),
                    ]
                    for i in range(1, 7)
                ]
                orders = []
                for i in range(1, 8 + variant * 3):
                    customer = (i % 4 + 1) if variant == 3 else rng.randint(1, 5)
                    amount = rng.choice(
                        [
                            None,
                            0,
                            threshold - 1,
                            threshold,
                            threshold + 1,
                            rng.randint(1, 80),
                        ]
                    )
                    ordered_at = rng.choice([date, "2026-10-01", "2026-10-31", None])
                    orders.append([i, customer, amount, ordered_at])
                if variant:
                    orders.extend([[100, 1, threshold, date], [101, 2, None, date]])
                if variant == 2:
                    other_region = next(
                        r for r in ("Norte", "Sur", "Centro") if r != region
                    )
                    for customer in customers[3:]:
                        customer[2] = other_region
                    for order in orders:
                        order[1] = 4 + order[0] % 2
                databases.append({"customers": customers, "orders": orders})
            prompt = (
                "Escribe SOLO una consulta SQLite SELECT (puede usar WITH). No herramientas. "
                "Devuelve exactamente columnas solicitadas en el orden solicitado; orden de filas irrelevante, "
                "semántica multiconjunto: conservar duplicados salvo que se indique otra cosa. NULL sigue "
                "semántica SQLite, no equivale a cero. Fechas ISO YYYY-MM-DD, comparación lexicográfica; "
                "fechas NULL no cumplen filtros de fecha. Importes enteros en la misma unidad; no redondear.\n"
                + SCHEMA
                + "\nPregunta: "
                + question
                + "\nBase visible: "
                + json.dumps(databases[0], ensure_ascii=False)
            )
            result.append(
                {
                    "id": f"{level}-{index:02}",
                    "level": level,
                    "family": family,
                    "databases": databases,
                    "reference": reference,
                    "prompt": prompt,
                    "question": question,
                    "region": region,
                    "threshold": threshold,
                    "date": date,
                }
            )
    return result


def reward(prompt, completion):
    # El prompt contiene especificación y base visible; recuperar solo la tarea exacta registrada.
    for task in tasks():
        if task["prompt"] == prompt:
            return float(verify(task, completion) == "correct")
    return 0.0
