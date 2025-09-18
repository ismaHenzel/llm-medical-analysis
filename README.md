## Objetivo Geral

Desenvolver um software, no formato de um chatbot, para auxiliar na identificação preliminar de patologias e no aconselhamento para a busca de profissionais de saúde adequados, com base em informações do cotidiano e histórico médico do usuário.

## ⚙️ Funcionalidades

Interface de Conversação: Permite que o usuário interaja com o LLM de forma intuitiva, devendo informar ao menos três sintomas para receber uma hipótese diagnóstica e a indicação de qual especialista procurar.

Cadastro de Usuário: Interface para o usuário fornecer dados pessoais e histórico médico, como medicamentos de uso contínuo. As informações são coletadas por meio de formulários estruturados e campos de texto livre.

Login de Usuário: Permite o acesso seguro à interface de conversação mediante a inserção de e-mail e senha cadastrados, utiliza criptografia argon2 na senha, bem como todas as rotas necesśarias validam a conexão com token Jwt.

## Tecnologias Utilizadas

### Backend:

Linguagem de Programação: ![Python](https://img.shields.io/badge/-Python-000?&logo=Python)\
Framework: ![FastAPi](https://img.shields.io/badge/-FastApi-000?&logo=FastApi)\
ORM: ![SqlAlchemy](https://img.shields.io/badge/-SqlAlchemy-000?&logo=SqlAlchemy)\
Validação de Dados: ![Pydantic](https://img.shields.io/badge/-Pydantic-000?&logo=Pydantic)\
Migrações no banco de dados: ![Alembic](https://img.shields.io/badge/-Alembic-000?&logo=Alembic)\
Testes: ![Pytest](https://img.shields.io/badge/-Pytest-000?&logo=Pytest)\
Segurança: ![JWT](https://img.shields.io/badge/JWT-black?logo=JSON%20web%20tokens)

### Frontend:
Linguagem de Programação: ![Python](https://img.shields.io/badge/-Python-000?&logo=Python)\
Biblioteca: ![Streamlit](https://img.shields.io/badge/-Streamlit-000?&logo=Streamlit)

### Banco de Dados:
SGBD:  ![PostgreSql](https://img.shields.io/badge/-PostgreSql-000?&logo=postgresql) 

### Inteligência Artificial:
Orquestração: ![Langgraph](https://img.shields.io/badge/-Langgraph-000?&logo=Langgraph)\
LLM: ![Gemini](https://img.shields.io/badge/-Gemini-000?&logo=google%20gemini)

### Ambiente Operacional:
Conteinerização: ![Docker](https://img.shields.io/badge/-Docker-000?&logo=Docker)\
Sistema Operacional: ![Arch Linux](https://img.shields.io/badge/-Arch%20Linux-000?&logo=Linux)

## Arquitetura do Software

O sistema é composto por um backend desenvolvido em Python com FastAPI e um frontend em Streamlit. O backend gerencia toda a lógica de negócio, incluindo o CRUD de pacientes e a interação com o agente de IA, que utiliza o Gemini 2.5 Pro para analisar os sintomas e o histórico do usuário. A comunicação entre o frontend e o backend é realizada de forma segura através de uma API RESTful com autenticação JWT. O banco de dados PostgreSQL armazena as informações dos usuários, e todo o ambiente é conteinerizado com Docker.
![Arquitetura](./assets/architecture.png)

### Como Executar o Projeto
Para reproduzir o ambiente, é necessário ter o Docker e o Docker Compose instalados.

Clone o repositório:

```
git clone [https://github.com/ismaHenzel/llm-medical-analysis.git](https://github.com/ismaHenzel/llm-medical-analysis.git)
```

Configure as variáveis de ambiente:
No diretório do backend, crie um arquivo .env e adicione as suas chaves de API para o Gemini 2.5 Pro e a Tavily. Essas variáveis não foram disponibilizadas no repositório.

Exemplo de .env:
``` 
JWT_SECRET_KEY=yIQOGPCMafIbo9y6ZHdU1y+Edlm9Ges38myrZHq9KKdlbjSrzNnUv88IgZi+Vv2q
DATABASE_URL="postgresql://postgres:changeme@postgres:5432/medical_analysis"
TAVILY_API_KEY="your api key"
GOOGLE_API_KEY="your api key"
```

No diretório backend, execute o comando:
```
docker-compose up -d --build
```

No diretório frontend, execute o comando:
```
docker-compose up -d --build
```

(Sempre execute primeiro o backend, já que ele cria um network utilizado no frontend)

## ✅ Resultados e Validação
O protótipo foi validado com sucesso em três cenários fictícios e um caso de uso real, demonstrando bons resultados em identificar corretamente as possíveis patologias em cenários simples e o especialista adequado a ser procurado.

### Cenários Fictícios Diagnosticados Corretamente:

* Crise de enxaqueca

* Cólica biliar

* Síndrome serotoninérgica

### Testes (Conversas com o Chatbot em PDF):
[conversations](https://github.com/ismaHenzel/llm-medical-analysis/tree/main/results/conversations)

### Fichas Médicas Utilizadas nos Testes:
[users](https://github.com/ismaHenzel/llm-medical-analysis/tree/main/results/auto_create_users)

## Considerações Finais e Trabalhos Futuros

Apesar dos resultados promissores, reconhece-se a necessidade de testes mais amplos. Como trabalhos futuros, sugere-se:

* Implementação de uma base de dados local com informações sobre doenças, medicamentos, lesões e alergias para a utilização de RAG (Retrieval-Augmented Generation) com grafos e buscas vetoriais para enriquecer o conhecimento do agente.  

* Implementação de um servidor MCP, com a adição de novas ferramentas para o llm.

* Adição de funcionalidades como validação de e-mails, refatoração de rotas para operações assíncronas e a possibilidade de análise de imagens e documentos, como exames clínicos.
