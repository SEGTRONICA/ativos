import streamlit as st

# Adiciona o logo na barra lateral
st.logo('logo.png')
def check_password():
    
    """Retorna `True` se o usuário inseriu a senha correta."""
    usernames = st.secrets["credentials"]["usernames"]
    passwords = st.secrets["credentials"]["passwords"]
    # 1. Inicializa o estado da sessão para autenticação se ainda não existir.
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # 2. Se o usuário já estiver autenticado, mostra uma mensagem de sucesso.
    if st.session_state["authenticated"]:
        return True

    # 3. Cria o formulário de login.
    with st.form("login"):
        st.title("Login")
        st.write("Por favor, insira suas credenciais para continuar.")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            try:
                if usernames.index(username) == passwords.index(password):
                    st.session_state["authenticated"] = True
                    st.rerun() # Recarrega a página para mostrar o estado de "logado"
            except ValueError:
                st.error("Usuário ou senha incorretos.")
    return False

# --- Execução da verificação de senha ---
check_password()

