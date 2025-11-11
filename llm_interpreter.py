# llm_interpreter.py
import requests
from config import GOOGLE_API_KEY, MODEL_NAME

def explain_result(question, sql_query, result):
    prompt = f"""
You are a helpful AI assistant that explains SQL query results.

User Question: {question}
Generated SQL: {sql_query}
SQL Output: {result}

Please provide a clear and concise natural language explanation of the result.
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("❌ Gemini Error:", response.text)
        raise Exception(f"Gemini API Error: {response.status_code}")

    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
