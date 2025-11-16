# llm_client.py
import requests
import re
from config import GOOGLE_API_KEY, MODEL_NAME
from embeddings import ExampleRetriever

import os

DEFAULT_EXAMPLES = [
    {"user": "Show all users with active status.", "sql": 'SELECT "username", "email" FROM "User" WHERE "status" = \'active\';'},
    {"user": "Count the number of leads in each stage.", "sql": 'SELECT "stage", COUNT(*) FROM "lead" GROUP BY "stage";'},
    {"user": "Get top 5 agencies by total leads.", "sql": 'SELECT "agencyid", COUNT(*) AS total FROM "lead" GROUP BY "agencyid" ORDER BY total DESC LIMIT 5;'},
    # add more short examples here as needed
]

_retriever = ExampleRetriever(DEFAULT_EXAMPLES)

def load_schema_from_file(path: str) -> str:
    """Load plain-text table schema from disk and return it."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schema file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def _build_few_shot(examples):
    """Return a small examples string constructed from selected examples."""
    lines = []
    for ex in examples:
        lines.append(f"User: {ex['user']}")
        lines.append(f"SQL: {ex['sql']}")
        lines.append("")  # blank spacer
    return "\n".join(lines)

def generate_sql(schema, question, k=3):
    # fetch top-k similar few-shot examples
    selected = _retriever.get_top_k(question, k=k)
    few_shot_text = _build_few_shot(selected)
    print("", few_shot_text)
    prompt = f"""
You are an expert PostgreSQL assistant. 
Generate an SQL query that answers the user's question.

Rules:
- Only return SQL (no explanation, no markdown).
- Single-line SQL (no line breaks).
- Always use double quotes for identifiers.
- Make sure table/column names match the schema exactly.

{few_shot_text}

Table Schema:
{load_schema_from_file("schema.txt")}

User Question: {question}
SQL Query:
"""
    print("", prompt)
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
