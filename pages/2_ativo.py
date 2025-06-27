import streamlit as st
import pandas as pd
from utils import carregar_dados # Importa a função do arquivo utils.py
from utils import logout  # Importa a função de autenticação do arquivo 0_login.py
# --- CONFIGURAÇÃO DA PÁGINA ---
st.logo('logo.png')
if st.session_state["authenticated"]:
    # Adiciona o logo na barra lateral
    st.logo('logo.png')

    st.title("🔎 Detalhes do Ativo")
    if st.sidebar.button("Logout"):
        logout()
    # --- CARREGAMENTO DOS SEGREDOS ---
    try:
        SHEET_URL_ATIVOS = st.secrets["SHEET_URL_ATIVOS"]
        HISTORICO_SHEET_URL = st.secrets["HISTORICO_SHEET_URL"]
        MANUTENCAO_FORM_URL = st.secrets["MANUTENCAO_FORM_URL"]
        FORM_URL_CADASTRO = st.secrets["FORM_URL"]
    except KeyError as e:
        st.error(f"ERRO DE CONFIGURAÇÃO: O segredo '{e}' não foi encontrado! Verifique o painel do Streamlit.")
        st.stop()

    # --- LÓGICA PRINCIPAL DA PÁGINA ---

    # Obtém o ID do ativo dos parâmetros da URL (ex: ?id_ativo=SEU_ID)
    query_params = st.query_params
    id_ativo_escaneado = query_params.get("id_ativo")

    # Campo para o usuário inserir o ID manualmente
    id_manual = st.text_input("Insira ou escaneie o ID do Ativo aqui:", value=id_ativo_escaneado or "")

    if not id_manual:
        st.info("Aguardando um ID de ativo. Escaneie um QR Code ou digite o ID acima.")
        st.stop()

    # Carrega ambos os DataFrames
    df_ativos = carregar_dados(SHEET_URL_ATIVOS)
    df_historico = carregar_dados(HISTORICO_SHEET_URL)

    if df_ativos.empty:
        st.error("Não foi possível carregar a lista de ativos. Verifique a planilha.")
        st.stop()

    # Procura pelo ativo no DataFrame
    ativo_info = df_ativos[df_ativos['ID DO ATIVO'] == id_manual]

    if not ativo_info.empty:
        ativo = ativo_info.iloc[0]
        st.success(f"Ativo encontrado!")

        # Layout com abas para detalhes e histórico
        tab1, tab2 = st.tabs(["📄 Detalhes do Ativo", "⚙️ Histórico de Atuações"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.header(ativo.get('Nome do dispositivo', 'N/A'))
                st.subheader(ativo.get('Tipo do Ativo', 'N/A'))
                st.write(f"**Cliente:** {ativo.get('Cliente', 'N/A')}")
                st.write(f"**Modelo do Ativo:** {ativo.get('Modelo do Ativo', 'N/A')}")
                st.write(f"**Tipo de negócio:** {ativo.get('Tipo de negócio', 'N/A')}")
                st.write(f"**Data de instalação:** {ativo.get('Data de instalação', 'N/A')}")
                st.write(f"**Cadastrado por:** {ativo.get('Endereço de e-mail', 'N/A')}")
                st.write(f"**Numero do Pedido:** {ativo.get('Numero do Pedido', 'N/A')}")


            with col2:
                st.header("Registrar Nova Atuação")
                st.warning("COPIE O ID DO ATIVO ABAIXO PARA USAR NO FORMULÁRIO:")
                st.code(id_manual, language=None)

                # !!! IMPORTANTE !!!
                # Substitua 'entry.SEU_ENTRY_ID_AQUI' pelo ID real do campo no seu Google Forms.
                # Você pode encontrar esse ID inspecionando o código-fonte do seu formulário.
                link_manutencao = f"{MANUTENCAO_FORM_URL}?usp=pp_url&entry.123456789={id_manual}" # Exemplo de ID: entry.123456789

                st.markdown(f'''
                    <a href="{link_manutencao}" target="_blank" style="
                        display: inline-block; padding: 12px 20px; font-size: 18px;
                        font-weight: bold; color: white; background-color: #FFA500; /* Laranja */
                        text-align: center; text-decoration: none; border-radius: 8px;">
                        ⚙️ Adicionar Atuação
                    </a>
                ''', unsafe_allow_html=True)
                st.caption("O formulário de atuação será aberto em uma nova aba.")


        with tab2:
            st.header("Histórico de Atuações no Dispositivo")
            if not df_historico.empty:
                historico_do_ativo = df_historico[df_historico['ID DO ATIVO'] == id_manual]
                if not historico_do_ativo.empty:
                    # Ordena o histórico pela data mais recente primeiro
                    # Converte a coluna de data para datetime para ordenar corretamente
                    historico_do_ativo['Data da Atuação'] = pd.to_datetime(historico_do_ativo['Data da Atuação'], errors='coerce')
                    st.dataframe(historico_do_ativo.sort_values(by='Data da Atuação', ascending=False), use_container_width=True)
                else:
                    st.info("Nenhuma atuação registrada para este dispositivo.")
            else:
                st.info("Nenhum histórico de atuação encontrado ou falha ao carregar.")

    else:
        # Lógica para cadastrar um novo ativo
        st.warning("Ativo ainda não cadastrado.")
        st.info("Se este é um novo ativo, copie o ID abaixo e use-o no formulário de cadastro.")
        st.code(id_manual, language=None)
        st.markdown(f'''
            <a href="{FORM_URL_CADASTRO}" target="_blank" style="
                display: inline-block; padding: 12px 20px; font-size: 18px;
                font-weight: bold; color: white; background-color: #4CAF50; /* Verde */
                text-align: center; text-decoration: none; border-radius: 8px;">
                ➕ Cadastrar Novo Ativo
            </a>
        ''', unsafe_allow_html=True)

