import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# Função para salvar os dados na planilha
def salvar_paciente(paciente):
    pacientes_sheet.append_row([
        paciente["Nome Completo"],
        paciente["Telefone"],
        paciente["Endereço"],
        paciente["Responsável Familiar"],
        paciente["Contato Responsável"],
        paciente["Operação"],
        ", ".join(paciente["Profissionais"])
    ])
    st.success("Paciente salvo com sucesso!")

def salvar_profissional(profissional):
    profissionais_sheet.append_row([
        profissional["Nome Completo"],
        profissional["Telefone"],
        profissional["Endereço"],
        profissional["Serviço"],
        ", ".join(profissional["Pacientes"])
    ])
    st.success("Profissional salvo com sucesso!")

def salvar_vinculo(vinculo):
    vinculos_sheet.append_row([
        vinculo["Paciente"],
        vinculo["Profissional"],
        vinculo["Data"],
        vinculo["Período"]
    ])
    st.success("Vínculo salvo com sucesso!")

# Interface do Streamlit
st.title("Sistema de Cadastro - Pacientes e Profissionais")

menu = st.sidebar.selectbox("Escolha uma opção", [
    "Cadastrar Paciente",
    "Cadastrar Profissional",
    "Buscar Paciente",
    "Buscar Profissional",
    "Vincular Paciente e Profissional"
])

# Cadastro de Paciente
if menu == "Cadastrar Paciente":
    st.subheader("Cadastro de Paciente")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    responsavel = st.text_input("Responsável Familiar")
    contato_resp = st.text_input("Contato do Responsável")
    operacao = st.selectbox("Operação", ["Labi", "AssistCare", "Outra"])

    profissionais_lista = profissionais_df["Nome Completo"].tolist() if "Nome Completo" in profissionais_df.columns else []
    profissionais_selecionados = st.multiselect("Profissionais Responsáveis", profissionais_lista)

    if st.button("Salvar Paciente"):
        novo_paciente = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Responsável Familiar': responsavel,
            'Contato Responsável': contato_resp,
            'Operação': operacao,
            'Profissionais': profissionais_selecionados
        }
        salvar_paciente(novo_paciente)

# Cadastro de Profissional
elif menu == "Cadastrar Profissional":
    st.subheader("Cadastro de Profissional")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    servico = st.selectbox("Serviço", ["Fisioterapia", "Fonoaudiologia", "Outro"])

    pacientes_lista = pacientes_df["Nome Completo"].tolist() if "Nome Completo" in pacientes_df.columns else []
    pacientes_selecionados = st.multiselect("Pacientes Atendidos", pacientes_lista)

    if st.button("Salvar Profissional"):
        novo_profissional = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Serviço': servico,
            'Pacientes': pacientes_selecionados
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
    paciente_lista = pacientes_df["Nome Completo"].tolist() if "Nome Completo" in pacientes_df.columns else []
    profissional_lista = profissionais_df["Nome Completo"].tolist() if "Nome Completo" in profissionais_df.columns else []

    paciente = st.selectbox("Escolha um paciente", paciente_lista)
    profissional = st.selectbox("Escolha um profissional", profissional_lista)
    data = st.date_input("Data do Atendimento")
    periodo = st.selectbox("Período", ["Manhã", "Tarde", "Noite"])

    if st.button("Salvar Vínculo"):
        vinculo = {
            'Paciente': paciente,
            'Profissional': profissional,
            'Data': str(data),
            'Período': periodo
        }
        salvar_vinculo(vinculo)

# Mostrar Vínculos Atuais
st.subheader("Vínculos Atuais")
st.write("**Pacientes Cadastrados**")
st.dataframe(pacientes_df)
st.write("**Profissionais Cadastrados**")
st.dataframe(profissionais_df)
st.write("**Vínculos Registrados**")
st.dataframe(vinculos_df)
