{% docs __overview__ %}

# 📈 yfinance-analytics-stack

Bem-vindo à documentação oficial do **yfinance-analytics-stack**! Este projeto é uma plataforma automatizada de Engenharia de Dados voltada para a captura, transformação e disponibilização de métricas financeiras das principais ações do mercado (AAPL, AMZN, GOOGL, MSFT, NVDA).

---

## Arquitetura de Dados

O projeto segue os princípios da **Medallion Architecture** (Camadas Bronze, Silver e Gold), garantindo organização, rastreabilidade e performance:

```
                        [ Apache Airflow ] ──(Ingestão Diária)──> [ Python / yfinance ]
                                                      │
                                                      ▼
                                              ┌─────────────────┐
                                              │ PostgreSQL      │
                                              │ (Supabase)      │
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │     dbt         │
                                              │  (Transformação)│
                                              └────────┬────────┘
                                                       │
            ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
            ▼                                          ▼                                          ▼
    [ Camada BRONZE ]                          [ Camada SILVER ]                          [ Camada GOLD ]
    Dados brutos (Append)                      Limpeza e Tipagem                          Métricas Avançadas
    Schema: public.stocks                      Schema: silver.stg_stocks                  Schema: gold.fct_stocks_metrics
```

---

## Tecnologias Utilizadas

* **Orquestração:** [Apache Airflow](https://airflow.apache.org/) - Gerencia o agendamento diário e execução da pipeline.
* **Coleta de Dados:** [yfinance](https://github.com/ranaroussi/yfinance) - Biblioteca Python para consumo da API do Yahoo Finance.
* **Transformação:** [dbt (data build tool)](https://www.getdbt.com/) - Modelagem, documentação e testes das camadas analíticas.
* **Banco de Dados:** [Supabase / PostgreSQL](https://supabase.com/) - Infraestrutura de armazenamento em nuvem.

---

## 📂 Estrutura do Projeto

```text
yfinance-analytics-stack/
├── app/
│   └── dags/
│       └── yfinance_ingestion.py   # Script Airflow (Carga Incremental D-1)
├── dbt_project/
│   ├── models/
│   │   ├── silver/
│   │   │   ├── schema.yml          # Definição de Sources e Staging
│   │   │   └── stg_stocks.sql      # Casts e renomeação (Bronze -> Silver)
│   │   └── gold/
│   │       └── fct_stocks_metrics.sql # Janelas analíticas (LAG/PARTITION)
│   └── dbt_project.yml             # Configurações globais do dbt
└── docker-compose.yml              # Ambiente Airflow/Postgres Local
```

{% enddocs %}