import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import psycopg2.extras as extras

# Carga variables de entorno desde .env si existe
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "tablero"),
    "user": os.getenv("DB_USER", "tablero_user"),
    "password": os.getenv("DB_PASSWORD", "password"),
}

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            **DB_CONFIG
        )
    return _pool

def get_conn():
    return get_pool().getconn()

def put_conn(conn):
    get_pool().putconn(conn)

def init_db():
    """Ejecuta schema.sql para crear la tabla si no existe."""
    sql_path = Path(__file__).parent / "schema.sql"
    with open(sql_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    finally:
        put_conn(conn)

def fetch_all(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params or [])
            return cur.fetchall()
    finally:
        put_conn(conn)

def fetch_one(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params or [])
            return cur.fetchone()
    finally:
        put_conn(conn)

def execute(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params or [])
            conn.commit()
            try:
                return cur.fetchone()
            except Exception:
                return None
    finally:
        put_conn(conn)
