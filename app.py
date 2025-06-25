import streamlit as st
import pandas as pd

# --- DEPURANDO O CÓDIGO DO VISUALIZADOR DE ATIVOS ---

st.set_page_config(layout="centered")
st.title("Depurando o Visor de Ativos")
st.write("---")

# --- PASSO 1: Verificando os Segredos (Secrets) ---
st.header("PASSO 1: Verificando os Segredos")
try:
    SHEET_URL = st.secrets["SHEET_URL"]
    FORM_URL = st.secrets["FORM_URL"]
    st.success("Segredos SHEET_URL e FORM_URL carregados com sucesso!")
except KeyError as e:
    st.error(f"ERRO CRÍTICO: O segredo '{e}' não foi encontrado! Vá em Settings -> Secrets e configure-o.")
    st.stop() # Para a execução se os segredos não existirem

# --- PASSO 2: Lendo o ID da URL ---
st.header("PASSO 2: Lendo o ID da URL")
query_params = st.query_params
id_ativo_escaneado = query_params.get("id_ativo")

if not id_ativo_escaneado:
    st.warning("Nenhum 'id_ativo' encontrado na URL. Escaneie um QR Code para começar.")
    st.stop()
else:
    st.success(f"ID encontrado na URL: `{id_ativo_escaneado}`")

# --- PASSO 3: Carregando e Verificando a Planilha ---
st.header("PASSO 3: Carregando e Verificando a Planilha")
def carregar_dados(url):
    csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
    try:
        df = pd.read_csv(csv_url)
        st.success("Planilha Google carregada com sucesso!")
        return df
    except Exception as e:
        st.error(f"ERRO ao carregar a Planilha Google: {e}")
        return None

df = carregar_dados(SHEET_URL)

if df is None:
    st.error("A execução foi interrompida porque a planilha não pôde ser carregada.")
    st.stop()

# --- PASSO 4: Verificando a Coluna e os Tipos de Dados ---
st.header("PASSO 4: Verificando a Coluna e os Tipos")
if 'ID do Ativo' not in df.columns:
    st.error(f"ERRO CRÍTICO: A coluna 'ID do Ativo' não foi encontrada na sua planilha!")
    st.write("Colunas encontradas:", df.columns.to_list())
    st.stop()
else:
    st.success("A coluna 'ID do Ativo' foi encontrada na planilha.")
    # Forçando a conversão para string para garantir a comparação correta
    df['ID do Ativo'] = df['ID do Ativo'].astype(str)
    st.info("A coluna 'ID do Ativo' foi convertida para texto para garantir a comparação.")


# --- PASSO 5: Procurando pelo ID na Planilha ---
st.header("PASSO 5: Procurando pelo ID")
st.write(f"Procurando por `{id_ativo_escaneado}` na coluna 'ID do Ativo'...")

ativo_info = df[df['ID do Ativo'] == id_ativo_escaneado]

if not ativo_info.empty:
    st.success("SUCESSO! O ativo foi encontrado na planilha. Mostrando os detalhes:")
    # Aqui iria o código para mostrar os detalhes do ativo
    st.dataframe(ativo_info)
else:
    st.warning("AVISO: O ID não foi encontrado na planilha. Mostrando o link de cadastro.")
    # Aqui iria o código para mostrar o link do formulário
    st.markdown(f"### [CLIQUE AQUI PARA CADASTRAR](https://forms.gle/SEU_LINK_AQUI)", unsafe_allow_html=True) # Coloque seu link aqui para teste
    st.info("Se você já cadastrou e está vendo esta mensagem, o problema pode ser um espaço em branco ou caractere invisível no ID da planilha.")
