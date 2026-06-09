
  
    

  create  table "airflow"."bronze_gold"."fct_stocks_metrics__dbt_tmp"
  
  
    as
  
  (
    with silver_data as (
    select
        stock_ticker,
        date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume
    from "airflow"."bronze_silver"."stg_stocks"
),

calculated_metrics as (
    select
        stock_ticker,
        date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        
        -- 1. Retorno Diário (%): (Fechamento de Hoje / Fechamento de Ontem) - 1
        (
            (close_price / lag(close_price) over (partition by stock_ticker order by date)) - 1
        ) * 100 as daily_return_pct,

        -- 2. Volatilidade Intradia (Amplitude): Máxima - Mínima
        (high_price - low_price) as intraday_amplitude,

        -- 3. Liquidez Financeira: Preço de Fechamento x Volume de Ações negociadas
        (close_price * volume) as financial_volume

    from silver_data
)

select * from calculated_metrics
  );
  