import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Autenticação com a API do Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
gc = gspread.authorize(credentials)

# Conectar à planilha do Google Sheets
spreadsheet = gc.open("hessel-consulta")
pacientes_sheet = spreadsheet.worksheet("Pacientes")
profissionais_sheet = spreadsheet.worksheet("Profissionais")
vinculos_sheet = spreadsheet.worksheet("Vinculos")

# Inicializa as tabelas com os dados da planilha
def carregar_dados():
    pacientes = pd.DataFrame(pacientes_sheet.get_all_records())
    profissionais = pd.DataFrame(profissionais_sheet.get_all_records())
    vinculos = pd.DataFrame(vinculos_sheet.get_all_records())
    return pacientes, profissionais, vinculos

pacientes_df, profissionais_df, vinculos_df = carregar_dados()

# 👀 Debug: Ver colunas da aba profissionais
st.write("Colunas de profissionais_df:", profissionais_df.columns.tolist())

# Interface do Streamlit
st.title("Sistema de Cadastro - Pacientes e Profissionais")

menu = st.sidebar.selectbox("Escolha uma opção", [
    "Cadastrar Paciente", 
    "Cadastrar Profissional", 
    "Buscar Paciente", 
    "Buscar Profissional", 
    "Vincular Paciente e Profissional"
])

# Funções para salvar dados
def salvar_paciente(paciente):
    pacientes_sheet.append_row([
        paciente["Nome Completo"], paciente["Telefone"], paciente["Endereço"],
        paciente["Responsável Familiar"], paciente["Contato Responsável"], paciente["Operação"],
        ", ".join(paciente["Profissionais"])
    ])
    st.success("Paciente salvo com sucesso!")

def salvar_profissional(profissional):
    profissionais_sheet.append_row([
        profissional["Nome Completo"], profissional["Telefone"], profissional["Endereço"],
        profissional["Serviço"], ", ".join(profissional["Pacientes"])
    ])
    st.success("Profissional salvo com sucesso!")

def salvar_vinculo(vinculo):
    vinculos_sheet.append_row([
        vinculo["Paciente"], vinculo["Profissional"], vinculo["Data"], vinculo["Período"]
    ])
    st.success("Vínculo salvo com sucesso!")

# Cadastro de Paciente
if menu == "Cadastrar Paciente":
    st.subheader("Cadastro de Paciente")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    responsavel = st.text_input("Responsável Familiar")
    contato_resp = st.text_input("Contato do Responsável")
    operacao = st.selectbox("Operação", ["Labi", "AssistCare", "Outra"])

    profissionais = st.multiselect("Profissionais Responsáveis", profissionais_df["Nome Completo"].tolist())

    if st.button("Salvar Paciente"):
        novo_paciente = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Responsável Familiar': responsavel,
            'Contato Responsável': contato_resp,
            'Operação': operacao,
            'Profissionais': profissionais
        }
        salvar_paciente(novo_paciente)

# Cadastro de Profissional
elif menu == "Cadastrar Profissional":
    st.subheader("Cadastro de Profissional")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    servico = st.selectbox("Serviço", ["Fisioterapia", "Fonoaudiologia", "Outro"])

    pacientes = st.multiselect("Pacientes Atendidos", pacientes_df["Nome Completo"].tolist())

    if st.button("Salvar Profissional"):
        novo_profissional = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Serviço': servico,
            'Pacientes': pacientes
        }
        salvar_profissional(novo_profissional)

# Buscar Paciente
elif menu == "Buscar Paciente":
    st.subheader("Buscar Paciente")
    nome = st.text_input("Digite o nome do paciente")
    if st.button("Buscar"):
        resultados = pacientes_df[pacientes_df['Nome Completo'].str.contains(nome, case=False)]
        if not resultados.empty:
            st.dataframe(resultados)
        else:
            st.warning("Paciente não encontrado.")

# Buscar Profissional
elif menu == "Buscar Profissional":
    st.subheader("Buscar Profissional")
    nome = st.text_input("Digite o nome do profissional")
    if st.button("Buscar"):
        resultados = profissionais_df[profissionais_df['Nome Completo'].str.contains(nome, case=False)]
        if not resultados.empty:
            st.dataframe(resultados)
        else:
            st.warning("Profissional não encontrado.")

# Vincular Paciente e Profissional
elif menu == "Vincular Paciente e Profissional":
    st.subheader("Vincular Paciente e Profissional")
    paciente = st.selectbox("Escolha um paciente", pacientes_df["Nome Completo"].tolist())
    profissional = st.selectbox("Escolha um profissional", profissionais_df["Nome Completo"].tolist())
    data = st.date_input("Data do Atendimento")
    periodo = st.selectbox("Período", ["Manhã", "Tarde", "Noite"])

    if st.button("Salvar Vinculo"):
        vinculo = {
            'Paciente': paciente,
            'Profissional': profissional,
            'Data': str(data),
            'Período': periodo
        }
        salvar_vinculo(vinculo)

# Mostrar Vínculos atuais
st.subheader("Vínculos Atuais")
st.write("**Pacientes**")
st.dataframe(pacientes_df)
st.write("**Profissionais**")
st.dataframe(profissionais_df)
