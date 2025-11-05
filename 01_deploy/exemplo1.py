from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb

from fastapi import FastAPI, Query
import uvicorn
import asyncio

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

api_key = os.environ.get("OPENAI_API_KEY")
print(f"DEBUG: Chave carregada? {'Sim' if api_key else 'NÃO'}. Prefixo: {api_key[:7] if api_key else 'Nenhum'}")

#RAG
vector_db = ChromaDb(collection="pdf_agent", path="tmp/chromadb", persistent_client=True)
knowledge = Knowledge(vector_db=vector_db)


db = SqliteDb(session_table="agent_session", db_file="tmp/agent.db")

agent = Agent(
    name="Agente de PDF",
    model=OpenAIChat(id="gpt-5-nano", api_key=os.getenv("OPENAI_API_KEY")),
    db=db,
    knowledge=knowledge,
    instructions="Você deve chamar o usuário de senhor",
    description="",
    #add_history_to_context=True,
    search_knowledge=True,
    num_history_runs=3,
    debug_mode=True,
)


# FASTAPI ================================================================= 
app = FastAPI(title="Agente de PDF", description="API para agente de PDF")

@app.post("/agent_pdf")
def agente_pdf(pergunta: str = Query(...)):
    response = agent.run(pergunta)
    final_message = response.messages[-1].content
    return {"message": final_message}

# RUN =======================================================================
if __name__ == "__main__":
    asyncio.run(knowledge.add_content(
        url="https://s3.sa-east-1.amazonaws.com/static.grendene.aatb.com.br/releases/2417_2T25.pdf",
        metadata={"source": "Gendene", "type": "pdf", "description": "Relatório Trimestral 2T25"},
        skip_if_exists=True,
        reader=PDFReader()
    ))
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)