# UtilPulse Command Centre

> **Real-Time Conversational Intelligence Platform for Municipal Water Distribution Networks, Asset Reliability, and Water Quality Compliance.**

---

## Architecture & Tech Stack

- **Frontend**: Streamlit with custom Swiss editorial design system (Space Grotesk, Inter, JetBrains Mono)
- **LLM Pipeline**: Groq API (`openai/gpt-oss-120b`) with temperature-controlled JSON intent extraction & natural language synthesis
- **RAG Knowledge Base**: ChromaDB with `all-MiniLM-L6-v2` embeddings over IS 10500:2012, CPHEEO guidelines, and WHO drinking water standards
- **Telemetry Database**: Local indexed SQLite database (`water_nodes` table, 163,904 records across 10 Indian metropolitan cities)
- **Visuals**: Plotly Express & Graph Objects tailored with dark transparent editorial theme
- **Security**: Role-Based Access Control (Admin, Zone Operator, Quality Analyst, Executive)

---

## Prerequisites

- **Python**: Version `3.10`, `3.11`, or `3.12` installed.
- **Git**: Installed on your system.
- **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com/keys).

---

## Setup & Running on a New Machine

### 1. Clone the Repository
```bash
git clone <YOUR_GIT_REPOSITORY_URL>
cd UCC
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to create your `.env` file:

**On Windows:**
```powershell
copy .env.example .env
```

**On Linux / macOS:**
```bash
cp .env.example .env
```

Open `.env` and paste your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 5. Launch the Application
```bash
streamlit run main.py
```

The application will start and open in your default browser at:
`http://localhost:8501` (or next available port).

*(Note: On the first run, the local SQLite database is automatically generated from `Datasets/util_12.csv` and indexed for sub-second query performance).*

---

## Demo Operator Credentials

Log in with any of the pre-configured accounts:

| Username | Password | Role | Operational Scope |
|---|---|---|---|
| `admin` | `admin123` | System Administrator | Full access across all 10 cities & all telemetry dimensions |
| `operator_mumbai` | `oper123` | Zone Operator | Field operations manager for municipal networks |
| `quality_analyst` | `qual123` | Water Quality Specialist | Potability, chlorine, turbidity, and chemical audit focus |
| `executive` | `exec123` | Chief Operations Officer | Executive city-level performance and macro benchmarks |

---

## Project Structure

```
UCC/
├── main.py                     # Primary router and application entry point
├── config.py                   # Central configurations, schema, cities, and roles
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions (.env, .db, chroma_db, caches)
├── Datasets/
│   └── util_12.csv             # Raw municipal water telemetry (163,904 rows, 51 cols)
├── database/
│   ├── data_loader.py          # CSV to SQLite auto-ingestion & indexing
│   └── db_manager.py           # SQLite connection and safe query executor
├── knowledge_base/documents/   # Domain Markdown knowledge base for RAG
│   ├── schema_metadata.md      # Documentation of all 51 telemetry attributes
│   ├── kpi_definitions.md      # 10 water utility KPIs and standard formulas
│   ├── water_quality_standards.md # IS 10500:2012, CPHEEO & WHO potability standards
│   └── regulatory_frameworks.md # AMRUT 2.0, National Water Policy, Smart Cities
├── rag/
│   └── rag_engine.py           # ChromaDB vector indexer and semantic retriever
├── llm/
│   ├── intent_parser.py        # Intent parser with strict domain guardrails
│   └── query_engine.py         # Secure SQL synthesizer & data provenance generator
├── response/
│   ├── response_generator.py   # Grounded response generator with refusal logic
│   └── chart_generator.py      # Minimal editorial Plotly chart generator
├── security/
│   ├── auth.py                 # User authentication & role mapping
│   └── security_gate.py        # Role-based column/row access gatekeeper
├── frontend/
│   ├── styles.py               # Google Fonts, variables (--accent), CSS overrides
│   ├── components.py           # Minimal editorial stats, rows, and provenance badges
│   ├── home_page.py            # 50/50 two-halves landing hero & capabilities list
│   ├── login_page.py           # Clean centered authorization modal
│   └── chat_page.py            # Two-column conversational intelligence command centre
└── prompts/
    ├── intent_prompt.txt       # Structured intent extraction instructions
    ├── sql_prompt.txt          # Safe SQLite query generation prompt
    └── system_prompt.txt       # System behavior rules & domain boundary constraints
```
