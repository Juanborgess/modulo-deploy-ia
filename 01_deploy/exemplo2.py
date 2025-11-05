# CÓDIGO FINAL CORRIGIDO PARA EXECUTAR O AGENTOS

# Importações Necessárias
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.os import AgentOS

# CARREGAMENTO SEGURO DA CHAVE E DEBUG
api_key = os.environ.get("OPENAI_API_KEY")
print(f"DEBUG: Chave carregada? {'Sim' if api_key else 'NÃO'}. Prefixo: {api_key[:7] if api_key else 'Nenhum'}")

# RAG/STORAGE SETUP
vector_db = ChromaDb(collection="pdf_agent", path="tmp/chromadb", persistent_client=True)
knowledge = Knowledge(vector_db=vector_db)
db = SqliteDb(session_table="agent_session", db_file="tmp/agent.db")


# ************* 1. Definição do Agente *************
agent = Agent(
    id="agente_pdf",
    name="Agente de PDF",
    # Usa a variável de chave carregada
    model=OpenAIChat(id="gpt-5-nano", api_key=api_key), 
    db=db,
    knowledge=knowledge,
    instructions="Você deve chamar o usuário de senhor e busque informações no PDF antes de responder.",
    description="",
    enable_user_memories=True,
    add_history_to_context=True,
    search_knowledge=True,
    num_history_runs=3,
    debug_mode=True,
)


# ************* 2. AGENTOS Simplificado *************
agent_os = AgentOS(
    name="Agente de PDF",
    agents=[agent], 
)

app = agent_os.get_app()

# RUN =======================================================================
if __name__ == "__main__":
    # Indexação de Conteúdo (RAG)
    knowledge.add_content(
        url="https://s3.sa-east-1.amazonaws.com/static.grendene.aatb.com.br/releases/2417_2T25.pdf",
        metadata={"source": "Gendene", "type": "pdf", "description": "Relatório Trimestral 2T25"},
        skip_if_exists=True,
        reader=PDFReader()
    )
    
    # Execução do Deploy Simplificado (Porta 8000 é a mais comum)
    agent_os.serve(app="exemplo2:app", host="0.0.0.0", port=8000, reload=True)