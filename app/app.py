import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import dotenv
import os

dotenv.load_dotenv()

# 1. Configurações de conexão com o Supabase (Substitua pelas suas credenciais)
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DATABASE = os.getenv('DB_NAME')
PROJECT_ID = os.getenv('DB_PROJECT_ID')


@st.cache_data
def load_data():
    # Criamos a conexão com o banco
    engine = create_engine(f'postgresql://postgres.{PROJECT_ID}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
    
    # Buscamos os dados da camada Gold
    query = "SELECT * FROM bronze_gold.fct_stocks_metrics"
    df = pd.read_sql(query, con=engine)
    
    # Garante que a data está no formato correto de data do Pandas
    df['date'] = pd.to_datetime(df['date'])
    return df

# Inicializa o carregamento dos dados
try:
    df_gold = load_data()
except Exception as e:
    st.error(f"Erro ao conectar no Supabase: {e}")
    st.stop()

# 2. Construção da Interface do Streamlit
st.title("📈 Dashboard de Análise de Ações")
st.markdown("Dados integrados via Airflow, transformados com dbt e armazenados no Supabase.")

# Criando componentes na barra lateral
st.sidebar.header("Filtros")

# Extrai os tickers únicos para preencher as opções do selectbox
lista_tickers = df_gold['stock_ticker'].unique()
ticker_selecionado = st.sidebar.selectbox("Selecione a Ação:", options=lista_tickers)

# 3. Filtrando os dados com base na escolha do usuário
df_filtrado = df_gold[df_gold['stock_ticker'] == ticker_selecionado]

# 4. Exibindo os Gráficos baseados no filtro
st.subheader(f"Análise Diária — {ticker_selecionado}")

# Criando abas para organizar as métricas que você criou na Gold
aba_retorno, aba_amplitude, aba_liquidez = st.tabs([
    "Retorno Diário (%)", 
    "Volatilidade (Amplitude)", 
    "Liquidez Financeira"
])

with aba_retorno:
    st.markdown("**Variação percentual do preço de fechamento contra o dia anterior**")
    # Formatando para o gráfico usar a data como eixo X e o retorno como eixo Y
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

# Exibindo os dados brutos filtrados caso o usuário queira auditar
if st.checkbox("Mostrar tabela de dados brutos filtrados"):
    st.dataframe(df_filtrado)