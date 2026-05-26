from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

from yfinance_ingestion import ingest_yfinance_data

# Configurações padrão da DAG
default_args = {
    'owner': 'engenharia_dados',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define a DAG
with DAG(
    'pipeline_yfinance_diaria',
    default_args=default_args,
    description='Pipeline diária para atualizar dados de ações no Supabase',
    schedule_interval='0 0 * * *', # Expressão Cron para: "Todo dia à meia-noite"
    catchup=False # Impede o Airflow de tentar rodar todos os dias passados desde o start_date
) as dag:

    task_ingestao = PythonOperator(
        task_id='executar_ingestao_yfinance',
        python_callable=ingest_yfinance_data,
    )

    task_dbt = BashOperator(
        task_id='executar_transformacao_dbt',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    task_ingestao >> task_dbt