from datetime import datetime, timedelta
from dotenv import load_dotenv
from airflow.sdk import Variable
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
import yfinance as yf
import os

def postgres_upsert_method(table, conn, keys, data_iter):
    """
    Método customizado para o pandas to_sql que executa um 
    INSERT ... ON CONFLICT DO NOTHING no PostgreSQL.
    """
    # Converte os dados do iterador em uma lista de dicionários mapeados pelas colunas
    data = [dict(zip(keys, row)) for row in data_iter]
    
    # Cria a instrução de inserção baseada na tabela alvo do SQLAlchemy
    insert_stmt = pg_insert(table.table).values(data)
    
    # Define o que fazer em caso de conflito. 
    upsert_stmt = insert_stmt.on_conflict_do_nothing(
        index_elements=['date', 'ticker'] # Colunas que formam a chave única
    )
    
    # Executa a query
    conn.execute(upsert_stmt)

def ingest_yfinance_data(start_date=None, tickers=None, **kwargs):
    load_dotenv()

    PASSWORD = os.getenv('DB_PASSWORD')
    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')
    DATABASE = os.getenv('DB_NAME')
    USER = os.getenv('DB_USER')

    # Captura de Tickers
    try:
        if tickers is None:
            tickers_var = Variable.get("TICKERS", default="AAPL,MSFT,GOOGL").split(",")
            tickers = [t.strip().upper() for t in tickers_var]
        print(f"Tickers selecionados: {tickers}")
    except Exception as e:
        print(f"Erro ao ler variáveis de TICKERS: {e}. Usando fallback AAPL.")
        tickers = ["AAPL"]

    # 2. SE NENHUMA DATA FOI PASSADA VIA DAG, busca a Variável do Airflow
    if start_date is None:
        # Tenta buscar a variável. Se não existir no painel, retorna None
        start_date = Variable.get("START_DATE", default=None)
        if start_date:
            print(f"Data de início capturada via Airflow Variable (START_DATE): {start_date}")

    connection_url = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    engine = create_engine(connection_url)

    # 3. Lógica de decisão da data (Modificada para aceitar a variável)
    if start_date is not None and start_date.strip() != "":
        try:
            datetime.strptime(start_date.strip(), '%Y-%m-%d')
            start_date = start_date.strip()
        except ValueError:
            print(f"Formato inválido para start_date recebido: {start_date}. Usando fallback automático.")
            start_date = None

    # Se ainda for None (Variável não existe e nem foi passada por parâmetro), roda modo inteligente
    if start_date is None:
        inspector = inspect(engine)
        if 'stocks' in inspector.get_table_names():
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"table 'stocks' detectada. Modo incremental ativado automaticamente para: {start_date}")
        else:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            print(f"table 'stocks' NÃO encontrada. Fazendo carga inicial automática desde: {start_date}")

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
        print(f"Iniciando download do yfinance para {tickers} desde {start_date}...")
        data = yf.download(tickers, start=start_date, timeout=15)
    except Exception as e:
        print(f"Erro ou Timeout no download do yfinance: {e}")
        return

    if data.empty:
        print(f"Nenhum dado encontrado para {tickers} no período solicitado.")
        return

    # Reshape do DataFrame
    data = data.stack(level=1, future_stack=True)
    data.reset_index(inplace=True)
    data.columns = [str(col).lower() for col in data.columns]

    inspector = inspect(engine)
    table_exists = 'stocks' in inspector.get_table_names()

    # Garantia física da restrição de unicidade ANTES da primeira inserção inteligente
    with engine.begin() as connection:
        if table_exists:
            # Cria a constraint caso a tabela já exista mas não tenha a regra aplicada
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'unique_date_ticker'
                    ) THEN
                        ALTER TABLE stocks ADD CONSTRAINT unique_date_ticker UNIQUE (date, ticker);
                    END IF;
                END $$;
            """))

    # Ingestão inteligente com tratamento de conflito
    try:
        with engine.begin() as connection:
            # Se a tabela não existir, o pandas cria ela primeiro
            # Se ela já existe, usamos o nosso método modificado de upsert
            data.to_sql(
                'stocks', 
                con=connection, 
                if_exists='append', 
                index=False,
                method=postgres_upsert_method if table_exists else None
            )
            
            # Se a tabela acabou de ser criada agora pelo pandas, aplicamos a constraint para as próximas execuções
            if not table_exists:
                connection.execute(text("""
                    ALTER TABLE stocks ADD CONSTRAINT unique_date_ticker UNIQUE (date, ticker);
                """))
                
            print(f"Processamento concluído. Dados enviados para validação de conflito no banco.")
            
    except Exception as e:
        print(f"Error inserting data into database: {e}")