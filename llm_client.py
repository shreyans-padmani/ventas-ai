# llm_client.py
import requests
import re
from config import GOOGLE_API_KEY, MODEL_NAME

FEW_SHOT_EXAMPLES = """
Examples:
User: Show all users with active status.
SQL: SELECT "username", "email" FROM "User" WHERE "status" = 'active';

User: Count the number of leads in each stage.
SQL: SELECT "stage", COUNT(*) FROM "lead" GROUP BY "stage";

User: Get top 5 agencies by total leads.
SQL: SELECT "agencyid", COUNT(*) AS total FROM "lead" GROUP BY "agencyid" ORDER BY total DESC LIMIT 5;
"""

def generate_sql(schema, question):
    prompt = f"""
You are an expert PostgreSQL assistant. 
Generate an SQL query that answers the user's question.

Rules:
- Only return SQL (no explanation, no markdown).
- Single-line SQL (no line breaks).
- Always use double quotes for identifiers.
- Make sure table/column names match the schema exactly.

{FEW_SHOT_EXAMPLES}

Table Schema:
{schema}

User Question: {question}
SQL Query:
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("❌ Gemini Error:", response.text)
        raise Exception(f"Gemini API Error: {response.status_code}")

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    query = re.sub(r"```sql|```", "", text).strip().replace("\n", " ")
    return query
