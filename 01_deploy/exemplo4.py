#IMPORTS
import requests
import json
from pprint import pprint
import streamlit as st

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

# Streaming===============================================
st.set_page_config(page_title="Agente Chat PDF")

st.title("Agente Chat PDF")


#-Histórico de mensagens===============================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# mostrar mensagens===============================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistent" and message.get("process"):
            with st.expander(label="process", expander=False):
                st.json(message["process"])
        st.markdown(message["content"])


# Input de usuário===============================================
if prompt := st.chat_input("Digite sua mensagem..."):
    # adicionar mensagem do usuário ao histórico===============================================
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # placeholder para a resposta do assistente===============================================
    with st.chat_message("assistent"):
        process_placeholder = st.empty()
        response_placeholder = st.empty()
        full_response = ""

    #processar resposta do agente===============================================
    for event in get_response_stream(prompt):
        event_type = event.get("event",  "")

        if event_type == "ToolCallStarted":
            tool_name = event.get("tool", {}).get("tool_name")
            with st.status(f"Executando {tool_name}...", expanded=True):
                st.json(event.get("tool", {}).get("tool_args", {}))
         

        #conteúdo da mensagem===============================================
        elif event_type == "RunContent":
            content = event.get("content", "")
            if content:
                full_response += content
                response_placeholder.markdown(full_response + "▌")

    response_placeholder.markdown(full_response)  # mensagem final sem cursor

    # Salvaa resposta e historico na session state===============================================
    st.session_state.messages.append(
        {
            "role": "assistent",
            "content": full_response,
        }
    )