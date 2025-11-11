# main.py
from text_to_sql import text_to_sql
from sql_executor import execute_sql
from llm_interpreter import explain_result

if __name__ == "__main__":
    print("🚀 Text-to-SQL + LLM Interpreter (Production Mode)\n")

    while True:
        question = input("❓ Enter your question (or 'exit' to quit): ")
        if question.lower() in ["exit", "quit"]:
            break

        try:
            sql = text_to_sql(question)
            print("\n🧠 Generated SQL:")
            print(sql)

            result = execute_sql(sql)
            print("\n📊 SQL Result:")
            print(result)

            explanation = explain_result(question, sql, result)
            print("\n💬 Natural Language Answer:")
            print(explanation)

            print("-" * 70)
        except Exception as e:
            print("⚠️ Error:", e)
            print("-" * 70)
