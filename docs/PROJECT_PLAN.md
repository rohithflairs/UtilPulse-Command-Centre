# UtilPulse Command Centre — Project Plan

## Overview
A Conversational Intelligence Platform for Water Utility Operations with:
- Dark, minimal, modern Streamlit UI
- Authorization/login system with role-based access
- Natural language Q&A powered by Gemini LLM + RAG
- Interactive charts, KPI dashboards, and data provenance

## Architecture

```
User → Home Screen → Login → Chat Interface
                                ├── Left Panel:  Question input + history
                                └── Right Panel: AI Response + Charts + Provenance
```

## Project Structure

```
UCC/
├── main.py                         # 🚀 Entry point — run from here
├── config.py                       # ⚙️ Central configuration
├── requirements.txt
├── .env                            # API keys (gitignored)
├── .gitignore
│
├── Datasets/
│   └── util_12.csv                 # Source dataset (163,904 rows)
│
├── database/                       # 💾 Data layer
│   ├── __init__.py
│   ├── data_loader.py              # CSV → SQLite loader
│   └── db_manager.py               # DB connection & query runner
│
├── knowledge_base/                 # 📚 Domain knowledge documents
│   ├── __init__.py
│   └── documents/
│       ├── schema_metadata.md      # Column definitions for LLM
│       ├── kpi_definitions.md      # KPI formulas & interpretation
│       ├── water_quality_standards.md  # IS 10500, WHO standards
│       └── regulatory_frameworks.md    # CPHEEO, BIS, Smart Cities
│
├── rag/                            # 🔍 Retrieval Augmented Generation
│   ├── __init__.py
│   └── rag_engine.py               # ChromaDB vector store + retrieval
│
├── llm/                            # 🧠 LLM Intelligence layer
│   ├── __init__.py
│   ├── intent_parser.py            # NL → structured intent JSON
│   └── query_engine.py             # Intent → SQL → execute → results
│
├── response/                       # 📝 Response formatting
│   ├── __init__.py
│   ├── response_generator.py       # LLM-powered answer generation
│   └── chart_generator.py          # Plotly chart creation
│
├── security/                       # 🔒 Auth & access control
│   ├── __init__.py
│   ├── auth.py                     # Login/user management
│   └── security_gate.py            # Role-based data filtering
│
├── kpi/                            # 📊 KPI calculations
│   ├── __init__.py
│   └── kpi_calculator.py           # Pre-built KPI queries
│
├── prompts/                        # 💬 LLM prompt templates
│   ├── system_prompt.txt
│   ├── intent_prompt.txt
│   └── sql_prompt.txt
│
├── frontend/                       # 🎨 UI layer (Streamlit)
│   ├── __init__.py
│   ├── styles.py                   # Dark theme CSS + styling
│   ├── home_page.py                # Landing/intro page
│   ├── login_page.py               # Authorization page
│   ├── chat_page.py                # Main chat interface
│   └── components.py               # Reusable UI components
│
└── docs/
    ├── PROJECT_PLAN.md             # This file
    └── BUILD_LOG.md                # Progress tracking log
```

## Build Steps (Ordered)

| Step | Module | Files | Status |
|------|--------|-------|--------|
| 1 | Setup | requirements.txt, .env, .gitignore, config.py | ⬜ TODO |
| 2 | Database | database/data_loader.py, database/db_manager.py | ⬜ TODO |
| 3 | Knowledge Base | knowledge_base/documents/*.md | ⬜ TODO |
| 4 | Prompts | prompts/*.txt | ⬜ TODO |
| 5 | RAG Engine | rag/rag_engine.py | ⬜ TODO |
| 6 | LLM Layer | llm/intent_parser.py, llm/query_engine.py | ⬜ TODO |
| 7 | Response | response/response_generator.py, response/chart_generator.py | ⬜ TODO |
| 8 | KPI | kpi/kpi_calculator.py | ⬜ TODO |
| 9 | Security | security/auth.py, security/security_gate.py | ⬜ TODO |
| 10 | Frontend | frontend/styles.py, home_page.py, login_page.py, chat_page.py, components.py | ⬜ TODO |
| 11 | Main | main.py | ⬜ TODO |
| 12 | Testing | End-to-end tests with 15+ questions | ⬜ TODO |

## User Flow

1. **Home Screen** → UtilPulse intro + "Start Chat" button
2. **Login Screen** → Username/password + role selection → Authorization
3. **Chat Screen** → Left panel (input + history) | Right panel (response + charts)
4. **Header** → Shows logged-in user name + designation/role tag

## Users (Pre-configured)

| Username | Password | Role | Access Level |
|----------|----------|------|-------------|
| admin | admin123 | Admin | Full access |
| operator_mumbai | oper123 | Zone Operator | Zone-level data |
| quality_analyst | qual123 | Quality Analyst | Water quality columns only |
| executive | exec123 | Executive | City-level aggregates only |

## Tech Stack

- **Frontend**: Streamlit (dark theme)
- **LLM**: Google Gemini 2.0 Flash
- **RAG**: ChromaDB + sentence-transformers
- **Database**: SQLite
- **Charts**: Plotly
- **Language**: Python 3.10+
