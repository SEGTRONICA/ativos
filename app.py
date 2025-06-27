import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Ativos - Segtrônica",
    page_icon="logo.png"
)

pages = [
    st.Page("pages/0_login.py", title="Login"),
]   
pg = st.navigation(pages)
pg.run()

if st.session_state["authenticated"]:
    pages = [
        st.Page("pages/1_ativo.py", title="Detalhes do Ativo"),
        st.Page("pages/2_home.py", title="Home")
    ]   
    pg = st.navigation(pages)
    pg.run()

