import streamlit as st
import pandas as pd

# --- CÓDIGO DE PRODUÇÃO COM DIAGNÓSTICO DE LINK ---

st.set_page_config(layout="centered", page_title="Visor de Ativos")
st.title("Visor de Ativos")

try:
    SHEET_URL = st.secrets["SHEET_URL"]
    FORM_URL = st.secrets["FORM_URL"]
    FORM_ENTRY_ID = "entry.49708730" # O ID que você configurou
except KeyError as e:
    st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado!")
    st.stop()

def carregar_dados(url):
    csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
    try:
        df = pd.read_csv(csv_url)
        # Atenção: O nome da coluna aqui deve ser EXATAMENTE igual ao da sua planilha
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
        st.error("Não foi possível carregar os dados ou a coluna 'ID DO ATIVO' não foi encontrada. Verifique o nome da coluna na planilha.")
    else:
        ativo_info = df[df['ID DO ATIVO'] == id_ativo_escaneado]

        if not ativo_info.empty:
            st.success(f"Ativo encontrado!")
            ativo = ativo_info.iloc[0]
            st.header(ativo['Nome do Ativo'])
            st.write(f"**Localização:** {ativo['Localização']}")

        else:
            st.warning("Ativo ainda não cadastrado.")
            st.header("Por favor, cadastre este ativo")

            link_preenchido = f"{FORM_URL}?usp=pp_url&{FORM_ENTRY_ID}={id_ativo_escaneado}"
            
            # --- LINHA DE DIAGNÓSTICO ADICIONADA ---
            st.info("A aplicação está tentando te redirecionar para o seguinte link:")
            st.code(link_preenchido, language="text")
            # ------------------------------------

            st.markdown(f'''
                <a href="{link_preenchido}" target="_blank" style="
                    display: inline-block; padding: 12px 20px; font-size: 18px;
                    font-weight: bold; color: white; background-color: #4CAF50;
                    text-align: center; text-decoration: none; border-radius: 8px;">
                    📝 Cadastrar Novo Ativo
                </a>
            ''', unsafe_allow_html=True)
            st.info("Se o preenchimento automático não funcionar, o 'entry.ID' no código está incorreto.")
