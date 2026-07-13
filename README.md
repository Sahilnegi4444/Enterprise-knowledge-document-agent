# Enterprise Knowledge & Documentation Agent

An enterprise-grade, single-agent autonomous documentation system designed to understand natural language business requests, formulate structured execution plans, gather context via semantic vector RAG and live web search, and compile professional Microsoft Word (`.docx`) documents.

The system is optimized for production efficiency, utilizing a hybrid planning mechanism, task-specific model routing (Groq Llama-3), and lightweight structural self-reflection checks.


## Demo - https://drive.google.com/file/d/19MA7ODVyK49MpJ_lnKATTAhKHjqJ-Tsx/view?usp=sharing
---

## 1. System Architecture

The agent follows clean architecture and SOLID design principles, dividing processing into decoupled services.

```mermaid
graph TD
    A[Client Request] --> B[Security & Validation Service]
    B --> C[Intent Detector]
    C --> D{Hybrid Planner}
    
    D -- Well-Defined Intent --> E[Deterministic Rule-Based Planner]
    D -- Ambiguous / Dynamic Intent --> F[LLM Planner Llama-3.1-8b]
    
    E --> G[Concurrent Tool Router]
    F --> G
    
    G --> H1[RAG Tool ChromaDB]
    G --> H2[Web Search Tool Tavily]
    
    H1 --> I[Context Builder]
    H2 --> I
    
    I --> J[Content Generator Llama-3.3-70b]
    J --> K[Reflection Auditor]
    
    K --> L1{Lightweight Python Audit}
    L1 -- Fails Structure --> M[Correction Retry Loop]
    L1 -- Passes Structure --> L2{LLM Auditor Llama-3.1-8b}
    
    L2 -- Audit Fails < 8.0 --> M
    L2 -- Audit Passes >= 8.0 --> N[Document Compiler python-docx]
    M -- Max 1 Retry --> J
    
    N --> O1[Local Document Persistence]
    N --> O2[JSON Telemetry Audit Logging]
    O1 --> P[API Response]
    O2 --> P
```

### Component Breakdown
* **Security & Validation Service**: Filters prompt injections, rejects empty or excessively long prompts, and ensures structural payload safety.
* **Intent Detector**: Employs deterministic mapping rules to classify requests into categories (e.g., `Proposal`, `Technical Design`, `PRD`, `SOP`, `API Documentation`).
* **Hybrid Planner**: Routes requests based on intent. Standard documents bypass the LLM and construct a deterministic plan instantly. Ambiguous, multi-document, or dynamic requests trigger the LLM Planner.
* **Concurrent Tool Router**: Dispatches tool executions (`RAG` and `Web Search`) in parallel using Python's `asyncio` to reduce latency.
* **Context Builder**: Consolidates results from vector databases, search snippets, and assumptions into an unified context injection prompt.
* **Content Generator**: Synthesizes the context into a structured JSON schema conforming to `StructuredDocument`.
* **Reflection Auditor**: Audits documents for quality. First, a lightweight Python validation checks structural markers (headings, empty blocks). If it passes, LLM reflection is skipped for simple requests. Otherwise, it triggers the LLM auditor for a comprehensive checklist audit.
* **Document Compiler**: Consolidates the validated JSON structure into a styled, corporate Microsoft Word DOCX binary.
* **Audit Logger**: Saves the compiled document locally and logs telemetry metrics (query, intent, tool logs, latency, and reflection scores) to a JSON file.

---

## 2. Ingestion & RAG System

The RAG engine is built to retrieve standard guidelines and corporate formatting templates stored under `knowledge_base/`.

```mermaid
graph LR
    subgraph Ingestion Pipeline
        A[Markdown Guidelines] --> B[Semantic Chunking]
        B --> C[SentenceTransformers Embedding]
        C --> D[(ChromaDB Collection)]
    end
    
    subgraph Retrieval Pipeline
        E[Search Query] --> F[Query Embedding]
        F --> G[Metadata Filter]
        G --> H[(ChromaDB Query)]
        H --> I[Relevant Context Blocks]
    end
```

### Semantic Chunking
Instead of split-character chunking, documents are parsed based on markdown headings (`#`, `##`, `###`). This preserves the structural cohesion of guideline sections, ensuring that complete tables or lists are never cut in half during indexing.

### Vector Storage & Metadata Filtering
* **Embeddings**: Uses `all-MiniLM-L6-v2` locally to generate dense representations.
* **Vector DB**: Persists in a local `ChromaDB` directory.
* **Metadata Filtering**: Standard templates are tagged with document categories (e.g., `document_type="Proposal"`). During planning, the router applies metadata filters to target search queries only to the folders associated with the request type.

---

## 3. Why Web Search & RAG?

The agent operates in a dual-information retrieval structure to synthesize comprehensive enterprise documents:

* **Why RAG?** RAG acts as the agent's internal anchor. It supplies standardized layouts, organization guidelines, style matrices, and corporate templates. This guarantees that all generated documents follow the precise structure and policy bounds required by the enterprise.
* **Why Web Search?** Web search serves as the agent's window to the outside world. It fetches live, transient data such as the latest version of a software library (e.g., LangChain API features), current pricing plans (e.g., DynamoDB tier pricing), or active best practices. This overrides any stale training limits or localized knowledge gaps.

---

## 4. Resilience, Edge Cases, & Fallbacks

To ensure enterprise-grade stability, the system handles external service disruptions gracefully:

| Potential Failure | Mitigation Strategy / Fallback Mechanism |
| :--- | :--- |
| **LLM Planner Crash** | Catches exceptions and builds a deterministic default template plan automatically. |
| **Tavily Search Failure** | Leverages an `async_retry` decorator. If it still fails (e.g., `400 Bad Request` or expired API key), it logs the error body and falls back to a mock data structure so processing can continue. |
| **ChromaDB Connection Issue** | Uses an in-memory fallback list to query local document templates directly from files if the vector store is unreachable. |
| **Malformed LLM Output** | Employs Pydantic validators on LLM JSON structures. If parsing fails, the orchestrator triggers the self-reflection correction loop with a structural hint. |
| **API Rate Limits / Timeout** | All external HTTP endpoints utilize an exponential backoff decorator (`factor=2.0`, `retries=3`) to smooth out transient network blips. |

---

## 5. Engineering Decisions & Performance Trade-offs

### 1. Single-Agent Architecture
- **Decision:** Implemented a single autonomous agent responsible for planning, tool selection, execution, and document generation.
- **Why:** The assignment focuses on autonomous reasoning rather than distributed coordination. A single-agent architecture keeps the workflow simple, predictable, and easier to debug while still demonstrating autonomous planning and dynamic tool orchestration.
- **Trade-off:** While multi-agent systems provide better specialization and parallelism, they introduce additional communication overhead, state management complexity, and orchestration latency that are unnecessary for this assignment.

---

### 2. Task-Specific Model Routing (Multi-Model Workflow)
- **Decision:** Different LLMs are configured through environment variables based on the complexity of each task.

```text
PLANNER_MODEL     -> llama-3.1-8b-instant
GENERATOR_MODEL   -> llama-3.3-70b-versatile
REFLECTION_MODEL  -> llama-3.1-8b-instant
FALLBACK_MODEL    -> llama-3.1-8b-instant
```

- **Why:** Planning and document auditing are lightweight reasoning tasks that do not require a large model, while document generation benefits from the higher reasoning capability of the 70B model.
- **Trade-off:** Managing multiple model configurations adds slight implementation complexity but significantly reduces API cost and overall latency while maintaining document quality.

---

### 3. Two-Stage Document Validation
- **Decision:** Before returning the generated document, the system performs two validation stages:
  1. Lightweight Python validation for document structure.
  2. LLM-based semantic review only when required.

- **Why:** Python efficiently detects structural issues such as missing headings, empty sections, and invalid document formatting without consuming LLM tokens. The smaller LLM is reserved for reviewing content quality and completeness.

- **Trade-off:** This introduces a small amount of additional validation logic but avoids unnecessary LLM calls for structurally invalid outputs and improves the overall quality of generated documents.

---

### 4. Retrieval-Augmented Generation (RAG)
- **Decision:** Internal enterprise templates and engineering best practices are stored as Markdown documents, embedded into ChromaDB, and retrieved before generation.

- **Why:** Grounding the LLM with internal knowledge reduces hallucinations, improves consistency, and allows the agent to generate documents following predefined organizational standards.

- **Trade-off:** Maintaining a knowledge base requires periodic updates, but it is significantly more flexible than fine-tuning the model whenever documentation changes.

---

### 5. Web Search as an Optional Tool
- **Decision:** Web search is executed only when the planner determines that recent or external information is required.

- **Why:** Many requests (e.g., SOPs or project proposals) can be completed entirely from internal knowledge, while requests involving recent technologies or industry trends benefit from external search.

- **Trade-off:** Conditional tool execution reduces unnecessary API calls, lowers latency, and minimizes dependency on external services while preserving access to up-to-date information when needed.

---

### 6. Technical Stack Decisions

#### Why FastAPI?
FastAPI provides high-performance asynchronous request handling, automatic request validation using Pydantic, and interactive OpenAPI documentation through Swagger UI, making it well suited for AI backend services.

#### Why ChromaDB?
ChromaDB is a lightweight, embedded vector database that requires no external infrastructure. It is ideal for MVPs and demonstration projects while still supporting efficient semantic retrieval.

#### Why Groq?
Groq offers low-latency inference with high-performance open-source LLMs, making it an excellent choice for responsive AI applications while remaining cost-effective during development.

#### Why Markdown Knowledge Base?
Markdown files are simple to maintain, version control, and update. They also provide clean semantic structure for chunking and retrieval within the RAG pipeline.

## 6. Professional Document Styling (DOCX Compiler)

The `DocxGenerator` is designed to compile Microsoft Word binaries that match corporate design standards:
* **Typography**: Sets Calibri as default. Heading 1 is set to **18pt bold Deep Navy (`#1A365D`)**, Heading 2 to **14pt bold Accent Blue (`#2B6CB0`)**, and body paragraphs to **11pt Charcoal Slate (`#2D3748`)**.
* **Page Layout**: Implements exact 1-inch margins on all sides.
* **Headers & Footers**: Right-aligned header showing the document title; left-aligned footer showing `Prepared by: [Author]  |  Date: [Date]` with a right-aligned **dynamic page numbering field** (`Page X of Y` field code).
* **Tables**: Styles headers with a solid Deep Navy background, white bold text, and alternating light gray backgrounds (`#F7FAFC`) for table rows.

---

## 7. Future Improvements

* **Conversation Memory**: Implementing stateful session memories to allow users to ask follow-up questions and request specific revisions to generated documents.
* **Multi-Agent Abstraction**: Splitting content generation into a swarm of writing agents, where each sub-agent writes and reviews a single section (e.g., technical diagram vs financial plan) concurrently before final stitching.
* **Redis Caching**: Caching tool results, semantic collections, and final Word compilations to accelerate duplicate queries and reduce LLM token usage.
* **Human-in-the-Loop Approval Workflow**: Adding execution checkpoints where the agent pauses (e.g., after plan formulation) to let the user edit the checklist or tools before executing RAG and generation.
* **Persistent Audit DB**: Migrating local JSON telemetry files to a relational PostgreSQL database with visual analytics dashboards to monitor latency trends, LLM billing, and audit logs.

---

## 8. Getting Started & Usage

### Installation
1. Clone the repository and navigate to the project directory.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
Create a `.env` file in the root directory:
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
FALLBACK_MODEL=llama-3.1-8b-instant
PLANNER_MODEL=llama-3.1-8b-instant
GENERATOR_MODEL=llama-3.3-70b-versatile
REFLECTION_MODEL=llama-3.1-8b-instant

# Tavily Web Search Configuration
TAVILY_API_KEY=your_tavily_api_key

# RAG & Embeddings Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_DIR=./data/chroma
RAG_TOP_K=3
CHUNK_SIZE=500
CHUNK_OVERLAP=75
TEMPERATURE=0.2
```

### Running the System
* **FastAPI Server (API)**:
  ```bash
  uvicorn app.api.main:app --reload
  ```
  Swagger docs will be available at: `http://localhost:8000/docs`
  
* **Run Tests**:
  ```bash
  python -m pytest
  ```
