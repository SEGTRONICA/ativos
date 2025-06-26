import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(layout="wide", page_title="Visor de Ativos - Segtrônica",page_icon="logo.png")
# --- CARREGANDO O ARQUIVO DE CONFIGURAÇÃO ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- INICIALIZAÇÃO DO AUTENTICADOR ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- TELA DE LOGIN ---
# CORREÇÃO PRINCIPAL: O método login() agora é chamado sozinho.
# Ele não retorna mais valores. O estado é verificado via st.session_state.
authenticator.login()

if st.session_state["authentication_status"]:
    # --- PÁGINA PRINCIPAL APÓS LOGIN ---
    # O botão de logout também é chamado sozinho e atualiza o session_state
    st.sidebar.title(f'Bem-vindo(a), *{st.session_state["name"]}*')
    authenticator.logout('Logout', 'sidebar')

    st.title('Dashboard de Gerenciamento de Ativos 📈')

    # Exemplo de como usar dados do usuário logado:
    st.write(f"Usuário: `{st.session_state['username']}`")
    
    # Exemplo de lógica baseada no papel (role) do usuário
    try:
        user_role = config['credentials']['usernames'][st.session_state['username']]['role']
        if user_role == 'admin':
            st.success("Você tem acesso de Administrador.")
            # Coloque aqui os componentes visíveis apenas para admins
        else:
            st.info("Você tem acesso de Visualizador.")
    except KeyError:
        st.warning("Papel (role) do usuário não definido no arquivo de configuração.")

    # SEU CÓDIGO DO DASHBOARD VAI AQUI
    st.write("Aqui você pode visualizar e gerenciar seus ativos.")


elif st.session_state["authentication_status"] is False:
    st.error('Usuário/senha incorreto')
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, insira seu usuário e senha')


# --- REGISTRO DE NOVOS USUÁRIOS (Fora da lógica de login) ---
# Esta parte permanece a mesma da correção anterior.
st.divider()
try:
    if authenticator.register_user('Registrar novo usuário', preauthorization=True):
        st.success('Usuário registrado com sucesso! Por favor, faça o login para continuar.')
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)
st.title("Ativos - Segtrônica")
st.logo('logo.png',size='large')
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
    st.subheader("Lista de Ativos Cadastrados")
    if not df_ativos.empty:
        st.sidebar.markdown("### Lista de Ativos")
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
            tab1, tab2 = st.tabs(["📄 Detalhes do Ativo", "⚙️ Histórico de Atuações"])
            with tab1:
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

            with tab2:
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
