import os
from time import sleep

import requests
import streamlit as st
from utils import (
    create_header, 
    local_storage_get, 
    local_storage_set,
    local_storage_remove,
    validate_token
)

# --- Configuration ---
BACKEND_URL = os.environ["BACKEND_URL"]

st.set_page_config(page_title="Assistente Médico", page_icon="🩺")
create_header(header_text="")
st.markdown("**Lembre-se: este assistente não substitui um médico verdadeiro.**")

# --- Authentication Handling ---
if st.session_state.get("token"):
    local_storage_set("token", st.session_state.get("token"))
else:
    st.session_state["token"] = local_storage_get("token", "token-get")

validate_token()
st.toast("Autenticação Validada", icon="✅")

# --- API Communication Functions ---

def get_chat_history(patient_id: int, token: str):
    """Fetches the chat history from the backend."""  
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/chat/{patient_id}", headers=headers)
        response.raise_for_status() 
        return response.json().get("messages", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching chat history: {e}")
        return []

def post_chat_message(thread_id: str, message: str, patient_record: dict, token: str):
    """Sends a new message to the backend and gets the assistant's response."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "thread_id": thread_id,
        "message": message,
        "patient_record": patient_record
    }
    try:
        response = requests.post(f"{BACKEND_URL}/chat/", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_detail = e.response.json().get('detail', str(e)) if e.response else str(e)
        st.error(f"Error sending message: {error_detail}")
        return None

# --- Sidebar Display ---
with st.sidebar:
    st.header("Ficha Médica do Paciente")
    st.json(st.session_state.patient_data)
    st.info(" A inteligência artificial tem acesso a essa informação e ela será considerada nas análises ")
    
    if st.button(label="Sair da aplicação",icon="➡️",type="primary"):
        st.toast("Saindo da Aplicação... ", icon="➡️")

        st.session_state.messages =  []
        st.session_state.history_loaded = False
        local_storage_remove("token")

        sleep(1)

        st.switch_page("./app.py")

# --- State Initialization ---
if not st.session_state.get("history_loaded"):
    patient_id = st.session_state.patient_data["id"]
    st.session_state.messages = get_chat_history(patient_id, st.session_state["token"])
    st.session_state.history_loaded = True

# Display existing chat messages
for msg in st.session_state.messages:
    avatar_url = "./assets/user.png" if msg["role"] == "user" else "./assets/diagnostic.png"
    st.chat_message(msg["role"],avatar=avatar_url).write(msg["content"])

# --- Chat Input and Interaction Loop ---
if prompt := st.chat_input("Descreva seu sintoma aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="./assets/user.png").write(prompt)

    token = st.session_state["token"] 

    if not token:
        st.error("Token de autenticação não encontrado, por favor, logue-se novamente")
        st.stop()
        
    thread_id = str(st.session_state.patient_data["id"])
    
    with st.spinner("O assistente está pensando..."):
        assistant_response = post_chat_message(
            thread_id=thread_id,
            message=prompt,
            patient_record=st.session_state.patient_data,
            token=token
        )

    # 4. If receives a valid response, add it to the state and refresh the UI
    if assistant_response:
        st.session_state.messages.append(assistant_response)
        st.rerun()
