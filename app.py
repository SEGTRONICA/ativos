import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO ---
# As URLs agora são lidas do gerenciador de segredos do Streamlit
# Isso torna seu código seguro para ir ao GitHub
try:
    SHEET_URL = st.secrets["SHEET_URL"]
    FORM_URL = st.secrets["FORM_URL"]
except KeyError:
    st.error("As URLs da Planilha ou do Formulário não foram configuradas nos segredos da aplicação.")
    st.stop()


# --- LÓGICA DO APP (continua exatamente a mesma) ---

st.set_page_config(layout="centered")
st.title("Visor de Ativos")

# Função para carregar e limpar os dados da planilha
def carregar_dados(url):
    csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
    try:
        df = pd.read_csv(csv_url)
        df['ID DO ATIVO'] = df['ID DO ATIVO'].astype(str)
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da planilha. Verifique o link e as permissões. Erro: {e}")
        return pd.DataFrame()

# Pega o ID do ativo da URL da página
query_params = st.query_params
id_ativo_escaneado = query_params.get("id_ativo")


if not id_ativo_escaneado:
    st.info("Bem-vindo! Escaneie um QR Code para começar.")
else:
    df = carregar_dados(SHEET_URL)
    
    if not df.empty:
        # Procura pelo ativo na planilha
        ativo_info = df[df['ID do Ativo'] == id_ativo_escaneado]

        # SE O ATIVO FOI ENCONTRADO, MOSTRA OS DADOS
        if not ativo_info.empty:
            st.success(f"Ativo encontrado!")
            st.header(ativo_info.iloc[0]['Nome do Ativo'])
            
            st.write(f"**Localização:** {ativo_info.iloc[0]['Localização']}")
            st.write(f"**Observações:** {ativo_info.iloc[0]['Observações']}")
            
            # Se houver uma coluna com link de foto, exibe a imagem
            if 'Foto do Ativo' in ativo_info.columns and pd.notna(ativo_info.iloc[0]['Foto do Ativo']):
                st.image(ativo_info.iloc[0]['Foto do Ativo'], caption="Foto do Ativo")

        # SE O ATIVO NÃO FOI ENCONTRADO, MOSTRA O LINK PARA CADASTRO
        else:
            st.warning("Ativo ainda não cadastrado.")
            st.header("Primeiro passo: Cadastre este ativo!")

            # Cria um link pré-preenchido para o Google Form, já com o ID correto!
            link_preenchido = f"{FORM_URL}?usp=pp_url&entry.49708730={id_ativo_escaneado}"
            # IMPORTANTE: Você precisa descobrir o entry.ID_DO_CAMPO_ID correto.
            # Veja como no tutorial abaixo do código.
            
            st.markdown(f'''
                <a href="{link_preenchido}" target="_blank" style="
                    display: inline-block;
                    padding: 12px 20px;
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    background-color: #4CAF50;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 8px;">
                    📝 CLIQUE AQUI PARA CADASTRAR
                </a>
            ''', unsafe_allow_html=True)
            st.info("Após preencher o formulário, escaneie o QR Code novamente para ver os detalhes.")
