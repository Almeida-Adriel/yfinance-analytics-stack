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

## Pré-requisitos e Como Rodar o Projeto

### 1. Pré-requisitos Básicos
Antes de iniciar, certifique-se de ter instalado em seu ambiente de desenvolvimento:
* **Git** (Para clonagem do repositório)
* **Docker Engine** v20.10+
* **Docker Compose** v2.0+

### 2. Clonando o Repositório
Abra o terminal na pasta onde deseja salvar o projeto e execute o comando abaixo para realizar o clone da aplicação:

```bash
git clone [https://github.com/Almeida-Adriel/yfinance-analytics-stack.git](https://github.com/Almeida-Adriel/yfinance-analytics-stack.git)
```

### 3. Navegue até a raiz do projeto
```bash
cd yfinance-analytics-stack
```

### 4. Configurando as Conexões (adicione um arquivo em C:\Users\{seu usuário}\.dbt\profiles.yml) deixei arquivos exemplo na raiz do projeto
```bash
./profiles-example.yml
./example.env
```

### 5. Inicializando a Infraestrutura (Docker Compose)
```bash
docker-compose up -d
```

### 5. Portais de acesso disponiveis
| Serviço / Aplicação | URL Local | Credenciais de Acesso |
| :--- | :--- | :--- |
| **Apache Airflow Webserver** | [http://localhost:8080](http://localhost:8080) | Usuário: `admin` \| Senha: `admin` |
| **dbt Docs (Portal Interativo)** | [http://localhost:8081](http://localhost:8081) | Acesso Livre |
| **Streamlit Analytics Dashboard** | [http://localhost:8501](http://localhost:8501) | Acesso Livre |
