import pandas as pd
import requests
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error

def baixar_serie(codigo):
    """Busca dados na API do Banco Central."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
    try:
        response = requests.get(url, timeout=10)
        data_json = response.json()
        df = pd.DataFrame(data_json)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'))
        df.set_index('data', inplace=True)
        df = df.sort_index()
        df = df.asfreq('MS')

        df = df.loc['2000-01-01':]
        return df
    except Exception as e:
        return None


def processar_dados(codigo_principal, codigos_exogenos):
    """Coleta e une todas as séries selecionadas pelo usuário."""
    df_principal = baixar_serie(codigo_principal)
    if df_principal is None: return None

    colunas = {f"V{codigo_principal}": df_principal['valor']}

    for cod in codigos_exogenos:
        df_exog = baixar_serie(cod)
        if df_exog is not None:
            colunas[f"V{cod}"] = df_exog['valor']

    df_final = pd.concat(colunas, axis=1).dropna()
    return df_final.loc['2000-01-01':]


def treinar_e_prever(df, col_alvo, cols_exog, meses_previsao):
    """Treina o modelo SARIMAX baseado nas escolhas do usuário."""
    # Divisão treino/teste (usamos os últimos 12 meses para validar)
    train = df.iloc[:-12]
    test = df.iloc[-12:]

    # Configuração do modelo
    exog_train = train[cols_exog] if cols_exog else None

    model = SARIMAX(
        train[col_alvo],
        exog=exog_train,
        order=(0, 1, 0),
        seasonal_order=(0, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    result = model.fit(disp=False)

    # Previsão Out-of-sample (Validação)
    exog_test = test[cols_exog] if cols_exog else None
    forecast_test = result.get_forecast(steps=12, exog=exog_test)

    # Previsão Futura (O que o usuário pediu no Slider)
    # Para simplificar no TCC, projetamos o futuro repetindo o último valor das exógenas
    exog_future = None
    if cols_exog:
        ultimos_valores_exog = test[cols_exog].tail(1)
        exog_future = pd.concat([ultimos_valores_exog] * meses_previsao, ignore_index=True)

    forecast_future = result.get_forecast(steps=meses_previsao, exog=exog_future)

    return train, test, forecast_test.predicted_mean, forecast_future.predicted_mean

def testar_estacionariedade(serie):
    """Realiza o teste Augmented Dickey-Fuller."""
    res = adfuller(serie.dropna())
    is_estacionaria = res[1] < 0.05
    return {
        "estatistica": res[0],
        "p-valor": res[1],
        "resultado": "Estacionária" if is_estacionaria else "Não Estacionária"
    }

def calcular_metricas(real, previsto):
    """Calcula EQM (Erro Quadrático Médio) e DAM (Desvio Absoluto Médio - MAE)."""
    eqm = mean_squared_error(real, previsto)
    dam = mean_absolute_error(real, previsto) # DAM é o mesmo que MAE
    return eqm, dam