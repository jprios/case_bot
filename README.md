# Parcela Saúde Intelligent Assistant Project

## 1. Introduction

This document presents the architecture and implementation of a natural language agent that simulates a **Parcela Saúde analyst**, responding to questions about financing medical procedures based on detailed context. The solution was developed using Python, libraries from the LangChain ecosystem, and language models (LLMs) from multiple providers.

---

## 2. General Architecture

The project architecture is modular and component-oriented. It is organized into five main blocks:

1. `telegram_bot.py`: entry point for Telegram interactions.
2. `interface.py`: manages communication with LLMs.
3. `router.py`: defines the logic for model selection based on the question.
4. `vector_db.py`: manages semantic memory through a vector database.
5. `context_loader.py`: loads contextual data from multiple sources (Slack, Email, Drive, etc.).

---

## 3. Components and Features

### 3.1. `telegram_bot.py` – Support Bot

This script initializes a Telegram bot capable of:

- Responding to any received message (no `/start` required).
- Starting the conversation with a **custom introductory message**.
- Forwarding questions to the interface for LLM-based responses.
- Monitoring inactivity over time and ending sessions with warning messages.

**Main functions:**

- `handle_message`: processes each message, triggers router logic, sends waiting and response messages.
- `monitorar_inatividade`: sends reminders and ends sessions after inactivity.
- `enviar_boas_vindas`: sends a personalized introductory message to each user.

---

### 3.2. `interface.py` – LLM Integration

This module mediates calls to language models, adding:

- **Custom prompt** with the Parcela Saúde persona.
- **Intelligent fallback** in case the main model fails.
- **Semantic indexing** of questions/answers for future memory.

**Class: `LLMInterface`**

- `responder(pergunta: str, modelo: str) -> str`: main method.
  - Injects `SystemMessage` with persona and instructions.
  - Sends `HumanMessage` to the chosen LLM.
  - Performs up to 5 attempts with exponential backoff.
  - Applies fallback with the `mistral_7b_instruct` model, as it is the only one with free access in this context (adjustable rule).
  - Indexes the answer into the vector database for future semantic memory usage.

---

### 3.3. `router.py` – Model Routing

This component selects the most appropriate model based on the content of the question.

**Class: `LLMRouter`**

- `escolher_modelo(pergunta: str) -> dict`:
  - Analyzes sensitive keywords (e.g., "money", "term", "legal").
  - Routes sensitive technical questions to more powerful models like GPT-4 or Claude.
  - In other cases, prioritizes lower-cost models like GPT-3.5 or Mistral.

The logic is simple but modular, and can be extended to consider:
- Semantic classification.
- Cost per token.
- Average response time (latency).

---

### 3.4. `vector_db.py` – Vector Database with FAISS

This module implements semantic memory with **FAISS**, using **HuggingFace Embeddings** with the `all-MiniLM-L6-v2` model.

**Reasons for using FAISS:**

- It is local and lightweight, ideal for prototype projects without the need for external services.
- Supports efficient semantic search in embeddings.
- Easy integration with LangChain.
- Does not depend on connectivity with paid services like Pinecone or Weaviate.

**Main functions:**

- `indexar_mensagem(pergunta, resposta)`: converts into a document, generates embedding, and saves it in the vector index.
- `buscar_contexto(pergunta)`: searches for semantic similarity between the new question and the indexed history.

---

### 3.5. `context_loader.py` – Context Loading

This module simulates integration with external information sources. It is structured to accept multiple formats and origins, such as:

- WhatsApp messages
- Emails (.eml, .msg)
- PDF and Word files
- Spreadsheets
- Slack (via API)

**Main functions:**

- `carregar_contexto_de_arquivos()`: scans directories and loads text, .pdf, .docx files, etc.
- `limpar_e_normalizar(texto)`: removes noise and standardizes content for vector indexing.
- `criar_documentos(textos)`: transforms texts into `Document` objects for embedding.

---

## 4. Model Orchestration

The general orchestration of the response generation follows these coordinated steps among modules:

1. **Receive the question** via the bot in `telegram_bot.py`, check session status, and send the introductory message if necessary.
2. **Classify the question** into categories (legal, financial, technical, etc.) through the `LLMRouter` class.
3. **Select the most appropriate model** based on the defined policy (e.g., balanced or low-cost).
4. **Search for context** in the vector database with `vector_db.py`, adding history or information similar to the question.
5. **Generate the answer** using `LLMInterface`, which injects the persona, sends it to the model, and handles possible failures with fallback.
6. **Send the answer** to the user via the Telegram bot.
7. **Store the interaction** in the vector database for future use and context improvement.

This orchestration allows modularity, adaptability to different providers, and customization of the assistant's behavior according to the needs of the project.

---

## 5. Strategies and Technical Decisions

### 5.1. Agent Persona

A fixed prompt was developed that defines the Parcela Saúde analyst with the following instructions:

- Empathetic, professional, and clear demeanor.
- Deep knowledge of financing, credit, and disbursement.
- Avoid generic answers.
- Forbidden to declare itself as AI.

This prompt is injected as a `SystemMessage` at the beginning of each interaction.

### 5.2. Fallback with Mistral

As only the `mistral_7b_instruct` model can be accessed for free via OpenRouter without an API key, it was set as the fallback in case of failures. However, this rule is modular and can be changed to other models or providers.

---

## 6. Final Considerations

The project delivers a robust conversational agent capable of:

- Handling customer questions via Telegram.
- Using multiple LLMs with intelligent routing.
- Maintaining semantic memory through FAISS.
- Being easily expanded with new context sources (Slack, WhatsApp, etc.).
- Scaling to other channels, such as public API or web interface.

The solution is modularized, extensible, and prepared for future evolution with a focus on scalability and customization.
