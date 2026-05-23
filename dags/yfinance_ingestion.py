from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy import text
import yfinance as yf
import os

load_dotenv()
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
DATABASE = os.getenv('DB_NAME')

tickers=['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'NVDA'] # Example tickers for analysis

def ingest_yfinance_data(start_date=None, interval='1d', tickers=tickers):

    engine = create_engine(f'postgresql://postgres:{PASSWORD}@{HOST}:5432/{DATABASE}')

    if start_date is not None or datetime.strptime(start_date, '%Y-%m-%d') < datetime.now() - timedelta(days=30):
        print(f"start_date {start_date} is more than 30 days ago. Adjusting for initial load. start_date set to {(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}")
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    else:
        inspector = inspect(engine) # Check if the table exists

        if 'stocks' in inspector.get_table_names():
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"table 'stocks' detectada. Modo incremental ativado para a data: {start_date}")

        else:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            print(f"table 'stocks' NÃO encontrada. Fazendo carga inicial desde: {start_date}")

    # Validate start_date format and reasonable year to avoid DST/parsing issues
    try:
        parsed_start = datetime.strptime(start_date, '%Y-%m-%d')
    except Exception as e:
        print(f"Invalid start_date '{start_date}': {e}")
        return

    if parsed_start.year < 1900:
        print(f"start_date year {parsed_start.year} looks incorrect.")
        return
    
    if isinstance(tickers, str):
        tickers = [tickers]
        
    tickers = [t.upper() for t in tickers]

    try:
        data = yf.download(tickers, start=start_date)
    except Exception as e:
        print(f"Error downloading data for {tickers}: {e}")
        return

    if data.empty:
        print(f"Any data found for {tickers}.")
        return

    # Reshape the DataFrame
    data = data.stack(level=1)
    data.reset_index(inplace=True)
    data.columns = [str(col).lower() for col in data.columns]

    # Ingest data into the database
    try:
        with engine.connect() as connection:
            data.to_sql('stocks', con=connection, if_exists='append', index=False)
            print(f"Success! {len(data)} rows inserted via append into table 'stocks'.")
    except Exception as e:
        print(f"Error inserting data into database: {e}")

ingest_yfinance_data(start_date=('2026-05-01'))
# Define the DAG
# with DAG(
#     'yfinance_ingestion',
#     default_args={
#         'owner': 'airflow',
#         'depends_on_past': False,
#         'start_date': datetime(2026, 5, 22),
#         'retries': 1,
#         'retry_delay': timedelta(minutes=5),
#     },
#     schedule_interval='@daily',
# ) as dag:
    
#     ingest_task = PythonOperator(
#         task_id='ingest_yfinance_data',
#         python_callable=ingest_yfinance_data,
#     )

#     ingest_task