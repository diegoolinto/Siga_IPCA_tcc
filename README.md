# 📈 Siga_IPCA - Análise Preditiva da Inflação Brasileira

Este repositório contém o código-fonte da aplicação web desenvolvida como Trabalho de Conclusão de Curso (TCC) para o curso de **Tecnólogo em Sistemas para Internet (TSI)** do **Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Norte (IFRN)**.

🔗 **Acesse a aplicação no ar:** https://sigaipcatcc.streamlit.app/

---

## 📌 Sobre o Projeto

O projeto consiste em uma ferramenta interativa para análise e projeção da inflação brasileira, utilizando o **Índice Nacional de Preço ao Consumidor Amplo (IPCA)** como série temporal principal. A aplicação permite a consulta de dados históricos e a simulação de cenários futuros utilizando o modelo estatístico **SARIMAX**, considerando também a influência de variáveis macroeconômicas exógenas como a **Taxa SELIC** e o **IGP-M**.

### 🛠️ Principais Funcionalidades

- **Ingestão em Tempo Real:** Coleta automatizada de séries temporais via API do Sistema Gerenciador de Séries Temporais do Banco Central do Brasil (SGS/BCB).
- **Análise Estatística:** Execução do teste de estacionariedade Augmented Dickey-Fuller (ADF) e cálculo de métricas de erro de validação (EQM e DAM/MAE).
- **Simulação de Cenários:** Interface interativa para seleção de horizontes de previsão (1 a 24 meses) e comparação entre valores reais e projetados.
- **Visualização Dinâmica:** Gráficos reativos construídos com a biblioteca Plotly.

---

## 💻 Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **Framework Web:** Streamlit
- **Manipulação de Dados:** Pandas, NumPy
- **Modelagem Econométrica:** Statsmodels, Scikit-learn
- **Visualização:** Plotly
- **Consumo de Dados:** Requests (REST API / BCB)

---
