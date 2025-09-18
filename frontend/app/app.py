import json
from http import HTTPStatus

import requests
import streamlit as st
from utils import create_header

BACKEND_URL = "http://fastapi:8080"

def login_form():
    """
    Displays the login form and handles user authentication by calling the backend API.
    """
    col1, col2, col3 = st.columns([1, 10, 1])

    with col2:
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center'>Preencha suas credenciais</h4>", unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="seuemail@exemplo.com")
            password = st.text_input("Password", type="password", placeholder="senha")

            login_submitted = st.form_submit_button("Login")

        if st.button("Não possui uma conta ? Crie uma aqui!", type="primary"):
            st.switch_page("./pages/sign_up.py")

        if login_submitted:
            
            login_data = {
                'username': email,
                'password': password
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/auth/token", data=login_data)

                if response.status_code == HTTPStatus.OK:
                    token_data = response.json()
                    
                    st.success("Logged in successfully!")
                    st.session_state["logged_in"] = True
                    st.session_state["token"] = token_data['access_token']
                    st.switch_page("./pages/chat.py")
                    st.rerun()
                elif response.status_code == HTTPStatus.UNAUTHORIZED:
                    st.error("Email ou senha incorretos.")
                else:
                    st.error(f"Erro ao fazer login. Status: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao servidor. Verifique se o backend está em execução.")

            ### <<< CHANGE END: API AUTHENTICATION LOGIC >>> ###

# --- Main script execution flow ---
st.set_page_config(page_title="Login", page_icon="🔒")

create_header()
login_form()

