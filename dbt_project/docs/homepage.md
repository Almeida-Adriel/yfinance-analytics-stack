{% docs __overview__ %}

# yfinance-analytics-stack | Portal de Governança de Dados

Bem-vindo ao centro de documentação técnica e dicionário de dados da nossa pipeline financeira. Este portal foi projetado para garantir total transparência sobre a linhagem dos dados (*lineage*), regras de negócio e a estrutura de modelagem SQL das nossas análises de mercado.

---

## Governança e Arquitetura de Tabelas (Medallion)

A modelagem de dados isola o ciclo de vida da informação em três camadas lógicas dentro do PostgreSQL, garantindo que o dashboard em **Streamlit** consuma apenas dados limpos e homologados.

### Camada Bronze (Raw Data)
* **Objetivo:** Armazenamento fiel dos dados brutos extraídos via API do Yahoo Finance (`yfinance`).
* **Frequência & SLA:** Diário (D-1), agendado e orquestrado via **Apache Airflow**.
* **Estratégia de Carga:** Ingestão Incremental Inteligente com proteção física no banco contra duplicidade via cláusula `ON CONFLICT DO NOTHING`.
* **Tabela Core:** `public.stocks`

### 🥈 Camada Silver (Staging & Cleansing)
* **Objetivo:** Higienização, padronização de nomenclatura (*snake_case*), tratamento de fusos horários e tipagem rigorosa dos dados estruturados.
* **Materialização:** `view` (Garante eficiência e dados sempre atualizados sem custo de armazenamento duplicado).
* **Modelo dbt:** `silver.stg_stocks`

### 🥇 Camada Gold (Business & Analytics)
* **Objetivo:** Modelagem dimensional e tabelas fato prontas para consumo analítico, consolidadas com métricas avançadas de performance.
* **Regras de Negócio Implementadas:** Aplicação de funções de janela analítica (`LAG`, `PARTITION BY`) para entrega de:
  * *Retorno Diário (%):* Variação percentual do preço de fechamento ajustado contra o dia anterior.
  * *Volatilidade (Amplitude):* Cálculo de oscilação do preço do ativo para identificar dispersão e risco de mercado.
  * *Liquidez Financeira:* Mapeamento do volume financeiro movimentado para acompanhar o fluxo de capital das ações.
* **Materialização:** `table` (Otimizada para alta performance de leitura no Dashboard).
* **Modelo dbt:** `gold.fct_stocks_metrics`

---

## 🗺️ Como Navegar neste Portal

Utilize o menu de navegação à esquerda para explorar os metadados do projeto:
* **Explore as Camadas (Tags/Sources):** Navegue pelas pastas `sources` e `models` para inspecionar o código SQL de cada transformação e a descrição de cada coluna individualmente.
* **Gráfico de Linhagem (Lineage Graph):** Clique no ícone flutuante de gráfico no canto inferior direito. Ele abrirá o mapa visual interativo que mostra exatamente o caminho que o dado percorre da API do Yahoo Finance até a tabela Fato final.

{% enddocs %}