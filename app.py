import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.modelo import processar_dados, treinar_e_prever, testar_estacionariedade, calcular_metricas, baixar_serie

st.set_page_config(page_title="SAPI - IFRN", layout="wide")

# Dicionário de códigos informado pelo SGST do Banco central
mapa_codigos = {
    "IPCA": 433, "INPC": 188, "IGP-M": 189, "SELIC": 4390, "IPA-M": 7450
}

# --- Título e Subtítulo principal ---

st.title("📈 SAPI — Sistema de Análise e Previsão da Inflação")
st.caption("Trabalho de Conclusão de Curso (TCC) — Tecnólogo em Sistemas para Internet (IFRN)")

st.markdown("---")


st.sidebar.title("Configurações do Modelo")

# 1. Usuário seleciona o alvo(índice a ser analisada) e as influências
alvo_nome = st.sidebar.selectbox("Índice a ser analisado - Série Principal (Alvo):", list(mapa_codigos.keys()))
exog_nomes = st.sidebar.multiselect("Variáveis Exógenas (Influências):",
                                    [k for k in mapa_codigos.keys() if k != alvo_nome])

meses_futu = st.sidebar.slider("Meses de previsão futura:", 1, 24, 12)

cod_alvo = mapa_codigos[alvo_nome]
cods_exog = [mapa_codigos[n] for n in exog_nomes]

if st.sidebar.button("Executar Análise Completa"):

    with st.spinner("Processando..."):
        # 1. Busca e Processamento
        df = processar_dados(cod_alvo, cods_exog)


        if df is not None:
            col_alvo = f"V{cod_alvo}"
            cols_exog = [f"V{c}" for c in cods_exog]

            # 2. Treinamento e Predição
            train, test, pred_valida, pred_futura = treinar_e_prever(df, col_alvo, cols_exog, meses_futu)

            # --- ORGANIZAÇÃO EM ABAS (UI Profissional) ---
            tab1, tab2, tab3 = st.tabs(["📈 Predição", "📊 Estatísticas ADF/Erros", "🔗 Correlação"])

            with tab1:
                st.subheader("Projeção SARIMAX")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df[col_alvo], name="Histórico Real"))
                fig.add_trace(go.Scatter(x=test.index, y=pred_valida, name="Validação", line=dict(dash='dot')))

                # Datas futuras
                datas_f = pd.date_range(start=df.index[-1], periods=meses_futu + 1, freq='MS')[1:]
                fig.add_trace(go.Scatter(x=datas_f, y=pred_futura, name="Previsão Futura", line=dict(color='red')))
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Análise de Estacionariedade (ADF)")
                adf = testar_estacionariedade(df[col_alvo])
                c1, c2, c3 = st.columns(3)
                c1.metric("P-Valor", f"{adf['p-valor']:.4f}")
                c2.metric("Estatística", f"{adf['estatistica']:.2f}")
                c3.info(f"Resultado: {adf['resultado']}")

                st.markdown("---")
                st.subheader("Métricas de Precisão do Modelo")
                eqm, dam = calcular_metricas(test[col_alvo], pred_valida)
                m1, m2 = st.columns(2)
                m1.metric("EQM (Erro Quadrático Médio)", f"{eqm:.4f}")
                m2.metric("DAM (Desvio Absoluto Médio)", f"{dam:.4f}")

            with tab3:
                st.subheader("Matriz de Correlação")
                if len(df.columns) > 1:
                    # Renomear colunas para os nomes amigáveis antes de correlacionar
                    df_corr = df.rename(
                        columns={f"V{mapa_codigos[k]}": k for k in mapa_codigos if f"V{mapa_codigos[k]}" in df.columns})
                    corr = df_corr.corr()
                    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
                    st.plotly_chart(fig_corr)
                else:
                    st.warning("Selecione variáveis exógenas para ver a correlação.")

        else:
            st.error("Erro na conexão com os dados do Banco Central.")
else:
    # --- Mensagem de boas-vindas / introdução ---
    st.subheader("Bem vindo ao SAPI")
    st.write("""
        Esta plataforma foi desenvolvida para **analisar e prever a trajetória da inflação oficial do Brasil (IPCA)** 
        utilizando técnicas econométricas de **Séries Temporais (Modelo SARIMAX)**. 
        Com ela, você pode visualizar dados históricos atualizados em tempo real diretamente da API do Banco Central 
        e simular cenários futuros considerando o impacto de variáveis macroeconômicas como a **Taxa SELIC** e o **IGP-M**.
        """)

    st.markdown("---")

    # --- CARDS INFORMATIVOS (3 COLUNAS) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Dados do BCB")
        st.write("Consumo automatizado das séries temporais oficiais do Banco Central do Brasil (SGS/BCB).")

    with col2:
        st.markdown("### 🤖 Modelo SARIMAX")
        st.write("Previsões estatísticas que consideram sazonalidade e a influência de indicadores exógenos.")

    with col3:
        st.markdown("### 🎯 Tomada de Decisão")
        st.write("Avaliação de métricas de precisão (EQM e DAM) e simulação visual de cenários futuros.")

    st.markdown("---")

    # --- PASSO A PASSO PAINEL DE AJUDA ---
    st.info(
        """
        👈 **Como utilizar a aplicação:**
        1. Abra o **Menu Lateral (Configurações do Modelo)** clicando na seta no canto superior esquerdo.
        2. Escolha o **Índice Alvo** (ex: IPCA).
        3. Selecione as **Variáveis Exógenas** desejadas (ex: SELIC, IGP-M).
        4. Defina o **Horizonte de Previsão** (quantidade de meses à frente).
        5. Clique no botão **"Executar Análise Completa"** para gerar os gráficos e relatórios!
        """
    )

# Usando o código que o usuário escolheu na seleção do índice e baixando os dados reais do site do banco central
if st.sidebar.button("Visualizar Dados Reais"):
    with st.spinner("Conectando ao API do Banco Central..."):
        # 1. Busca os dados reais usando sua função no arquivo modelo.py
        st.header("📊 Consulta de Dados Reais (SGS - Banco Central)")
        df_real = baixar_serie(cod_alvo)

        if df_real is not None:
            # 2. Mostra uma visão geral dos números (Métricas rápidas)
            ultimo_valor = df_real['valor'].iloc[-1]
            data_ultima = df_real.index[-1].strftime('%m/%Y')

            c1, c2 = st.columns(2)
            c1.metric(f"Último valor registrado ({data_ultima})", f"{ultimo_valor:.2f}%")
            c2.metric("Total de meses na base", len(df_real))

            # 3. Cria o gráfico de linha interativo com Plotly
            fig_real = px.line(
                df_real,
                y='valor',
                title=f"Série Histórica Real: {alvo_nome}",
                labels={'valor': 'Variação (%)', 'data': 'Período'},
                line_shape="spline"  # Deixa a linha mais "suave"
            )

            # Personalização do gráfico
            fig_real.update_traces(line_color='#00CC96')  # Cor verde para representar "Real"
            st.plotly_chart(fig_real, use_container_width=True)

            # 4. Opção de ver a tabela de dados
            with st.expander("Ver tabela de dados brutos"):
                st.dataframe(df_real.sort_index(ascending=False))
        else:
            st.error("Não foi possível carregar os dados. Verifique o código SGS.")