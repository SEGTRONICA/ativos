import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Visor de Ativos")
st.title("Visor de Ativos e Manutenção")

# --- CARREGAMENTO DOS SEGREDOS --
try:
    SHEET_URL_ATIVOS = st.secrets["SHEET_URL_ATIVOS"] # Nome novo
    HISTORICO_SHEET_URL = st.secrets["HISTORICO_SHEET_URL"] # Nome novo
    
    FORM_URL_CADASTRO = st.secrets["FORM_URL"]
    MANUTENCAO_FORM_URL = st.secrets["MANUTENCAO_FORM_URL"]

except KeyError as e:
    st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado! Verifique o painel do Streamlit.")
    st.stop()
    
# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def carregar_dados(url_completa):
    try:
        # A URL já vem pronta dos segredos, não precisa mais do .replace()
        df = pd.read_csv(url_completa, dtype=str)
        return df
    except Exception:
        return pd.DataFrame()

# --- LÓGICA PRINCIPAL ---
query_params = st.query_params
id_ativo_escaneado = query_params.get("id_ativo")

# Carrega ambos os DataFrames
df_ativos = carregar_dados(SHEET_URL_ATIVOS)
df_historico = carregar_dados(HISTORICO_SHEET_URL)

if not id_ativo_escaneado:
    st.info("Bem-vindo! Escaneie o QR Code de um ativo para começar.")
    st.subheader("Lista de Ativos Cadastrados")
    if not df_ativos.empty:
        st.dataframe(df_ativos)

else:
    if df_ativos.empty:
        st.error("Não foi possível carregar a lista de ativos.")
    else:
        ativo_info = df_ativos[df_ativos['ID DO ATIVO'] == id_ativo_escaneado]
        
        if not ativo_info.empty:
            ativo = ativo_info.iloc[0]
            st.success(f"Ativo encontrado!")
            st.warning("COPIAR O ID DO ATIVO ABAIXO:")
            st.code(f"{id_ativo_escaneado}")
            
            # Layout com duas colunas para melhor organização
            col1, col2 = st.columns(2)

            with col1:
                st.header(ativo['Nome do dispositivo'])
                st.subheader(ativo['Tipo do Ativo'])
                st.write(f"**Numero do Pedido:** {ativo['Numero do Pedido']}")
                st.write(f"**Cliente:** {ativo['Cliente']}")
                st.write(f"**Modelo do Ativo:** {ativo['Modelo do Ativo']}")
                st.write(f"**Tipo de negócio:** {ativo['Tipo de negócio']}")
                st.write(f"**Data de instalação:** {ativo['Data de instalação']}")
                st.write(f"**Cadastrado por:** {ativo['Endereço de e-mail']}")
            
            with col2:
                st.header("Registrar Nova Atuação")
                # Link para o formulário de manutenção, pré-preenchendo o ID
                link_manutencao = f"{MANUTENCAO_FORM_URL}?usp=pp_url&entry.SEU_ENTRY_ID_AQUI={id_ativo_escaneado}"
                
                st.markdown(f'''
                    <a href="{link_manutencao}" target="_blank" style="
                        display: inline-block; padding: 12px 20px; font-size: 18px;
                        font-weight: bold; color: white; background-color: #FFA500; /* Laranja */
                        text-align: center; text-decoration: none; border-radius: 8px;">
                        ⚙️ Adicionar Atuação
                    </a>
                ''', unsafe_allow_html=True)

            st.divider()

            # --- SEÇÃO DE HISTÓRICO DE MANUTENÇÃO ---
            st.header("Histórico de Atuações no Dispositivo")
            if not df_historico.empty:
                historico_do_ativo = df_historico[df_historico['ID DO ATIVO'] == id_ativo_escaneado]
                if not historico_do_ativo.empty:
                    # Mostra o histórico, ordenando pela data mais recente primeiro
                    st.dataframe(historico_do_ativo.sort_values(by='Data da Atuação', ascending=False))
                else:
                    st.info("Nenhuma atuação registrada para este dispositivo.")
            else:
                st.info("Nenhum histórico de atuação encontrado.")

        else:
            # Lógica para cadastrar um novo ativo (simplificada)
            st.warning("Ativo ainda não cadastrado.")
            st.markdown(f'<a href="{FORM_URL_CADASTRO}" target="_blank">Clique aqui para ir ao formulário de cadastro.</a>', unsafe_allow_html=True)
