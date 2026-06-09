import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import dotenv
import os

# 1. Configurações Iniciais e Carga de Variáveis de Ambiente
dotenv.load_dotenv()

PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DATABASE = os.getenv('DB_NAME')
USER = os.getenv('DB_USER')

# Configuração da página do Streamlit (Layout Amplo)
st.set_page_config(page_title="Dashboard de Ações", layout="wide")

# 2. Gerenciamento Profissional de Conexões (Cache de Recursos)
@st.cache_resource
def get_database_engine():
    """Cria e armazena em cache a fábrica de conexões (Engine) do SQLAlchemy."""
    connection_url = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    return create_engine(connection_url)

@st.cache_data
def load_data():
    """Busca os dados da camada Gold e aplica tratamentos robustos de tipos."""
    engine = get_database_engine()
    query = "SELECT * FROM public_gold.fct_stocks_metrics"
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        colunas = [str(key) for key in result.keys()]
        df = pd.DataFrame(result.fetchall(), columns=colunas)
    
    # Padroniza nomes das colunas para minúsculo
    df.columns = [col.lower().strip() for col in df.columns]

    # Tratamento seguro de datas (remove fusos horários e NaNs)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['date'] = df['date'].dt.tz_localize(None)

    # Conversão explícita de tipos de dados numéricos (evita quebra no JS do navegador)
    colunas_numericas = ['daily_return_pct', 'intraday_amplitude', 'financial_volume']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

    # Remove registros inconsistentes
    df = df.dropna(subset=colunas_numericas)
    df = df.sort_values('date')

    return df

# Inicializa o carregamento dos dados com tratamento de exceção global
try:
    df_gold = load_data()
except Exception as e:
    st.error(f"Erro crítico ao conectar ou ler o banco de dados: {e}")
    st.stop()

# 3. Construção da Interface do Streamlit (UI/UX)
st.title("Dashboard de Análise de Ações")
st.markdown("Dados integrados via Airflow, transformados com dbt e armazenados.")

# --- Componentes da Barra Lateral (Filtros) ---
st.sidebar.header("Filtros de Seleção")

# Filtro de Ação (Ticker)
lista_tickers = df_gold['stock_ticker'].unique()
ticker_selecionado = st.sidebar.selectbox("Selecione a Ação:", options=lista_tickers)

# Aplica o primeiro filtro por Ticker para limitar as datas disponíveis na UI
df_ticker = df_gold[df_gold['stock_ticker'] == ticker_selecionado]

st.sidebar.markdown("---")
st.sidebar.subheader("Período de Análise")

# Captura os limites reais de datas para este ticker específico
min_date = df_ticker['date'].min().to_pydatetime()
max_date = df_ticker['date'].max().to_pydatetime()

# Filtro Temporal Dinâmico
data_selecionada = st.sidebar.date_input(
    "Selecione o intervalo de datas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 4. Filtragem Final dos Dados Baseado nos Filtros Ativos
if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    data_inicio, data_fim = data_selecionada
    df_filtrado = df_ticker[
        (df_ticker['date'] >= pd.to_datetime(data_inicio)) & 
        (df_ticker['date'] <= pd.to_datetime(data_fim))
    ]
else:
    df_filtrado = df_ticker # Fallback caso o usuário limpe um dos campos de data

# Se o filtro retornar um período sem dados, interrompe graciosamente
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para o período selecionado.")
    st.stop()


# --- Exibição dos Resultados na Tela Principal ---
st.subheader(f"Análise de Ativo — {ticker_selecionado}")

# 5. Painel de KPIs Resumidos (Métricas de Negócio)
col1, col2, col3 = st.columns(3)

with col1:
    ultimo_retorno = df_filtrado['daily_return_pct'].iloc[-1]
    st.metric(label="Último Retorno Diário", value=f"{ultimo_retorno:.2f}%")

with col2:
    amplitude_media = df_filtrado['intraday_amplitude'].mean()
    st.metric(label="Volatilidade Média (Amplitude)", value=f"$ {amplitude_media:.2f}")

with col3:
    volume_total = df_filtrado['financial_volume'].sum()
    if volume_total >= 1e12:
        volume_formatado = f"$ {volume_total / 1e12:.2f}T"
    elif volume_total >= 1e9:
        volume_formatado = f"$ {volume_total / 1e9:.2f}B"
    elif volume_total >= 1e6:
        volume_formatado = f"$ {volume_total / 1e6:.2f}M"
    elif volume_total >= 1e3:
        volume_formatado = f"$ {volume_total / 1e3:.2f}K"
    else:
        volume_formatado = f"$ {volume_total:.2f}"
    st.metric(label="Volume Total Movimentado", value=volume_formatado)

st.markdown("---")

# 6. Visualizações Gráficas Otimizadas por Abas
aba_retorno, aba_amplitude, aba_liquidez = st.tabs([
    "Retorno Diário (%)", 
    "Volatilidade (Amplitude)", 
    "Liquidez Financeira"
])

with aba_retorno:
    st.markdown("**Variação percentual do preço de fechamento contra o dia anterior**")
    chart_data_retorno = df_filtrado.set_index('date')['daily_return_pct']
    st.line_chart(chart_data_retorno)

with aba_amplitude:
    st.markdown("**Frequência cardíaca da ação (Máxima - Mínima do dia)**")
    chart_data_amplitude = df_filtrado.set_index('date')['intraday_amplitude']
    st.line_chart(chart_data_amplitude, color="#FF4B4B")

with aba_liquidez:
    st.markdown("**Volume financeiro total movimentado (Preço x Quantidade)**")
    chart_data_liquidez = df_filtrado.set_index('date')['financial_volume']
    st.area_chart(chart_data_liquidez, color="#29B5E8")

# 7. Auditoria de Dados Brutos
st.markdown("---")
if st.checkbox("Mostrar tabela de dados brutos filtrados para auditoria"):
    st.dataframe(df_filtrado, use_container_width=True)