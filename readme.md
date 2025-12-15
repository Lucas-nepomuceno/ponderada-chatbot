# Auditor de Compliance Dunder Mifflin (Agente Inteligente)

Este repositório é a resposta do trio Cecília, Laura e Lucas do Instituto de Tecnologia e Liderança da T12-EC08 à ponderada "Desafio: A Auditoria do Toby".

O objetivo é desenvolver um **Agente Inteligente de Auditoria** para Toby Flenderson, capaz de ingerir e cruzar dados financeiros e comunicações internas da Dunder Mifflin (Scranton) para garantir o *compliance* da empresa. A arquitetura implementada é baseada em **Retrieval-Augmented Generation (RAG)**, **Análise de Dados Estruturados (Pandas)** e **Orquestração de Agentes (LLM)**.

## Regras de Entrega e Cumprimento

| Requisito | Status | Detalhamento |
| :--- | :--- | :--- |
| **Código Fonte em Python** | Completo | Implementado no diretório `src/`. |
| **README com Arquitetura e Instruções** | Completo | Este documento detalha a arquitetura de Agentes, RAG e as ferramentas utilizadas. |
| **Vídeo de Demonstração** | Completo | O sistema atende aos 3 requisitos (4 níveis de complexidade). |
| **Uso de `.env`** | Completo | Chaves de API (e.g., `GEMINI_API_KEY`, `NVIDIA_API_KEY`) são carregadas via `.env`. |
| **Framework de Orquestração** | Completo | Utilização de Agentes com acesso a **Tools/Functions** (baseado em LangChain/Google ADK ou similar). |

## 1\. Arquitetura do Agente de Auditoria

A solução foi construída como um sistema de **Agentes Especializados** coordenados por um Agente Principal (**Toby's Auditor**). A chave da arquitetura é o uso de **Ferramentas (Tools)** que permitem ao Agente Orquestrador interagir com os diferentes *datasets* (TXT, CSV) de forma eficiente.

### Componentes Chave

| Componente | Framework/Tecnologia | Função | Níveis Atendidos |
| :--- | :--- | :--- | :--- |
| **Agente Orquestrador** | LLM (Gemini/NVIDIA NIM) | Interpreta a intenção do usuário e decide qual Tool ou Agente acionar (RAG, Busca em E-mail, Análise CSV). | Todos |
| **Agente RAG (Nível 1)** | Qdrant, `gemini-embedding-001` | Responde a consultas sobre a `politica_compliance.txt`, fornecendo citações como evidência. | Nível 1 |
| **Ferramenta de Análise CSV** | Pandas, Pydantic | Ferramenta que expõe funções como `ferramenta_busca_transacao_id(id)` e `executar_auditoria_simples()` ao Agente. | Nível 3.1, 3.2 |
| **Ferramenta de Busca em E-mail** | Python Nativo (Regex/String) | Permite buscar por termos e padrões no `emails.txt` para contextualização e conspiração. | Nível 2, 3.2 |

## 2\. Implementação por Nível de Desafio

### 2.1. Nível 1: Chatbot de Compliance (RAG)

  O RAG (Retrieval Augmented-Generation) é feito a partir do seguinte fluxo: Load -\> Sanitizing -\> Chunking -\> Embedding & Storing. Essa seção do projeto está contemplada no arquivo `src/parte-1-rag/rag/rag_politica_complicance.py`. No entanto, todos os arquivos da pasta `src/parte-1-rag` contribuem para tal. Abaixo, explica-se como o RAG foi feito para o `politica_compliance.txt` em vias de criar um chatbot que responde dúvidas acerca da política da empresa.

  Para começar o RAG, foi necessário carregar o `politica_compliance.txt`. Como o documento estava localmente conosco (na pasta `documents`), cumprir este passo foi simples: bastou carregá-lo em uma variável usando as funções `open()` e `read()` nativas do Python.

  Em seguida, criou-se os chunks. Primeiro, pensou-se em utilizar a biblioteca **LangChain** para quebrar o texto com base no número de tokens. No entanto, como o documento é semanticamente estruturado em seções, optou-se por um *chunking* manual. Para tanto, definimos e utilizamos a função `create_chunks()` e sua auxiliar `include_header()`. Essas, em conjunto, quebram o texto com base na separação que o próprio faz de suas seções, utilizando o "==...==" para iniciá-las e terminá-las. Ao final, utilizou-se a **LangChain** para deixar os *chunks* em formato adequado para passarem pelo embedding (função `create_documents`).

  Por último, fez-se o *embedding* e *storing* dos *chunks*. Para tanto, usou-se o modelo de embedding `gemini-embedding-001` e a Vector Store do Qdrant. Isso está mais claramente definido no arquivo `qdrant_vector_store.py` dentro de `src/parte-1-rag/rag/vector_store`, onde definimos a classe VectorStore, inicializando o cliente e a coleção "ponderada-parte-1" no Qdrant com o embedding supracitado. Essa classe também disponibiliza os métodos `add_documents` e `similarity_search` do QdrantVectorStore. Então, no arquivo `rag_politica_compliance.py`, carregamos os chunks na Qdrant usando `add_documents`.

  Abaixo, pode-se verificar o grafo pelo embedding.

<div style="align: center;">
<sup>Figura 1: Grafo com nós de chunks</sup>

![Grafo com todos os chunks](image.png)

<sub>Fonte: os autores</sub>

</div>

&emsp; Em `src/parte-1-rag/test.py`, inicializa-se um agente da NVIDIA com acesso a essa tool que responde dúvidas do cliente no terminal, enquanto mantém o histórico da conversa.

<div style="align: center;">
<sup>Figura 1: Grafo com nós de chunks</sup>

![Teste do chat com RAG consumindo a politica_compliance.txt](image-1.png)

<sub>Fonte: os autores</sub>
</div>

### 2.2. Módulo de Auditoria e Dados

Preparação e Limpeza de Dados, Detecção de Fraudes por Regras (Nível 3.1) e Desenvolvimento de Ferramentas (Tools) para Agentes de IA.

-----

#### 1\. Estrutura e Arquitetura do Módulo

Toda a lógica foi encapsulada no pacote `src/auditoria` para garantir modularidade e evitar conflitos de dependências.

| Caminho | Tipo | Propósito |
| :--- | :--- | :--- |
| `src/auditoria/` | **Pacote** | Contém toda a lógica de dados e regras. |
| `src/auditoria/data_preparation.py` | Script | **Responsável pela entrada de dados (I/O).** Carrega o CSV, limpa, padroniza e garante IDs únicos. |
| `src/auditoria/auditor_rules.py` | Script | **Responsável pela lógica de negócios.** Implementa as regras de compliance (Nível 3.1) e desenvolve as Tools. |
| `src/auditoria/main_orchestrator.py` | Script | **Ponto de Execução e Teste.** Orquestra o fluxo de trabalho para validação e demonstração. |

-----

#### 2\. Nível de Entrega: Detecção de Fraudes (Nível 3.1)

O módulo implementa o primeiro nível de detecção, focado em violações diretas da política de compliance (`politica_compliance.txt`).

##### 2.1. Função Principal de Validação

| Função | Descrição |
| :--- | :--- |
| `executar_auditoria_simples()` | Função mestra que gerencia o fluxo de trabalho: carrega os dados brutos, limpa-os e aplica todas as regras de compliance, retornando um DataFrame apenas com as transações violadas e suas justificativas. |

##### 2.2. Regras Implementadas (Extraídas da Política)

As seguintes regras são verificadas linha por linha no DataFrame:

| ID da Regra | Tipo | Condição | Ação |
| :--- | :--- | :--- | :--- |
| **R001\_LIMITE\_ALTO** | Limite de Gasto | `valor` \> $500.00 | Sinaliza transações que exigem aprovação do CFO. |
| **R003\_RESTRITO\_LOCAL** | Gasto Proibido | `descricao` contém "Hooters" | Viola a política de locais de reembolso. |
| **R004\_PROIBIDO\_ITENS** | Itens Proibidos | `descricao` contém palavras-chave (ex: "algemas", "espada", "frigobar", "spa") | Sinaliza compras estritamente proibidas ou não reembolsáveis. |

-----

#### 3\. Entregas Críticas para o Agente de IA (Pessoa 3)

A peça mais importante para a integração com a Cecilia é a Ferramanta de Acesso aos dados.

##### 3.1. Ferramenta de Busca de Transação (Tool)

| Função | Finalidade | Módulo |
| :--- | :--- | :--- |
| `ferramenta_busca_transacao_id(id_transacao)` | Permite que o **Agente de IA** (LLM) pesquise qualquer ID de transação mencionado em um e-mail. Retorna todos os detalhes da transação em formato **JSON**. | `auditor_rules.py` |

**Integração:** A Tool utiliza a variável global interna (`df_transacoes_global`) que é preenchida por `executar_auditoria_simples()`. Isso permite que a Tool seja chamada pelo Agente (que só passa o ID) e ainda acesse o DataFrame limpo.

##### 3.2. Estrutura de Dados (Nível 3.2)

O módulo `auditor_rules.py` também inclui a função **`detectar_smurfing()`** (fraude por estruturação) que será utilizada no Nível 3.2 para analisar padrões de gasto divididos pelo mesmo funcionário/fornecedor/data, antecipando a lógica de Fraude Contextual.

-----

### 2.3. Nível 2 e Nível 3.2: Conspiração e Fraude Contextual

Estes níveis representam a maior complexidade, exigindo que o Agente Orquestrador cruze informações não estruturadas (`emails.txt`) com dados estruturados (`transacoes_bancarias.csv`).

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

## 3\. Como Rodar a Aplicação (Instruções)

### Pré-requisitos

1.  **Docker** instalado e funcionando.
2.  Chave de API do provedor LLM (Gemini ou NVIDIA) disponível.

### 3.1. Configuração do Ambiente

1.  Clone o repositório:

    ```bash
    git clone [LINK_DO_REPOSITÓRIO]
    cd PONDERADA-CHATBOT
    ```

2.  Pegue o arquivo .env que enviaremos a parte\!

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

3.  **Finalização de Setup (opcional):**
    Após as alterações, rode o comando:

    ```bash
    pip freeze > requirements.txt && \
    exit
    ```

## 4\. Interface de Linha de Comando (CLI)

O projeto é acessado e demonstrado através de uma interface de console unificada, que atua como um *router* para as diversas funcionalidades de Auditoria e RAG (Retrieval Augmented Generation).

### 4.1. Como Acessar a CLI

A CLI é executada pelo script `main.py` na raiz do projeto (após garantir que o ambiente Docker está ativo e o volume está montado).

```bash
# Se estiver no terminal do container Docker:
python main.py
```

### 4.2. Fluxo de Navegação e Funcionalidades

O sistema inicia perguntando a identidade do usuário e, com base nela, libera diferentes níveis de acesso e ferramentas de Auditoria.

#### Rota A: Usuário Não-Toby (Consulta de Compliance)

Acesso para qualquer funcionário que precise de orientação sobre a política da empresa.

| Opção | Ação | Módulo Acionado | Finalidade |
| :--- | :--- | :--- | :--- |
| **2** | Sou outro funcionário e quero saber sobre a política de compliance | `start_chat()` | Inicia um chatbot interativo que consulta a `politica_compliance.txt` usando o RAG para responder a dúvidas. |

#### Rota B: Usuário Autenticado (Toby Flenderson)

O acesso às ferramentas de auditoria e verificação de fraude é restrito a Toby, o Auditor de RH, mediante autenticação de senha (lida do arquivo `.env`).

Após a autenticação, as seguintes opções se tornam disponíveis:

| Opção | Ação | Módulo Acionado | Finalidade |
| :--- | :--- | :--- | :--- |
| **1** | Desejo realizar uma auditoria simples | `executar_auditoria_simples()` | Executa a **Auditoria Nível 3.1**, verificando o `transacoes_bancarias.csv` contra regras diretas (limites de valor, itens proibidos). |
| **2** | Desejo realizar um auditoria de fraude contextual | `executar_agente_fraude_contextual()` | Executa o **Agente de Fraude Contextual (Nível 3.2)**, que analisa e-mails em busca de contexto e usa a Tool de busca de transação para validar a fraude. |
| **3** | Desejo verificar o chat | `start_chat()` | Permite que Toby acesse o mesmo chatbot de consulta de compliance. |

### 4.3. Estrutura de Autenticação

A segurança da CLI é implementada carregando a chave `SENHA` do arquivo `.env`. O acesso às funcionalidades de auditoria é totalmente dependente dessa variável.

## 5\. Material Complementar

  * `documents/politica_compliance.txt`: Regras para o RAG.
  * `documents/transacoes_bancarias.csv`: Dados para análise estruturada (Nível 3.1 e 3.2).
  * `documents/emails.txt`: Dados para análise não estruturada (Nível 2 e 3.2).
  * `src/parte-1-rag/`: Implementação do RAG com Qdrant.
  * `src/auditoria/`: Módulo de preparação de dados e regras de *compliance* (Tools).