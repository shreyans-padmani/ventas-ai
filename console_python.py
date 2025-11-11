import os
import re
import psycopg2
import requests
import pandas as pd

# -------------------------------
# 🔐 CONFIGURATION
# -------------------------------
GOOGLE_API_KEY = "AIzaSyDO540rkV5cQf1S-P6mRWZfyU2f0ToeYMw"

DB_CONFIG = {
    "dbname": "Ventas_Ai_DB",
    "user": "Ventas_Ai_User",
    "password": "Ventas_Ai!Pw",
    "host": "168.231.120.235",
    "port": "5432",
}

# -------------------------------
# 📦 DATABASE CONNECTION
# -------------------------------
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        exit()


def get_table_schema(conn):
    """Fetch table info for schema context."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public';
    """)
    tables = cursor.fetchall()
    schema_info = []
    for t in tables:
        table = t[0]
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}';
        """)
        cols = cursor.fetchall()
        schema_info.append(f"Table: {table}\n" + "\n".join([f" - {c[0]} ({c[1]})" for c in cols]))
    cursor.close()
    return "\n\n".join(schema_info)


# -------------------------------
# 🤖 LLM (Gemini API)
# -------------------------------
def generate_sql_from_question(schema, question):
    prompt = f"""
You are an expert PostgreSQL assistant.
Based on the table schema below, write a SQL query that answers the user's question.

Rules:
- Only return the SQL query (no explanation).
- Single-line SQL (no line breaks).
- Always wrap table and column names in double quotes.

Table Schema:
{schema}

Question: {question}
SQL Query:
"""

    # ✅ use updated Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    print("\n🔍 DEBUG: Sending request to Gemini API")
    print("🔹 URL:", url)
    print("🔹 Headers:", headers)
    print("🔹 Payload:", str(payload)[:500], "...")  # truncate for readability

    response = requests.post(url, headers=headers, json=payload)

    print("🔹 HTTP Status Code:", response.status_code)
    print("🔹 Response Text (first 400 chars):", response.text[:400])

    # Raise for status after debug info
    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Extract SQL code
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    query = match.group(1).strip() if match else text.replace("\n", " ").strip()
    return query



# -------------------------------
# 🧠 SIMPLE EVALUATION
# -------------------------------
def evaluate_query(generated, reference):
    """Compare LLM SQL to expected SQL in a simple rule-based way."""
    generated_clean = re.sub(r"\s+", " ", generated.strip().lower())
    reference_clean = re.sub(r"\s+", " ", reference.strip().lower())
    if generated_clean == reference_clean:
        return "✅ Exact match"
    elif all(k in generated_clean for k in reference_clean.split()[:3]):
        return "🟡 Partial match"
    else:
        return "❌ Not matching"


# -------------------------------
# 🚀 MAIN EXECUTION
# -------------------------------
def main():
    conn = get_connection()
    schema = get_table_schema(conn)

    user_questions = [
        "What was the lead of stage 2",
        "What are the names of all stages in the stage table?",
        "List all user names from the user table.",
        "Find the companyaddress of all agency in the agency table.",
        "What is the name of the lead with lead Index = 1"
    ]

    references = [
        'SELECT "name" FROM "stage" WHERE "sequence" = 2.00;',
        'SELECT "name" FROM "stage";',
        'SELECT "username" FROM "User";',
        'SELECT "companyaddress" FROM "agency";',
        'SELECT "companyname" FROM "lead" WHERE "leadid" = 1;'
    ]

    results = []

    for q, ref in zip(user_questions, references):
        print(f"\n🧩 Question: {q}")
        generated_sql = generate_sql_from_question(schema, q)
        print("🔹 Generated SQL:", generated_sql)
        print("🔸 Reference SQL:", ref)

        # Try executing query safely
        try:
            cur = conn.cursor()
            cur.execute(generated_sql)
            rows = cur.fetchmany(3)
            cur.close()
            status = "✅ Executed successfully"
        except Exception as e:
            rows = []
            status = f"❌ Execution error: {e}"

        # Evaluate correctness
        eval_result = evaluate_query(generated_sql, ref)

        results.append({
            "question": q,
            "generated_sql": generated_sql,
            "reference": ref,
            "status": status,
            "evaluation": eval_result
        })

    conn.close()

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("sql_evaluation_results.csv", index=False)
    print("\n✅ Evaluation complete. Results saved to sql_evaluation_results.csv")
    print(df)


if __name__ == "__main__":
    main()
