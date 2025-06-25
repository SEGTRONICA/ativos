import streamlit as st
import pandas as pd

# --- CÓDIGO DE PRODUÇÃO FINAL (VERSÃO "COPIAR E COLAR") ---

st.set_page_config(layout="centered", page_title="Visor de Ativos")
st.title("Visor de Ativos")

try:
    SHEET_URL = st.secrets["SHEET_URL"]
    FORM_URL = st.secrets["FORM_URL"]
except KeyError as e:
    st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado!")
    st.stop()

def carregar_dados(url):
    csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
    try:
        df = pd.read_csv(csv_url)
        df['ID DO ATIVO'] = df['ID DO ATIVO'].astype(str)
        return df
    except Exception:
        return pd.DataFrame()

query_params = st.query_params
id_ativo_escaneado = query_params.get("id_ativo")

if not id_ativo_escaneado:
    st.info("Bem-vindo! Escaneie o QR Code de um ativo para começar.")
else:
    df = carregar_dados(SHEET_URL)
    
    if df.empty and 'ID DO ATIVO' not in df.columns:
        st.error("Não foi possível carregar os dados ou a coluna 'ID DO ATIVO' não foi encontrada. Verifique a planilha.")
    else:
        ativo_info = df[df['ID DO ATIVO'] == id_ativo_escaneado]
        if not ativo_info.empty:
            st.success(f"Ativo encontrado!")
            ativo = ativo_info.iloc[0]
            st.header(ativo['Nome do dispositivo'])
            st.subheader(ativo['Tipo do Ativo'])
            st.write(f"Numero do Pedido: {ativo['Numero do Pedido']}")
            st.write(f"**Localização:** {ativo['Cliente']}")
            st.write(f"**Modelo do Ativo**: {ativo['Modelo do Ativo']}")
            st.write(f"**Tipo de negócio: {ativo['Tipo de negócio']}**")
            st.write(f"Data de instalação: {ativo['Data de instalação']}")
            st.write(f"Ultima autação: {ativo['Data e descrição da última atuação no dispositivo']}")
            st.write(f"Instalador: {ativo['Endereço de e-mail']}")

        else:
            # --- NOVA LÓGICA DE CADASTRO ---
            st.warning("Ativo ainda não cadastrado.")
            st.header("Siga os passos para cadastrar:")

            st.subheader("Passo 1: Copie o ID do Ativo")
            st.info("Este é o identificador único para este ativo. Você vai precisar colá-lo no formulário.")
            st.code(id_ativo_escaneado, language=None)

            st.subheader("Passo 2: Abra o formulário e cole o ID")
            st.markdown(f'''
                <a href="{FORM_URL}" target="_blank" style="
                    display: inline-block; padding: 12px 20px; font-size: 18px;
                    font-weight: bold; color: white; background-color: #4CAF50;
                    text-align: center; text-decoration: none; border-radius: 8px;">
                    📝 Abrir Formulário de Cadastro
                </a>
            ''', unsafe_allow_html=True)

            st.info("Após preencher e enviar o formulário, escaneie o QR Code novamente para ver os detalhes do ativo.")
