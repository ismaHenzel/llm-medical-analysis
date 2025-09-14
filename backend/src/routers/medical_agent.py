import operator
import os
import uuid
from http import HTTPStatus
from typing import Annotated, Dict, List, TypedDict

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import (AIMessage, AnyMessage, BaseMessage,
                                     HumanMessage)
from langchain_core.pydantic_v1 import BaseModel as PydanticV1BaseModel
from langchain_core.pydantic_v1 import Field as PydanticV1Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from src.models import Patient
from src.schemas.medical_agent import (ChatHistoryResponse, ChatMessage,
                                       ChatRequest)
from src.security import get_current_user

CurrentPatient = Annotated[Patient, Depends(get_current_user)]

router = APIRouter()

search_tool = TavilySearch(max_results=5)
tools = [search_tool]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    patient_record: dict
    question_count: int


AGENT_PROMPT = """
Você é um assistente médico virtual altamente inteligente e cauteloso. Sua função é ajudar pacientes a entenderem seus sintomas através de uma conversa contínua.

**NUNCA** forneça um diagnóstico definitivo. Sua tarefa é fazer perguntas para esclarecer os sintomas, sugerir possibilidades e, eventualmente, direcionar o paciente para o especialista correto.

**REGRAS CRÍTICAS:**
1.  **Conversa Contínua:** Mantenha um diálogo com o paciente. Faça uma pergunta por vez para coletar informações.
2.  **Contexto:** Foque nas últimas 20 mensagens para manter o contexto da conversa atual.
3.  **Lógica de Palpite:** A cada 5 perguntas que você fizer:
    - busque na internet com a ferramenta search_tool para possuir mais embasamento
    - Após isso, analise bem as últimas conversas realizadas, a busca na internet e no final você deve fornecer um "palpite" ou uma "hipótese preliminar" com base nas informações coletadas até o momento. Deixe claro que é apenas uma possibilidade. Após dar o palpite, você PODE e DEVE continuar fazendo mais perguntas se necessário.
4.  **Evite Redundância:** Antes de fazer uma nova pergunta, revise o histórico da conversa. **NÃO FAÇA** perguntas cujas respostas já foram fornecidas.
5.  **Use a Busca:** Se os sintomas ou a combinação com o histórico do paciente não forem claros, use a ferramenta de busca (`search_tool`) para pesquisar informações médicas relevantes.

**FICHA MÉDICA DO PACIENTE:**
{patient_record}
"""

def agent_analyst_node(state: AgentState):
    """
    Analisa o estado atual, decide se dá um palpite, faz uma pergunta ou usa uma ferramenta.
    """
    question_count = state.get('question_count', 0)
    context_messages = state['messages'][-20:]

    system_prompt = AGENT_PROMPT.format(patient_record=str(state.get('patient_record', {})))
    
    # Adiciona uma instrução especial se for hora de dar um palpite.
    if question_count > 0 and question_count % 3 == 0:
        hunch_instruction = (
            "INSTRUÇÃO ESPECIAL: Você já fez 3 perguntas. Com base no histórico da conversa, "
            "forneça um palpite preliminar sobre as possíveis causas dos sintomas. "
            "Use frases como 'Uma possibilidade poderia ser...', 'Com base no que você disse, talvez devêssemos considerar...'. "
            "Você pode fazer outra pergunta na mesma resposta se achar necessário para continuar a investigação."
            "No final de seu palpite, diga quais os profissionais da saúde são mais adequados a serem buscados, como por exemplo um médico cardiologista."
        )
        messages_with_prompt = [HumanMessage(content=system_prompt), HumanMessage(content=hunch_instruction)] + context_messages
    else:
        messages_with_prompt = [HumanMessage(content=system_prompt)] + context_messages
    
    ai_response = llm_with_tools.invoke(messages_with_prompt)
    
    new_question_count = question_count
    if not ai_response.tool_calls:
        new_question_count += 1
        
    return {"messages": [ai_response], "question_count": new_question_count}

def should_continue_edge(state: AgentState) -> str:
    """
    Decide o próximo passo: usar uma ferramenta ou terminar o turno.
    """
    last_message = state['messages'][-1]
    # Se a última mensagem contém uma chamada de ferramenta, vá para o nó de ação.
    if last_message.tool_calls:
        return "continue_to_tool"

    # Caso contrário, é uma resposta direta ao usuário, então o turno termina.
    return "end_turn"

@router.post("/chat/", response_model=ChatMessage)
def chat_endpoint(request: ChatRequest, current_patient: CurrentPatient):
    """
    Recebe uma mensagem do usuário e retorna a resposta do agente.
    """
    if current_patient.id != int(request.thread_id):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    config = {"configurable": {"thread_id": request.thread_id}}
    
    graph_input = {
        "messages": [HumanMessage(content=request.message)],
        "patient_record": request.patient_record,
    }
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not set")
        
    with PostgresSaver.from_conn_string(db_url) as checkpointer:
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent_analyst", agent_analyst_node)
        graph_builder.add_node("action_tool", tool_node)
        
        graph_builder.set_entry_point("agent_analyst")
        
        graph_builder.add_conditional_edges(
            "agent_analyst", 
            should_continue_edge, 
            {
                "continue_to_tool": "action_tool", 
                "end_turn": END
            }
        )
        graph_builder.add_edge("action_tool", "agent_analyst")
        graph = graph_builder.compile(checkpointer=checkpointer)
        final_state = graph.invoke(graph_input, config)
        last_message = final_state["messages"][-1]
        
        content = ""
        if isinstance(last_message, AIMessage):
            content = last_message.content

        return ChatMessage(role="assistant", content=content)

@router.get("/chat/{patient_id}", response_model=ChatHistoryResponse)
def get_history_endpoint(patient_id: int, current_patient: CurrentPatient):
    """
    Retorna o histórico de mensagens para uma determinada thread (paciente).
    """

    if current_patient.id != patient_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    config = {"configurable": {"thread_id": str(patient_id)}}
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return ChatHistoryResponse(messages=[])
    try:
        with PostgresSaver.from_conn_string(db_url) as checkpointer:
            thread_state = checkpointer.get(config)
            messages = []
            if thread_state and 'channel_values' in thread_state and 'messages' in thread_state['channel_values']:
                raw_messages = thread_state['channel_values']['messages']
                for msg in raw_messages:
                    if isinstance(msg, dict):
                       msg_obj = BaseMessage(**msg)
                    else:
                       msg_obj = msg
                       
                    if isinstance(msg_obj, HumanMessage):
                        messages.append(ChatMessage(role="user", content=msg_obj.content))
                    elif isinstance(msg_obj, AIMessage) and msg_obj.content:
                        messages.append(ChatMessage(role="assistant", content=msg_obj.content))
            
            return ChatHistoryResponse(messages=messages)
    except Exception as e:
        print(f"Error fetching history for thread {patient_id}: {e}")
        return ChatHistoryResponse(messages=[])
