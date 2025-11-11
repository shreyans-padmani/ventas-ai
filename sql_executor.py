# sql_executor.py
import psycopg2
from config import DB_CONFIG

def execute_sql(query):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if cursor.description:  # SELECT query
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:  # INSERT/UPDATE/DELETE
            conn.commit()
            result = {"rows_affected": cursor.rowcount}
    except Exception as e:
        result = {"error": str(e)}
    finally:
        cursor.close()
        conn.close()
    return result
