from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import text
import os

load_dotenv()
PASSWORD = os.getenv('password')
HOST = os.getenv('host')
DATABASE = os.getenv('database')

def ingest_yfinance_data(tickers=[]):
    import yfinance as yf
    import pandas as pd
    from sqlalchemy import create_engine

    if isinstance(tickers, str):
        tickers = [tickers]
        
    tickers = [t.upper() for t in tickers]
    start_date = datetime.now() - timedelta(days=1)
    
    data = yf.download(tickers, start=start_date)

    if data.empty:
        print(f"Any data found for {tickers}.")
        return

    data = data.stack(level=1)

    data.reset_index(inplace=True)

    data.columns = [str(col).lower() for col in data.columns]

    engine = create_engine(f'postgresql://postgres:{PASSWORD}@{HOST}:5432/{DATABASE}')

    # Ingest data into the database
    try:
        with engine.connect() as connection:
            data.to_sql('temp_bronze', con=connection, if_exists='replace', index=False)
            create_table = text("""
                CREATE TABLE IF NOT EXISTS bronze (
                    date DATE,
                    ticker VARCHAR(10),
                    close NUMERIC,
                    high NUMERIC,
                    low NUMERIC,
                    open NUMERIC,
                    volume BIGINT,
                    PRIMARY KEY (date, ticker)
                );
            """)
            insert_query = text("""
                INSERT INTO bronze (date, ticker, close, high, low, open, volume)
                SELECT date, ticker, close, high, low, open, volume FROM temp_bronze
                ON CONFLICT (date, ticker) DO NOTHING
            """)

            connection.execute(create_table)
            result = connection.execute(insert_query)
            connection.commit()
            print(f"Data ingested successfully. Rows affected/inserted: {result.rowcount}")

    except Exception as e:
        print(f"Error ingesting data for {tickers}: {e}")

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