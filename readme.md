
# Auditor de Compliance Dunder Mifflin (Agente Inteligente)

Este repositório é a resposta do trio Cecília, Laura e Lucas do Instituto de Tecnologia e Liderança da T12-EC08 à ponderada "Desafio: A Auditoria do Toby".

O objetivo é desenvolver um **Agente Inteligente de Auditoria** para Toby Flenderson, capaz de ingerir e cruzar dados financeiros e comunicações internas da Dunder Mifflin (Scranton) para garantir o *compliance* da empresa. A arquitetura implementada é baseada em **Retrieval-Augmented Generation (RAG)**, **Análise de Dados Estruturados (Pandas)** e **Orquestração de Agentes (LLM)**.

## Regras de Entrega e Cumprimento

| Requisito | Status | Detalhamento |
| :--- | :--- | :--- |
| **Código Fonte em Python** |  Completo | Implementado no diretório `src/`. |
| **README com Arquitetura e Instruções** |  Completo | Este documento detalha a arquitetura de Agentes, RAG e as ferramentas utilizadas. |
| **Vídeo de Demonstração** | Completo | O sistema atende aos 3 requisitos (4 níveis de complexidade). |
| **Uso de `.env`** | Completo | Chaves de API (e.g., `GEMINI_API_KEY`, `NVIDIA_API_KEY`) são carregadas via `.env`. |
| **Framework de Orquestração** | Completo | Utilização de Agentes com acesso a **Tools/Functions** (baseado em LangChain/Google ADK ou similar). |

## 1\. Arquitetura do Agente de Auditoria

A solução foi construída como um sistema de **Agentes Especializados** coordenados por um Agente Principal (**Toby's Auditor**). A chave da arquitetura é o uso de **Ferramentas (Tools)** que permitem ao Agente Orquestrador interagir com os diferentes *datasets* (TXT, CSV) de forma eficiente.

<div align="center">
  <img src="arquitetura_agentes.png" alt="Diagrama de Arquitetura do Agente de Auditoria Dunder Mifflin" style="max-width: 100%;">
  <figcaption>Figura 1: Arquitetura de Agentes e Ferramentas para a Auditoria. Fonte: Os Autores.</figcaption>
</div>

### Componentes Chave

| Componente | Framework/Tecnologia | Função | Níveis Atendidos |
| :--- | :--- | :--- | :--- |
| **Agente Orquestrador** | LLM (Gemini/NVIDIA NIM) | Interpreta a intenção do usuário e decide qual Tool ou Agente acionar (RAG, Busca em E-mail, Análise CSV). | Todos |
| **Agente RAG (Nível 1)** | Qdrant, `gemini-embedding-001` | Responde a consultas sobre a `politica_compliance.txt`, fornecendo citações como evidência. | Nível 1 |
| **Ferramenta de Análise CSV** | Pandas, Pydantic | Ferramenta que expõe funções como `ferramenta_busca_transacao_id(id)` e `executar_auditoria_simples()` ao Agente. | Nível 3.1, 3.2 |
| **Ferramenta de Busca em E-mail** | Python Nativo (Regex/String) | Permite buscar por termos e padrões no `emails_internos.txt` para contextualização e conspiração. | Nível 2, 3.2 |

## 2\. Implementação por Nível de Desafio

### 2.1. Nível 1: Chatbot de Compliance (RAG)

O RAG (Retrieval-Augmented Generation) foi implementado para consumir o documento `politica_compliance.txt`.

  * **Fluxo de Implementação:** *Load* $\rightarrow$ *Sanitizing* $\rightarrow$ **Chunking Semântico** $\rightarrow$ *Embedding* $\rightarrow$ *Storing*.
  * **Chunking Estratégico:** Optou-se por um *chunking* manual/estrutural com base na separação de seções (`==...==`) do documento, garantindo que cada *chunk* contivesse uma regra completa, otimizando a precisão da recuperação (o que é superior ao *chunking* baseado apenas em tokens).
  * **Vector Store:** Utilização do **Qdrant** para armazenamento vetorial e `gemini-embedding-001` para a criação dos embeddings.
  * **Entrega:** O Agente RAG não apenas responde à pergunta, mas garante que a **política seja citada** (prova) para justificar a resposta.

### 2.2. Nível 3.1: Detecção de Fraudes por Regras Diretas

Este nível foca na verificação de violações de *compliance* que são evidentes apenas pela análise do `transacoes_bancarias.csv`, sem necessidade de contexto de comunicação.

  * **Módulo:** `src/auditoria/auditor_rules.py`.
  * **Tool:** O Agente utiliza a função `executar_auditoria_simples()` que aplica as seguintes regras extraídas da política:
      * **R001 (Limite de Gasto):** Transações acima de **$500.00** exigem aprovação de CFO.
      * **R003 (Local Restrito):** Gasto em locais explicitamente proibidos (e.g., "Hooters").
      * **R004 (Itens Proibidos):** Compras de itens não reembolsáveis ou proibidos (e.g., "algemas", "espada").
  * **Resultado:** Geração de um DataFrame com todas as transações violadas e o código da regra (`R001`, `R003`, etc.) como justificativa.

### 2.3. Nível 2 e Nível 3.2: Conspiração e Fraude Contextual

Estes níveis representam a maior complexidade, exigindo que o Agente Orquestrador cruze informações não estruturadas (`emails_internos.txt`) com dados estruturados (`transacoes_bancarias.csv`).

#### A. Verificação de Conspiração (Nível 2)

  * **Fluxo:** O Agente Orquestrador utiliza a **Ferramenta de Busca em E-mail** para buscar padrões de comunicação entre Michael Scott e outros funcionários usando palavras-chave (`Toby`, `plano`, `RH`).
  * **Justificativa:** O LLM processa o resultado bruto dos e-mails e sintetiza um relatório para Toby, citando os trechos relevantes como evidência de que a desconfiança é (ou não é) verídica.

#### B. Fraude Contextual (Nível 3.2)

  * **Exemplo:** Detecção de **Smurfing** (dividir transações grandes em pequenas para evitar limites) combinando **Intenção** e **Execução**.
  * **Fluxo:**
    1.  **Prova de Intenção:** O Agente usa a **Ferramenta de Busca em E-mail** para encontrar e-mails com termos como "dividir", "evitar limite", ou "reembolso X".
    2.  **Prova de Execução:** Se o e-mail citar um ID ou um valor suspeito, o Agente chama a **Ferramenta de Análise CSV** (`ferramenta_busca_transacao_id()`).
    3.  **Relatório:** O Agente combina a **evidência do e-mail** (o acordo) com a **evidência da transação** (o registro financeiro) para provar a fraude.

-----

## 3\.  Como Rodar a Aplicação (Instruções)

### Pré-requisitos

1.  **Docker** instalado e funcionando.
2.  Chave de API do provedor LLM (Gemini ou NVIDIA) disponível.

### 3.1. Configuração do Ambiente

1.  Clone o repositório:

    ```bash
    git clone [LINK_DO_REPOSITÓRIO]
    cd PONDERADA-CHATBOT
    ```

2.  Pegue o arquivo .env que enviaremos a parte!

### 3.2. Rodando com Docker (Recomendado)

O uso do Docker garante que todas as dependências do `requirements.txt` e o ambiente Python sejam consistentes.

1.  **Build da Imagem:**

    ```bash
    docker build -t chatbot:latest .
    ```

2.  **Execução e Mapeamento de Volume:**
    Este comando roda a aplicação no modo interativo (`-it`) e mapeia o diretório local para o contêiner (`-v`), permitindo que você altere o código fonte e execute a aplicação dentro do ambiente isolado.

    ```bash
    docker run -it --rm -v $(pwd):/usr/src/chatbot chatbot:latest /bin/bash
    ```

3.  **Execução dos Módulos (Dentro do Contêiner):**

      * **Nível 1 (RAG Chatbot):**
        ```bash
        python src/parte-1-rag/test.py
        ```
      * **Nível 3.1 (Auditoria Simples):**
        ```bash
        python src/auditoria/main_orchestrator.py
        ```
      * **Nível 2 e 3.2 (Agente Orquestrador Completo):**
        (Assumindo que o Agente Principal está aqui, conforme sua implementação final)
        ```bash
        python src/main_agent.py
        ```

### 3.3. Instalação Local (Alternativa)

Se preferir rodar localmente (não recomendado, devido à arguição):

1.  Crie e ative um ambiente virtual.
2.  Instale as dependências: `pip install -r requirements.txt`.
3.  Execute os *scripts* na ordem desejada.

-----

## 4\. Material Complementar

  * `data/politica_compliance.txt`: Regras para o RAG.
  * `data/transacoes_bancarias.csv`: Dados para análise estruturada (Nível 3.1 e 3.2).
  * `data/emails_internos.txt`: Dados para análise não estruturada (Nível 2 e 3.2).
  * `src/parte-1-rag/`: Implementação do RAG com Qdrant.
  * `src/auditoria/`: Módulo de preparação de dados e regras de *compliance* (Tools).