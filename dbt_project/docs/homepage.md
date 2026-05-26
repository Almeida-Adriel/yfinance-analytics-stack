{% docs __overview__ %}

# yfinance-analytics-stack

Bem-vindo à documentação técnica da pipeline financeira. Este portal contém o dicionário de dados e a linhagem dos modelos SQL (Lineage Graph)

---

## Governança e Arquitetura de Tabelas (Medallion)

A modelagem de dados isola o ciclo de vida da informação em três camadas lógicas dentro do PostgreSQL, garantindo que o dashboard em **Streamlit** consuma apenas dados limpos e homologados.

### Camada Bronze (Raw Data)
* **Objetivo:** Armazenamento bruto dos dados extraídos do Yahoo Finance.
* **Estratégia de Carga:** Incremental diária via Airflow (*Append-Only*).
* **Tabela Core:** `public.stocks`

### Camada Silver (Staging & Cleaning)
* **Objetivo:** Limpeza, padronização de nomenclatura, tratamento de fusos horários e tipagem de dados estruturados (`CAST`).
* **Regra de Negócio:** Filtra linhas inválidas e garante unicidade por ticker/data.
* **Modelo dbt:** `silver.stg_stocks`

### Camada Gold (Business & Analytics)
* **Objetivo:** Tabelas prontas para consumo analítico, agregadas com métricas de performance financeira.
* **Regra de Negócio:** Aplicação de janelas analíticas (`LAG`, `PARTITION BY`) para computar:
  * Variação percentual diária do fechamento.
  * Média móvel acumulada.
  * Volatilidade e volume financeiro ponderado.
* **Modelo dbt:** `gold.fct_stocks_metrics`

---

## Navegação Útil

Utilize a barra lateral esquerda para explorar os metadados do projeto:
* **Sources:** Explore a tabela de origem vinda da ingestão (`public.stocks`).
* **Models:** Detalhe os scripts SQL de transformação, o tipo de materialização (View/Table) e a descrição de cada coluna individualmente.
* **Lineage Graph:** Clique no botão inferior direito `[ 📊 ]` para visualizar o gráfico de linhagem de ponta a ponta e entender como a camada Gold depende diretamente do Staging.

{% enddocs %}