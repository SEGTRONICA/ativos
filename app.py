import streamlit as st
import pandas as pd
import time
import urllib.error

# --- CÓDIGO DE DEPURACIÓN AVANÇADA PARA PROBLEMAS DE CONEXÃO ---

st.set_page_config(layout="centered", page_title="Depurador Avançado")
st.title("Depurador de Conexão")
st.write("Este código tenta diagnosticar problemas de conexão entre o Streamlit e o Google Sheets.")
st.write("---")

# 1. Carrega os segredos
try:
    SHEET_URL = st.secrets["SHEET_URL"]
    st.success("Segredo 'SHEET_URL' carregado com sucesso.")
except KeyError:
    st.error("ERRO: O segredo 'SHEET_URL' não foi encontrado!")
    st.stop()

# 2. Monta a URL de download do CSV, agora com um "cache buster" para forçar uma nova conexão
csv_url_base = SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
cache_buster = f"&dummy_cache_buster={int(time.time())}"
csv_url_final = csv_url_base + cache_buster

st.header("URL de Acesso Final")
st.info("O Streamlit tentará acessar a seguinte URL para baixar os dados:")
st.code(csv_url_final, language="text")

# 3. Tenta carregar os dados com tratamento de erro detalhado
st.header("Tentativa de Conexão")
try:
    st.write("Tentando `pd.read_csv(url)`...")
    df = pd.read_csv(csv_url_final)
    st.success("SUCESSO! A planilha foi carregada e lida pelo Pandas!")
    st.write("Amostra dos dados:")
    st.dataframe(df.head())

except urllib.error.HTTPError as e:
    st.error(f"ERRO DE HTTP: O servidor do Google retornou um código de erro.")
    st.write(f"**Código de Status:** {e.code}")
    st.write(f"**Motivo:** {e.reason}")
    st.write("Isso geralmente significa um problema de permissão que afeta apenas o servidor. Verifique as permissões da planilha novamente como garantia.")

except Exception as e:
    st.error(f"ERRO INESPERADO ao tentar ler a URL com o Pandas.")
    st.write(f"**Tipo de Erro:** {type(e).__name__}")
    st.write(f"**Mensagem de Erro:** {e}")
    st.info("Isso pode ser um problema de rede intermitente nos servidores do Streamlit ou um formato de CSV inválido.")
