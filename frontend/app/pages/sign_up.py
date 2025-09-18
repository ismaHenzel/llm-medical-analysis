import sys
from datetime import date

import requests
import streamlit as st

sys.path.append("../")
from utils import create_header

# --- CONFIGURAÇÃO DA API ---
API_URL = "http://fastapi:8080"

# --- MAPEAMENTO DE VALORES PARA ENUMS DO BACKEND ---
# Mapeia as opções da UI para os valores que o backend espera
SEX_MAP = {"Masculino": "Male", "Feminino": "Female"}

ANCESTRY_MAP = {
    'Branco(a)': 'White',
    'Preto(a)': 'Black',
    'Pardo(a)': 'Latin',
    'Asiático(a)': 'Asian',
    'Indígena': 'Multiracial',
    'Outro': 'Multiracial' 
}

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
def initialize_session_state():
    """Inicializa as chaves de estado da sessão para o formulário dinâmico, se não existirem."""
    keys = ['conditions', 'allergies', 'medications', 'injuries', 'family_histories']
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = []

# --- RENDERIZAÇÃO DA UI PARA SEÇÕES DINÂMICAS ---
def render_dynamic_section(section_title, items_list, add_button_label, key_prefix):
    """
    Renderiza uma seção que permite aos usuários adicionar, visualizar e remover itens dinamicamente.
    A entrada de dados acontece diretamente no local.
    """
    st.subheader(section_title)
    
    for i, item in enumerate(items_list):
        st.markdown(f"---")
        unique_key = f"{key_prefix}_{i}"

        if key_prefix == 'cond':
            cols = st.columns([3, 2, 2, 1])
            items_list[i]['condition_name'] = cols[0].text_input("Nome da Condição", value=item.get('condition_name', ''), key=f"name_{unique_key}")
            items_list[i]['diagnosis_date'] = cols[1].date_input("Data do Diagnóstico", value=item.get('diagnosis_date', date.today()), key=f"date_{unique_key}")
            items_list[i]['condition_status'] = cols[2].selectbox("Status", ["Ativa", "Inativa"], index=0 if item.get('condition_status', 'Ativa') == 'Ativa' else 1, key=f"status_{unique_key}")
            if cols[3].button("❌", key=f"remove_{unique_key}", help="Remover condição"):
                items_list.pop(i)
                st.rerun()

        elif key_prefix == 'allergy':
            cols = st.columns([3, 3, 2, 1])
            items_list[i]['substance'] = cols[0].text_input("Substância", value=item.get('substance', ''), key=f"sub_{unique_key}")
            items_list[i]['reaction_type'] = cols[1].text_input("Reação", value=item.get('reaction_type', ''), key=f"react_{unique_key}")
            items_list[i]['discovery_date'] = cols[2].date_input("Data da Descoberta", value=item.get('discovery_date', date.today()), key=f"disc_date_{unique_key}")
            if cols[3].button("❌", key=f"remove_{unique_key}", help="Remover alergia"):
                items_list.pop(i)
                st.rerun()

        elif key_prefix == 'med':
            cols = st.columns([3, 2, 2, 2, 1])
            items_list[i]['medication_name'] = cols[0].text_input("Nome do Medicamento", value=item.get('medication_name', ''), key=f"med_name_{unique_key}")
            items_list[i]['dosage'] = cols[1].text_input("Dosagem", value=item.get('dosage', ''), key=f"med_dosage_{unique_key}")
            items_list[i]['frequency'] = cols[2].text_input("Frequência", value=item.get('frequency', ''), key=f"med_freq_{unique_key}")
            items_list[i]['treatment_start_date'] = cols[3].date_input("Data de Início", value=item.get('treatment_start_date', date.today()), key=f"med_start_{unique_key}")
            if cols[4].button("❌", key=f"remove_{unique_key}", help="Remover medicamento"):
                items_list.pop(i)
                st.rerun()

        elif key_prefix == 'injury':
            cols = st.columns([3, 2, 2, 2, 1])
            items_list[i]['injury_description'] = cols[0].text_input("Descrição", value=item.get('injury_description', ''), key=f"injury_desc_{unique_key}")
            items_list[i]['type'] = cols[1].text_input("Tipo (ex: Fratura)", value=item.get('type', ''), key=f"injury_type_{unique_key}")
            items_list[i]['occurrence_date'] = cols[2].date_input("Data da Lesão", value=item.get('occurrence_date', date.today()), key=f"injury_date_{unique_key}")
            items_list[i]['severity'] = cols[3].text_input("Gravidade", value=item.get('severity', ''), key=f"injury_sev_{unique_key}")
            if cols[4].button("❌", key=f"remove_{unique_key}", help="Remover lesão"):
                items_list.pop(i)
                st.rerun()

        elif key_prefix == 'fam':
            cols = st.columns([3, 3, 1])
            items_list[i]['relationship_to_patient'] = cols[0].text_input("Parentesco", value=item.get('relationship_to_patient', ''), key=f"fam_rel_{unique_key}")
            items_list[i]['medical_condition'] = cols[1].text_input("Condição Médica", value=item.get('medical_condition', ''), key=f"fam_cond_{unique_key}")
            if cols[2].button("❌", key=f"remove_{unique_key}", help="Remover histórico"):
                items_list.pop(i)
                st.rerun()

    if st.button(add_button_label, key=f"add_{key_prefix}"):
        items_list.append({})
        st.rerun()

# --- FUNÇÃO DE SUBMISSÃO PARA A API ---
def create_patient():
    """Valida, formata e envia os dados do paciente para a API."""
    
    # 1. Validação dos campos obrigatórios
    required_fields = [full_name, email, password, birthdate, biological_sex, weight, ancestry]
    if not all(required_fields):
        st.error("Por favor, preencha todos os campos obrigatórios (*) em 'Informações do Paciente'.")
        return

    # 2. Formatação dos dados para o payload da API
    # Filtra registros vazios e converte datas para string no formato ISO
    medical_record_data = {
        "conditions": [
            {**c, 'diagnosis_date': c['diagnosis_date'].isoformat()}
            for c in st.session_state.conditions if c.get('condition_name')
        ],
        "allergies": [
            {**a, 'discovery_date': a['discovery_date'].isoformat()}
            for a in st.session_state.allergies if a.get('substance')
        ],
        "medications": [
            {**m, 'treatment_start_date': m['treatment_start_date'].isoformat()}
            for m in st.session_state.medications if m.get('medication_name')
        ],
        "injuries": [
            {**i, 'occurrence_date': i['occurrence_date'].isoformat()}
            for i in st.session_state.injuries if i.get('injury_description')
        ],
        "family_histories": [
            f for f in st.session_state.family_histories if f.get('medical_condition')
        ],
        "free_user_text": free_user_text
    }

    # Monta o payload final 
    patient_payload = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "birthdate": birthdate.isoformat(),
        "biological_sex": SEX_MAP.get(biological_sex), # Mapeia para o valor do Enum
        "weight": weight,
        "ancestry": ANCESTRY_MAP.get(ancestry), # Mapeia para o valor do Enum
        "medical_record": medical_record_data
    }

    try:
        response = requests.post(f"{API_URL}/patients/", json=patient_payload)

        if response.status_code == 201: 
            st.session_state["account_created"] = True

        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Ocorreu um erro.')
            st.error(f"Erro ao criar conta: {error_detail}")
        elif response.status_code == 422:
            st.error("Erro de validação nos dados enviados. Verifique os campos.")
            st.json(response.json())
        else:
            st.error(f"Ocorreu um erro inesperado no servidor. Status: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao servidor. Verifique se o backend está em execução.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")


# --- LAYOUT PRINCIPAL DA PÁGINA ---
st.set_page_config(page_title="Cadastro", page_icon="📝")
create_header()

initialize_session_state()

st.title("Formulário de Cadastro")
st.markdown("Preencha suas informações abaixo para criar uma conta.")

# --- Seção 1: Informações do Paciente ---
with st.container(border=True):
    st.header("Informações Pessoais")
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Nome Completo *")
        email = st.text_input("E-mail *")
        password = st.text_input("Senha *", type="password", help="Mínimo de 8 caracteres.")
    with col2:
        birthdate = st.date_input("Data de Nascimento *", min_value=date(1900, 1, 1), max_value=date.today())
        biological_sex = st.selectbox("Sexo Biológico *", SEX_MAP.keys())
        c1, c2 = st.columns(2)
        weight = c1.number_input("Peso (kg) *", min_value=0.0, format="%.2f")
        ancestry = c2.selectbox("Etnia *", ANCESTRY_MAP.keys())


st.markdown("---")

# --- Histórico Médico (Seções Dinâmicas) ---
with st.container(border=True):
    st.header("Histórico Médico")
    st.info("Clique no botão 'Adicionar' em cada seção para incluir um novo registro.")

    render_dynamic_section("Condições Médicas", st.session_state.conditions, "Adicionar Condição Médica", "cond")
    st.markdown("<br>", unsafe_allow_html=True)
    render_dynamic_section("Alergias", st.session_state.allergies, "Adicionar Alergia", "allergy")
    st.markdown("<br>", unsafe_allow_html=True)
    render_dynamic_section("Medicamentos Prescritos", st.session_state.medications, "Adicionar Medicamento", "med")
    st.markdown("<br>", unsafe_allow_html=True)
    render_dynamic_section("Histórico de Lesões", st.session_state.injuries, "Adicionar Lesão", "injury")
    st.markdown("<br>", unsafe_allow_html=True)
    render_dynamic_section("Histórico Familiar", st.session_state.family_histories, "Adicionar Histórico Familiar", "fam")

with st.container(border=True):
    st.header("Informações Adicionais")
    free_user_text = st.text_area(
        "Há algo mais que você gostaria de compartilhar?",
        placeholder="Descreva aqui seus hábitos (alimentação, exercícios, sono), estilo de vida, sintomas não diagnosticados, preocupações com a saúde ou qualquer outra informação que considere relevante...",
        max_chars=5000,
        height=250,
        help="Este campo é opcional, mas informações detalhadas podem auxiliar na análise."
    )

st.markdown("---")

# --- ENVIO FINAL ---
if st.button("Criar Conta", type="primary", on_click=create_patient, use_container_width=True):
    if st.session_state["account_created"] == True:
        st.success("Conta criada com sucesso! Você já pode fazer o login.")
        st.balloons()
        st.switch_page("./app.py") # redirects to login page

