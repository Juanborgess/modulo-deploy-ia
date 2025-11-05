#---------------------------------------------------
# Conta Corrente Bancária - FastAPI 
# Gerenciar saques e depositos de clientes
#---------------------------------------------------

#IMPORTS
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, Field

#INICIALIZAÇÃO DO APP
app = FastAPI(
    title="Conta Bancária - Conta Corrente",

)

#Adicionar Clientes
db_clients = {
    "joao": 0,
    "maria": 0,
    "pedro": 0,
}

#Criar uma classe para as movimentações (saques e depositos) obs: usar pydantic (para nao acontecer erros)
class Movimentacao(BaseModel):
    cliente: str = Field(..., description="Nome do cliente")
    valor: float = Field(..., gt=0, description="Valor da movimentação")

#Criar um endpoint HOME (raiz)
@app.get("/")
def read_root():
    return {"message": "Conta Bancaria - Conta Corrente"}

#Criar um endpoint para consultar o saldo
@app.post("/saldo/")
def saldo( cliente: str):
    return {"message": f"Saldo do cliente {cliente} é {db_clients[cliente]}"}

# Criar um endpoint para realizar saques
@app.post("/saque/")
def saque(movimentacao: Movimentacao):
    db_clients[movimentacao.cliente] -= movimentacao.valor
    return {"message": {"cliente": movimentacao.cliente, "valor_movimentacao": -movimentacao.valor, "saldo": db_clients[movimentacao.cliente]}}

# Criar um endpoint para realizar depósitos
@app.post("/deposito/")
def deposito(movimentacao: Movimentacao):
    db_clients[movimentacao.cliente] += movimentacao.valor
    return {"message":  {"cliente": movimentacao.cliente, "valor_movimentacao": movimentacao.valor, "saldo": db_clients[movimentacao.cliente]}}

#RUN
if __name__ == "__main__":
    uvicorn.run("exemplo2:app", host="0.0.0.0", port=8000, reload=True)