# Projeto de Assistente Inteligente Parcela Mais

## 1. Introdução

Este documento apresenta a arquitetura e implementação de um agente de linguagem natural que simula um **analista da Parcela Mais**, respondendo a perguntas sobre financiamento de procedimentos médicos com base em um contexto detalhado. A solução foi desenvolvida utilizando Python, bibliotecas do ecossistema LangChain, e modelos de linguagem (LLMs) de múltiplos provedores.

---

## 2. Arquitetura Geral

A arquitetura do projeto é modular e orientada a componentes. Ela se organiza em cinco blocos principais:

1. `telegram_bot.py`: ponto de entrada para interações via Telegram.
2. `interface.py`: gerencia a comunicação com os LLMs.
3. `router.py`: define a lógica para escolha do modelo com base na pergunta.
4. `vector_db.py`: gerencia memória semântica por meio de um banco vetorial.
5. `context_loader.py`: carrega dados contextuais a partir de múltiplas fontes (Slack, Email, Drive etc.).

---

## 3. Componentes e Funcionalidades

### 3.1. `telegram_bot.py` – Bot de Atendimento

Este script inicializa um bot Telegram capaz de:

- Responder qualquer mensagem recebida (sem necessidade de `/start`).
- Iniciar a conversa com uma **mensagem introdutória personalizada**.
- Encaminhar perguntas à interface para geração de respostas com LLM.
- Monitorar inatividade por tempo e encerrar sessões com mensagens de aviso.

**Funções principais:**

- `handle_message`: lida com cada mensagem, ativa a lógica do roteador, envia mensagens de espera e resposta.
- `monitorar_inatividade`: envia lembretes e finaliza sessões após inatividade.
- `enviar_boas_vindas`: envia mensagem introdutória personalizada por usuário.

---

### 3.2. `interface.py` – Integração com LLMs

Este módulo intermedia a chamada aos modelos de linguagem, adicionando:

- **Prompt customizado** com persona da Parcela Mais.
- **Fallback inteligente** caso o modelo principal falhe.
- **Indexação semântica** das perguntas/respostas para memória futura.

**Classe: `LLMInterface`**

- `responder(pergunta: str, modelo: str) -> str`: método principal.
  - Injeta `SystemMessage` com persona e instruções.
  - Envia `HumanMessage` ao LLM escolhido.
  - Realiza até 5 tentativas com backoff exponencial.
  - Aplica fallback com o modelo `mistral_7b_instruct`, por ser o único com chave de acesso gratuita neste contexto (regra ajustável).
  - Indexa a resposta à base vetorial para uso futuro via memória semântica.

---

### 3.3. `router.py` – Roteamento de Modelos

Este componente seleciona o modelo mais adequado com base no conteúdo da pergunta.

**Classe: `LLMRouter`**

- `escolher_modelo(pergunta: str) -> dict`:
  - Analisa palavras-chave sensíveis (ex: "dinheiro", "prazo", "jurídico").
  - Direciona perguntas técnicas sensíveis para modelos mais potentes como GPT-4 ou Claude.
  - Em outros casos, prioriza modelos de menor custo, como GPT-3.5 ou Mistral.

A lógica é simples mas modular, podendo ser estendida para considerar:
- Classificação semântica.
- Custo por token.
- Tempo médio de resposta (latência).

---

### 3.4. `vector_db.py` – Banco Vetorial com FAISS

Este módulo implementa memória semântica com **FAISS**, utilizando **HuggingFace Embeddings** com o modelo `all-MiniLM-L6-v2`.

**Justificativa para o uso do FAISS:**

- É local e leve, ideal para projetos de protótipo sem necessidade de serviços externos.
- Suporta busca semântica eficiente em embeddings.
- Fácil integração com LangChain.
- Não depende de conectividade com serviços pagos como Pinecone ou Weaviate.

**Funções principais:**

- `indexar_mensagem(pergunta, resposta)`: converte em documento, gera embedding e salva no índice vetorial.
- `buscar_contexto(pergunta)`: busca similaridade semântica da nova pergunta com o histórico indexado.

---

### 3.5. `context_loader.py` – Carregamento de Contexto

Este módulo simula a integração com fontes externas de informação. Está estruturado para aceitar múltiplos formatos e origens, como:

- Mensagens de WhatsApp
- Emails (.eml, .msg)
- Arquivos PDF e Word
- Planilhas
- Slack (via API)

**Funções principais:**

- `carregar_contexto_de_arquivos()`: percorre diretórios e carrega arquivos de texto, .pdf, .docx etc.
- `limpar_e_normalizar(texto)`: remove ruído e padroniza para indexação vetorial.
- `criar_documentos(textos)`: transforma textos em `Document` para serem embutidos.

---

## 4. Orquestração do Modelo

A orquestração geral da geração de resposta segue as seguintes etapas coordenadas entre os módulos:

1. **Recepção da pergunta** pelo bot via `telegram_bot.py`, com verificação da sessão e envio da mensagem introdutória se necessário.
2. **Classificação da pergunta** em categorias (jurídica, financeira, técnica etc.) por meio da classe `LLMRouter`.
3. **Escolha do modelo** mais apropriado com base na política definida (ex: balanceada ou baixo custo).
4. **Busca de contexto** no banco vetorial com `vector_db.py`, agregando histórico ou informações similares à pergunta.
5. **Geração da resposta** usando `LLMInterface`, que injeta persona, envia ao modelo e trata possíveis falhas com fallback.
6. **Resposta ao usuário** pelo bot no Telegram.
7. **Armazenamento da interação** no banco vetorial para uso futuro e melhoria de contexto.

Essa orquestração permite modularidade, adaptabilidade a diferentes provedores e personalização do comportamento do assistente conforme as necessidades do negócio.

---

## 5. Estratégias e Decisões Técnicas

### 5.1. Persona do Agente

Foi desenvolvido um prompt fixo que define o analista da Parcela Mais com as seguintes instruções:

- Postura empática, profissional e clara.
- Conhecimento profundo sobre financiamento, crédito e repasse.
- Evitar respostas genéricas.
- Proibido declarar-se IA.

Este prompt é injetado como `SystemMessage` no início de cada interação.

### 5.2. Fallback com Mistral

Como apenas o modelo `mistral_7b_instruct` pode ser acessado gratuitamente via OpenRouter sem API key, foi definido como fallback em caso de falhas. Contudo, essa regra é modular e pode ser alterada para outros modelos ou fornecedores.

---

## 6. Considerações Finais

O projeto entrega um agente conversacional robusto, capaz de:

- Atender dúvidas de clientes via Telegram.
- Utilizar múltiplos LLMs com roteamento inteligente.
- Manter memória semântica por meio de FAISS.
- Ser facilmente expandido com novas fontes de contexto (Slack, WhatsApp, etc.).
- Escalar o uso com outros canais, como API pública ou interface web.

A solução está modularizada, extensível e preparada para futura evolução com foco em escalabilidade e personalização.
