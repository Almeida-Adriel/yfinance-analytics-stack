# yfinance-analytics-stack

Bem-vindo à documentação oficial do **yfinance-analytics-stack**! Este projeto é uma plataforma automatizada de Engenharia de Dados voltada para a captura, transformação e disponibilização de métricas financeiras das principais ações do mercado (AAPL, AMZN, GOOGL, MSFT, NVDA).

---

## Arquitetura de Dados

O projeto segue os princípios da **Medallion Architecture** (Camadas Bronze, Silver e Gold), garantindo organização, rastreabilidade e performance:

```
                        [ Apache Airflow ] ──(Ingestão Diária)──> [ Python / yfinance ]
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │    PostgreSQL   │
                                          │      Local      │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │       dbt       │
                                          │ (Transformação) │
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

* **Orquestração:** [Apache Airflow (Astro CLI)](https://airflow.apache.org/) - Gerencia o agendamento diário, controle de variáveis de execução e fluxo da pipeline.
* **Coleta de Dados:** [yfinance](https://github.com/ranaroussi/yfinance) - Scripts em Python utilizando Pandas para consumo otimizado da API do Yahoo Finance.
* **Transformação & Modelagem:** [dbt (data build tool)](https://www.getdbt.com/) - Engenharia de transformações SQL, testes de qualidade de dados e documentação do lineage.
* **Banco de Dados:** [PostgreSQL 16](https://www.postgresql.org/) - Banco de dados relacional rodando localmente em container para o Data Warehouse.
* **Visualização:** [Streamlit](https://streamlit.io/) - Dashboard interativo em Python consumindo a camada Gold para análise de indicadores.
* **Administração do Banco:** [pgAdmin 4](https://www.pgadmin.org/) - Interface web para gerenciamento e consultas rápidas ao ecossistema PostgreSQL.

---

## Pré-requisitos e Como Rodar o Projeto

### 1. Pré-requisitos Básicos
Antes de iniciar, certifique-se de ter instalado em seu ambiente de desenvolvimento:
* **Git** (Para clonagem do repositório)
* **Docker Engine** v20.10+
* **Docker Compose** v2.0+

### 2. Clonando o Repositório
Abra o terminal na pasta onde deseja salvar o projeto e execute o comando abaixo para realizar o clone da aplicação:

```bash
git clone https://github.com/Almeida-Adriel/yfinance-analytics-stack.git
```

### 3. Navegue até a raiz do projeto
```bash
cd yfinance-analytics-stack
```

### 4. Configurando as Conexões
Para que os containers se comuniquem corretamente com o seu banco de dados, utilize os arquivos de exemplo disponibilizados na raiz do projeto como guia:

 - Copie o arquivo ./example.env para um novo arquivo chamado .env e preencha com as suas credenciais do seu banco de dados em nuvem ou o local.
        ```bash
        cp example.env .env
        ```

 - Mapeie o arquivo de credenciais do dbt (profiles.yml) apontando para o seu banco conforme o modelo em ./profiles-example.yml.

### 5. Inicializando a Infraestrutura (Docker Compose)
```bash
docker-compose up -d
```

### 6. Portais de acesso disponiveis
| Serviço / Aplicação | URL Local | Credenciais de Acesso |
| :--- | :--- | :--- |
| **Apache Airflow Webserver** | [http://localhost:8080](http://localhost:8080) | Usuário: `admin` \| Senha: `admin` |
| **Banco de Dados pgadmin** | [http://localhost:8080](http://localhost:5050) | Usuário: `admin@admin.com` \| Senha: `admin` |
| **dbt Docs (Portal Interativo)** | [http://localhost:8081](http://localhost:8081) | Acesso Livre |
| **Streamlit Analytics Dashboard** | [http://localhost:8501](http://localhost:8501) | Acesso Livre |
