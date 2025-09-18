import json
from pathlib import Path

import requests
import streamlit as st
from streamlit_javascript import st_javascript

BACKEND_URL = "http://fastapi:8080"

def create_header(header_text=None):

    with open('./default.css') as f:
        css_styles = f.read()

    st.markdown(f"""
    <style>
    {css_styles}
    </style>
    """,unsafe_allow_html=True)

    st.markdown('<p class="title">Tenma Project</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{"A medicina deve ser acessível para todos" if header_text==None else header_text}</p>', unsafe_allow_html=True)

def local_storage_get(key, id):
    return st_javascript(f"localStorage.getItem('{key}');", key=id)

def local_storage_set(key, value):
    return st_javascript(f"localStorage.setItem('{key}','{value}');")

def validate_token():
    """
    Checks for a token in session state and validates it against the backend /patients/me endpoint.

    - If no token exists locally, redirects to login.
    - If a token exists, it sends it to the backend for validation.
    - If valid (200 OK), it stores the user data in the session and allows the page to load.
    - If invalid (401 Unauthorized), it clears the local token and redirects to login.
    - If the server is unreachable, it shows a connection error.
    """
    token = local_storage_get("token", "token-validate")

    # Quick check for token existence in session state (avoids unnecessary API calls)
    if not token: 
        st.warning("Por favor, faça o login para acessar esta página.")
        st.page_link("app.py", label="Ir para a página de Login", icon="➡️")
        st.stop()
        return

    # If a token exists, validate it with the backend
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/patients/me", headers=headers)
        if response.status_code == 200:
            st.session_state["patient_data"] = response.json()
            return

        else:
            st.warning("Sua sessão expirou. Por favor, faça o login novamente.")
            st.page_link("app.py", label="Ir para a página de Login", icon="➡️")
            st.stop()
            return

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao servidor para validar a sessão. O backend está em execução?")
        st.stop()
        return
