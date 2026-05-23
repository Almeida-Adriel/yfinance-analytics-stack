with source as (
    select
        ticker,
        date,
        open,
        high,
        low,
        close,
        volume
    from {{ source ('postgres', 'stocks') }}
),

--rename columns and add metadata
renamed as (
    select
        cast(ticker as varchar(10)) as stock_ticker,
        cast(date as date) as date,
        cast(open as numeric(10, 2)) as open_price,
        cast(high as numeric(10, 2)) as high_price,
        cast(low as numeric(10, 2)) as low_price,
        cast(close as numeric(10, 2)) as close_price,
        cast(volume as bigint) as volume,
        current_timestamp as ingestion_timestamp
    from source
)

select * from renamed