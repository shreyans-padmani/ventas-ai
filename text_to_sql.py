# text_to_sql.py
from database import get_connection, get_schema
from llm_client import generate_sql

def text_to_sql(question):
    conn = get_connection()
    schema = get_schema(conn)
    sql_query = generate_sql(schema, question)
    conn.close()
    return sql_query
