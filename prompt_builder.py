# prompt_builder.py
FEW_SHOT = """
User: Show all users with status 'active'.
SQL: SELECT "username", "email" FROM "User" WHERE "status" = 'active';

User: Count leads in each stage.
SQL: SELECT "stage", COUNT(*) FROM "lead" GROUP BY "stage";
"""

def build_prompt(schema_text: str, question: str) -> str:
    return f"""
You are an expert PostgreSQL assistant.
Based on the table schema below and the user’s question, write a **single-line** SQL query.
Rules:
- Only provide the SQL query, no explanation.
- Use double quotes for table and column names.
- Do not add line breaks in the SQL.
- Use correct table/column names as per schema.

{FEW_SHOT}

Table Schema:
{schema_text}

User Question: {question}
SQL Query:
"""
