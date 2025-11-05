#IMPORTS
import requests
import json
from pprint import pprint

AGENT_ID = "agente_pdf"
ENDPOINT = f"http://localhost:7777/agents/{AGENT_ID}/runs"

#Conexão com agno (server)===============================================
def get_response_stream(message: str):
    response = requests.post(
        url=ENDPOINT,
        data={
            "message": message,
            "stream": "true",
        },
        stream=True
    )

#streaming (processamento)===============================================
    for line in response.iter_lines():
        if line:
            # parse server-sent events
            if line.startswith(b'data:'):
                data = line[6:] # remove 'data: ' prefix
                try:
                    event = json.loads(data)
                    yield event
                except json.JSONDecodeError:
                    continue


#printa a resposta=======================================================
def print_streaming_response(message: str):
    for event6 in get_response_stream(message):
        event_type = event6.get("event", "")

        # Início da execução
        if event_type == "RunStarted":
            print("Execução iniciada...")
            print("-" * 50)

        elif event_type == "RunContent":
            content = event6.get("content", "")
            if content:
                print(content, end= "", flush=True)

        #tool call iniciado
        elif event_type == "ToolCallStarted":
            tool = event6.get("tool", {})
            tool_name = tool.get("tool_name", "Unknown")
            tool_args = tool.get("tool_args", {})
            print(f"TOOL INICIADA: {json.dumps(tool_args, indent=2)}")


        elif event_type == "ToolCallCompleted":
            tool_name = event6.get("tool", {}).get("tool_name")
            print(f"\nTOOL FINALIZADA: {tool_name}")
            print("-" * 50)

        # Fim da execução
        elif event_type == "RunCompleted":
            print("Execução concluída!")
            metrics = event6.get("metrics", {})
            if metrics:
                print(f"Métricas: {json.dumps(metrics, indent=2)}")
            print("-" * 50)

# run (loop)=============================================================
if __name__ == "__main__":
    message = input("Digite uma mensagem: ")
    print_streaming_response(message)
    
    while True:
        message = input("Digite uma mensagem: ")
        print_streaming_response(message)
