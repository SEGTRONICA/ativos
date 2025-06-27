import streamlit as st
import pandas as pd

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
# Esta função é colocada em um arquivo separado (utils.py) para que possa ser
# reutilizada por várias páginas sem duplicar o código.
# O cache é mantido para otimizar o carregamento dos dados.

def logout():
    """Limpa o estado de autenticação e recarrega a página."""
    st.session_state["authenticated"] = False
    st.rerun()
    
@st.cache_data(ttl=60)
def carregar_dados(url_completa):
    """
    Carrega dados de uma URL de planilha do Google Sheets.

    Args:
        url_completa (str): A URL completa para o arquivo CSV da planilha.

    Returns:
        pd.DataFrame: Um DataFrame com os dados carregados ou um DataFrame vazio em caso de erro.
    """
    try:
        # A URL já vem pronta dos segredos, não precisa mais do .replace()
        # O dtype=str garante que IDs e outros números não sejam interpretados incorretamente.
        df = pd.read_csv(url_completa, dtype=str)
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da URL: {e}")
        return pd.DataFrame()

def check_password():
    """Retorna `True` se o usuário inseriu a senha correta."""

    # 1. Inicializa o estado da sessão para autenticação se ainda não existir.
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # 2. Se o usuário já estiver autenticado, mostra uma mensagem de sucesso.
    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun() # Recarrega a página para mostrar o formulário de login novamente
        return True

    # 3. Cria o formulário de login.
    with st.form("login"):
        st.title("Login")
        st.write("Por favor, insira suas credenciais para continuar.")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        # 4. Verifica as credenciais quando o formulário é enviado.
        #    IMPORTANTE: Em um aplicativo real, use st.secrets para armazenar credenciais!
        #    Ex: st.secrets["password"] == password
        if submitted:
            if username == "segtronica" and password == "1234":
                st.session_state["authenticated"] = True
                st.rerun() # Recarrega a página para mostrar o estado de "logado"
            else:
                st.error("Usuário ou senha incorretos.")
    return False
