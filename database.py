# database.py
import psycopg2

from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_schema(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name FROM information_schema.tables WHERE table_schema='public';
    """)
    tables = [t[0] for t in cursor.fetchall()]
    schema_info = []

    for table in tables:
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}';
        """)
        cols = cursor.fetchall()
        schema_info.append(f'Table "{table}":\n' + "\n".join([f'  - "{c[0]}" ({c[1]})' for c in cols]))

    cursor.close()
    return "\n\n".join(schema_info)
