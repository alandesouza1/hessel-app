# app.py
import streamlit as st
import pandas as pd

# Inicializa as tabelas em sessão se ainda não existirem
if 'pacientes' not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=[
        'Nome Completo', 'Telefone', 'Endereço', 'Responsável Familiar', 'Contato Responsável', 'Operação', 'Profissionais']
    )

if 'profissionais' not in st.session_state:
    st.session_state.profissionais = pd.DataFrame(columns=[
        'Nome Completo', 'Telefone', 'Endereço', 'Serviço', 'Pacientes']
    )

st.title("Sistema de Cadastro - Pacientes e Profissionais")

menu = st.sidebar.selectbox("Escolha uma opção", ["Cadastrar Paciente", "Cadastrar Profissional", "Buscar Paciente", "Buscar Profissional"])

# Função para mostrar os vínculos

def mostrar_vinculos():
    st.subheader("Vínculos atuais")
    st.write("**Pacientes**")
    st.dataframe(st.session_state.pacientes)
    st.write("**Profissionais**")
    st.dataframe(st.session_state.profissionais)

# Cadastro de Paciente
if menu == "Cadastrar Paciente":
    st.subheader("Cadastro de Paciente")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    responsavel = st.text_input("Responsável Familiar")
    contato_resp = st.text_input("Contato do Responsável")
    operacao = st.selectbox("Operação", ["Labi", "AssistCare", "Outra"])

    profissionais = st.multiselect("Profissionais Responsáveis", st.session_state.profissionais['Nome Completo'].tolist())

    if st.button("Salvar Paciente"):
        novo = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Responsável Familiar': responsavel,
            'Contato Responsável': contato_resp,
            'Operação': operacao,
            'Profissionais': profissionais
        }
        st.session_state.pacientes = pd.concat([st.session_state.pacientes, pd.DataFrame([novo])], ignore_index=True)

        for prof in profissionais:
            idx = st.session_state.profissionais[st.session_state.profissionais['Nome Completo'] == prof].index
            if not idx.empty:
                atual = st.session_state.profissionais.at[idx[0], 'Pacientes']
                if not isinstance(atual, list):
                    atual = []
                atual.append(nome)
                st.session_state.profissionais.at[idx[0], 'Pacientes'] = atual
        st.success("Paciente salvo com sucesso!")

# Cadastro de Profissional
elif menu == "Cadastrar Profissional":
    st.subheader("Cadastro de Profissional")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    servico = st.selectbox("Serviço", ["Fisioterapia", "Fonoaudiologia", "Outro"])

    pacientes = st.multiselect("Pacientes Atendidos", st.session_state.pacientes['Nome Completo'].tolist())

    if st.button("Salvar Profissional"):
        novo = {
            'Nome Completo': nome,
            'Telefone': telefone,
            'Endereço': endereco,
            'Serviço': servico,
            'Pacientes': pacientes
        }
        st.session_state.profissionais = pd.concat([st.session_state.profissionais, pd.DataFrame([novo])], ignore_index=True)

        for pac in pacientes:
            idx = st.session_state.pacientes[st.session_state.pacientes['Nome Completo'] == pac].index
            if not idx.empty:
                atual = st.session_state.pacientes.at[idx[0], 'Profissionais']
                if not isinstance(atual, list):
                    atual = []
                atual.append(nome)
                st.session_state.pacientes.at[idx[0], 'Profissionais'] = atual
        st.success("Profissional salvo com sucesso!")

# Buscar Paciente
elif menu == "Buscar Paciente":
    st.subheader("Buscar Paciente")
    nome = st.text_input("Digite o nome do paciente")
    if st.button("Buscar"):
        resultados = st.session_state.pacientes[st.session_state.pacientes['Nome Completo'].str.contains(nome, case=False)]
        if not resultados.empty:
            st.dataframe(resultados)
        else:
            st.warning("Paciente não encontrado.")

# Buscar Profissional
elif menu == "Buscar Profissional":
    st.subheader("Buscar Profissional")
    nome = st.text_input("Digite o nome do profissional")
    if st.button("Buscar"):
        resultados = st.session_state.profissionais[st.session_state.profissionais['Nome Completo'].str.contains(nome, case=False)]
        if not resultados.empty:
            st.dataframe(resultados)
        else:
            st.warning("Profissional não encontrado.")

mostrar_vinculos()