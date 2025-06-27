import streamlit as st
import pandas as pd
from utils import carregar_dados # Importa a função do arquivo utils.py
from utils import check_password  # Importa a função de autenticação do arquivo 0_login.py
from utils import logout  # Importa a função de logout do arquivo utils.py

# --- CONFIGURAÇÃO DA PÁGINA ---
# st.set_page_config deve ser o primeiro comando Streamlit.
st.logo('logo.png')

if st.session_state["authenticated"]:
    st.title("Visor de Ativos - Segtrônica")
    st.subheader("Lista de Ativos Cadastrados")

    # --- CARREGAMENTO DOS SEGREDOS ---
    try:
        SHEET_URL_ATIVOS = st.secrets["SHEET_URL_ATIVOS"]
        FORM_URL_CADASTRO = st.secrets["FORM_URL"]
    except KeyError as e:
        st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado! Verifique o painel do Streamlit.")
        st.stop()

    # --- CARREGAMENTO E EXIBIÇÃO DOS DADOS ---
    df_ativos = carregar_dados(SHEET_URL_ATIVOS)

    if not df_ativos.empty:
        # Filtros na barra lateral para facilitar a busca
        st.sidebar.header("Filtros")
        filtro_cliente = st.sidebar.text_input("Filtrar por Cliente")
        filtro_tipo = st.sidebar.text_input("Filtrar por Tipo de Ativo")
        filtro_id = st.sidebar.text_input("Filtrar por ID do Ativo")

        df_filtrado = df_ativos.copy()
        if filtro_cliente:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(filtro_cliente, case=False, na=False)]
        if filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['Tipo do Ativo'].str.contains(filtro_tipo, case=False, na=False)]
        if filtro_id:
            df_filtrado = df_filtrado[df_filtrado['ID DO ATIVO'].str.contains(filtro_id, case=False, na=False)]

        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("Nenhum ativo encontrado ou falha ao carregar os dados.")

    st.sidebar.info("Para ver os detalhes de um ativo, escaneie o QR Code ou navegue até a página 'Detalhes do Ativo' e insira o ID.")
    if st.sidebar.button("Logout"):
        logout()