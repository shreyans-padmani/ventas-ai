from fastapi import FastAPI
from pydantic import BaseModel
from text_to_sql import text_to_sql
from sql_executor import execute_sql
from llm_interpreter import explain_result
from collections import defaultdict
import os
import uvicorn

app = FastAPI()

# Maintain chat memory per session (could later move to Redis or DB)
chat_memory = defaultdict(list)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    
@app.get("/")
def root():
    return {"status": "ok", "message": "AI SQL API is running"}

@app.post("/chat")
def chat(data: ChatRequest):
    history = chat_memory[data.session_id]
    user_msg = data.message

    try:
        # Build conversational context (last few turns)
        context = "\n".join([f"User: {m['user']}\nAI: {m['ai']}" for m in history[-3:]])

        # Combine history into a contextual question
        contextual_question = f"""
You are an intelligent SQL assistant.
Previous conversation:
{context}

Now, user says:
{user_msg}

If the user refers to "previous query" or "last result", reuse or modify last SQL.
Otherwise, generate a new SQL query.
"""

        sql = text_to_sql(contextual_question)
        result = execute_sql(sql)
        answer = explain_result(user_msg, sql, result)

        # Save to memory
        history.append({"user": user_msg, "ai": answer, "sql": sql})

        return {
            "success": True,
            "session_id": data.session_id,
            "sql": sql,
            "result": result,
            "answer": answer,
            "history": history,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
