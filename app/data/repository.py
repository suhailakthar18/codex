import os
import sqlite3
from pathlib import Path


class SQLiteStoreRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price REAL NOT NULL,
                    likes INTEGER NOT NULL DEFAULT 0,
                    saved INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS cart_items (
                    product_id INTEGER PRIMARY KEY,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                );
                """
            )

    def list_products(self):
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

    def add_product(self, name: str, description: str, price: float):
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO products(name, description, price) VALUES (?, ?, ?)",
                (name, description, price),
            )
            row = conn.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)

    def change_metric(self, product_id: int, field: str):
        if field not in {"likes", "saved"}:
            raise ValueError("Unsupported metric")
        with self._connection() as conn:
            conn.execute(f"UPDATE products SET {field} = {field} + 1 WHERE id = ?", (product_id,))
            row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None

    def add_to_cart(self, product_id: int):
        with self._connection() as conn:
            exists = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
            if not exists:
                return None
            conn.execute(
                """
                INSERT INTO cart_items(product_id, quantity)
                VALUES (?, 1)
                ON CONFLICT(product_id) DO UPDATE SET quantity = quantity + 1
                """,
                (product_id,),
            )
        return self.get_cart()

    def get_cart(self):
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT p.id, p.name, p.price, c.quantity, p.price * c.quantity AS line_total
                FROM cart_items c
                JOIN products p ON p.id = c.product_id
                ORDER BY p.id DESC
                """
            ).fetchall()
        items = [dict(row) for row in rows]
        total = round(sum(item["line_total"] for item in items), 2)
        return {"items": items, "total": total}


class PostgresStoreRepository:
    def __init__(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("psycopg is required for postgres mode") from exc

        self.psycopg = psycopg
        self.conninfo = os.environ.get(
            "DATABASE_URL",
            "dbname=store user=store password=store host=db port=5432",
        )
        self._init_db()

    def _connection(self):
        conn = self.psycopg.connect(self.conninfo)
        conn.autocommit = False
        return conn

    def _init_db(self):
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        price DOUBLE PRECISION NOT NULL,
                        likes INTEGER NOT NULL DEFAULT 0,
                        saved INTEGER NOT NULL DEFAULT 0
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cart_items (
                        product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
                        quantity INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )
            conn.commit()

    def list_products(self):
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, description, price, likes, saved FROM products ORDER BY id DESC"
                )
                rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "name": r[1],
                "description": r[2],
                "price": r[3],
                "likes": r[4],
                "saved": r[5],
            }
            for r in rows
        ]

    def add_product(self, name: str, description: str, price: float):
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO products(name, description, price)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, description, price, likes, saved
                    """,
                    (name, description, price),
                )
                row = cur.fetchone()
            conn.commit()
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "likes": row[4],
            "saved": row[5],
        }

    def change_metric(self, product_id: int, field: str):
        if field not in {"likes", "saved"}:
            raise ValueError("Unsupported metric")
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE products
                    SET {field} = {field} + 1
                    WHERE id = %s
                    RETURNING id, name, description, price, likes, saved
                    """,
                    (product_id,),
                )
                row = cur.fetchone()
            conn.commit()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "likes": row[4],
            "saved": row[5],
        }

    def add_to_cart(self, product_id: int):
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
                if not cur.fetchone():
                    return None
                cur.execute(
                    """
                    INSERT INTO cart_items(product_id, quantity)
                    VALUES (%s, 1)
                    ON CONFLICT(product_id) DO UPDATE SET quantity = cart_items.quantity + 1
                    """,
                    (product_id,),
                )
            conn.commit()
        return self.get_cart()

    def get_cart(self):
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.name, p.price, c.quantity, p.price * c.quantity AS line_total
                    FROM cart_items c
                    JOIN products p ON p.id = c.product_id
                    ORDER BY p.id DESC
                    """
                )
                rows = cur.fetchall()
        items = [
            {
                "id": r[0],
                "name": r[1],
                "price": float(r[2]),
                "quantity": r[3],
                "line_total": float(r[4]),
            }
            for r in rows
        ]
        total = round(sum(item["line_total"] for item in items), 2)
        return {"items": items, "total": total}


def create_repository(db_path="data/store.db"):
    engine = os.environ.get("DB_ENGINE", "sqlite").lower()
    if engine == "postgres":
        return PostgresStoreRepository()
    return SQLiteStoreRepository(db_path)
