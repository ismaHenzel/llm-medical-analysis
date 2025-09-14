import os

import requests
import streamlit as st
from utils import (create_header, local_storage_get, local_storage_set,
                   validate_token)

# --- Configuration ---
BACKEND_URL = "http://localhost:8080"

st.set_page_config(page_title="Assistente Médico", page_icon="🩺")
create_header(header_text="")

# --- Authentication Handling ---
if st.session_state.get("token"):
    local_storage_set("token", st.session_state.get("token"))
else:
    st.session_state["token"] = local_storage_get("token", "token-get")

validate_token()

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

# --- Streamlit UI and State Management ---
st.markdown("**Lembre-se: este assistente não substitui um médico verdadeiro.**")

# --- Sidebar Display ---
with st.sidebar:
    st.header("Ficha Médica do Paciente")
    st.json(st.session_state.patient_data)
    st.info(" A inteligência artificial tem acesso a essa informação e ela será considerada nas análises ")

    st.page_link("app.py", label="Sair da aplicação", icon="➡️")

# --- Chat Initialization ---
if "history_loaded" not in st.session_state:
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
