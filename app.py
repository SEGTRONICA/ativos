import streamlit as st
import pandas as pd

# --- CÓDIGO DE PRODUÇÃO FINAL DO VISUALIZADOR DE ATIVOS ---

# Configuração inicial da página
st.set_page_config(layout="centered", page_title="Visor de Ativos")
st.title("Visor de Ativos")

# --- LÓGICA PRINCIPAL ---

# 1. Carrega os segredos (URLs) de forma segura
try:
    SHEET_URL = st.secrets["SHEET_URL"]
    FORM_URL = st.secrets["FORM_URL"]
    # IMPORTANTE: Garanta que este ID do campo está correto!
    FORM_ENTRY_ID = "entry.49708730" # Substitua pelo seu entry.ID real
except KeyError as e:
    st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado! Vá em Settings -> Secrets e configure-o no painel do Streamlit.")
    st.stop()

# Função para carregar e preparar os dados da planilha
def carregar_dados(url):
    csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
    try:
        df = pd.read_csv(csv_url)
        # Garante que a coluna do ID seja do tipo string para a comparação correta
        df['ID DO ATIVO'] = df['ID DO ATIVO'].astype(str)
        return df
    except Exception:
        # Se a planilha não puder ser carregada, retorna um DataFrame vazio
        return pd.DataFrame()

# 2. Pega o ID do ativo da URL da página
query_params = st.query_params
id_ativo_escaneado = query_params.get("id_ativo")

# 3. Decide o que mostrar na tela
if not id_ativo_escaneado:
    # Se nenhum ID for passado na URL, mostra a tela de boas-vindas
    st.info("Bem-vindo! Escaneie o QR Code de um ativo para começar.")
else:
    # Se um ID foi passado, carrega os dados
    df = carregar_dados(SHEET_URL)
    
    if df.empty and 'ID DO ATIVO' not in df.columns:
        st.error("Não foi possível carregar os dados dos ativos ou a coluna 'ID do Ativo' não foi encontrada. Verifique a planilha.")
    else:
        # Procura pelo ativo na planilha
        ativo_info = df[df['ID DO ATIVO'] == id_ativo_escaneado]

        # SE O ATIVO FOI ENCONTRADO, MOSTRA OS DADOS
        if not ativo_info.empty:
            st.success(f"Ativo encontrado!")
            ativo = ativo_info.iloc[0]
            
            st.header(ativo['Nome do Ativo'])
            st.write(f"**Localização:** {ativo['Localização']}")
            
            if 'Observações' in ativo and pd.notna(ativo['Observações']):
                st.write(f"**Observações:** {ativo['Observações']}")
            
            if 'Foto do Ativo' in ativo and pd.notna(ativo['Foto do Ativo']):
                st.image(ativo['Foto do Ativo'], caption="Foto do Ativo")

        # SE O ATIVO NÃO FOI ENCONTRADO, MOSTRA O LINK PARA CADASTRO
        else:
            st.warning("Ativo ainda não cadastrado.")
            st.header("Por favor, cadastre este ativo")

            link_preenchido = f"{FORM_URL}?usp=pp_url&{FORM_ENTRY_ID}={id_ativo_escaneado}"
            
            st.markdown(f'''
                <a href="{link_preenchido}" target="_blank" style="
                    display: inline-block; padding: 12px 20px; font-size: 18px;
                    font-weight: bold; color: white; background-color: #4CAF50;
                    text-align: center; text-decoration: none; border-radius: 8px;">
                    📝 Cadastrar Novo Ativo
                </a>
            ''', unsafe_allow_html=True)
            st.info("Após preencher o formulário, escaneie o QR Code novamente para ver os detalhes.")
