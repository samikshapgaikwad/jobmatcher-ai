# JobMatch AI 🤖

> An intelligent, agentic job matching platform powered by LangGraph, RAG, and Groq LLM — built to showcase end-to-end AI engineering across scraping, embedding, matching, and generative AI.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-blue?style=for-the-badge)](https://jobmatcher-ai.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Supabase](https://img.shields.io/badge/Supabase-pgvector-green?style=flat-square&logo=supabase)](https://supabase.com)

---

## 🎯 What This Project Does

JobMatch AI scrapes real job listings from multiple sources, embeds them using sentence transformers, and uses a **LangGraph agentic pipeline** to intelligently match candidates to jobs based on their resume.

When a user uploads their resume:
1. The system extracts and vectorizes their skills, experience, and education
2. A **LangGraph agent** performs multi-vector RAG retrieval from 400+ real job listings
3. A Groq LLM scores each job match (0-100) with detailed reasoning
4. The agent self-evaluates confidence and **retries with broader search** if needed
5. Users get ranked matches with gap analysis, cover letter generation, and contextual AI chat

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         SUPABASE                                │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │   jobs table         │  │   resumes table                  │ │
│  │   + 5 vector columns │  │   + 5 vector columns             │ │
│  │   (pgvector 384-dim) │  │   (pgvector 384-dim)             │ │
│  └──────────────────────┘  └──────────────────────────────────┘ │
│  pg_cron: cleanup at 1AM daily                                  │
└────────────────────┬────────────────────┬───────────────────────┘
                     │                    │
        ┌────────────┴──┐      ┌──────────┴──────────┐
        │  Embedding    │      │    Matching API      │
        │  Service      │      │    (LangGraph)       │
        │  Render:8001  │      │    Render:8000       │
        │               │      │                      │
        │ • Resume parse│      │ • Vector retrieval   │
        │ • Vectorize   │      │ • LLM reranking      │
        │ • Job embed   │      │ • Gap analysis       │
        │ • Scheduler   │      │ • Cover letters      │
        └───────────────┘      │ • AI chat            │
                               └──────────────────────┘
                                          │
                               ┌──────────┴──────────┐
                               │     Frontend         │
                               │     React + Vite     │
                               │     Render           │
                               └─────────────────────┘
```

---

## 🧠 The LangGraph Agent — Core Innovation

The heart of this project is a **stateful multi-node agent** built with LangGraph. Unlike simple vector search, this agent self-evaluates its results and retries with broader queries when confidence is low.
```
[START]
   │
   ▼
[retrieve_jobs] ──── pgvector cosine similarity
   │                 3 vectors: skills + experience + full_resume
   │                 Union-deduplicated results
   ▼
[rerank_jobs] ────── Single Groq LLM call scores ALL jobs at once
   │                 Returns: match_score, skills_pct, exp_pct,
   │                 strengths, weaknesses, missing_skills
   │                 Calculates average confidence score
   ▼
[route_after_rerank] ── Conditional edge
   │
   ├── confidence < 0.5 AND retries < 2
   │       │
   │       ▼
   │   [increment_retry] ── top_k += 10
   │       │
   │       └──────────────────► back to [retrieve_jobs]
   │
   └── confidence OK
           │
           ▼
       [analyze_gaps] ── Merges scored data with raw job data
           │              Sorts by match_score descending
           │              Returns top 10
           ▼
       [format_output]
           │
           ▼
        [END]
```

**Why this matters:** The conditional retry loop is what makes this an *agent* rather than a pipeline. It demonstrates understanding of agentic patterns — self-evaluation, dynamic replanning, and confidence-based routing.

---

## ✨ Features

### Core AI Features
- **Agentic RAG Matching** — LangGraph agent with conditional retry routing
- **Multi-Vector Retrieval** — 3 resume embeddings queried against pgvector simultaneously
- **LLM Reranking** — Groq Llama-3.3-70b scores and explains every match
- **Gap Analysis** — Identifies specific missing skills per job
- **Cover Letter Generation** — Personalized per job using candidate profile
- **Contextual AI Chat** — Ask anything about a specific job match

### Data Pipeline
- **4 Job Sources** — Indeed, Naukri (Playwright), Unstop API, Adzuna API
- **Auto Deduplication** — SHA256 hash-based upsert prevents duplicates
- **Auto Cleanup** — pg_cron deletes expired jobs daily at 1AM
- **Auto Embedding** — APScheduler embeds new jobs every 5 minutes

### Frontend
- **Google OAuth** — Supabase Auth with Google provider
- **Real-time Processing** — Animated resume upload with step-by-step status
- **Match Score Rings** — SVG-based animated score visualization
- **AI Insights Panel** — Slide-in panel with full job analysis
- **Save Jobs** — Persistent saved jobs via localStorage
- **Applied Jobs** — Automatically hidden after applying, toggle to show
- **Resume Persistence** — Upload state persists across navigation

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent** | LangGraph | Stateful multi-node agent with conditional routing |
| **LLM** | Groq Llama-3.3-70b | Job scoring, gap analysis, cover letters, chat |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | 384-dim vectors |
| **Vector DB** | Supabase pgvector | Cosine similarity search |
| **NLP** | spaCy en_core_web_sm | Resume entity extraction |
| **Scraping** | Playwright + Requests | Multi-source job ingestion |
| **Backend** | FastAPI + Python 3.11 | REST API layer |
| **Frontend** | React + TypeScript + Vite | UI |
| **Styling** | Tailwind CSS + shadcn/ui | Component library |
| **Auth** | Supabase Auth + Google OAuth | Authentication |
| **Database** | Supabase (PostgreSQL) | Data + vectors |
| **Scheduling** | APScheduler + pg_cron | Automated pipelines |
| **Deployment** | Render (Docker) + Vercel | Production hosting |

---

## 📁 Project Structure
```
jobmatcher-ai/
├── embedding_service/          # ML service — resume parsing + vectorization
│   ├── resume_pipeline/
│   │   ├── resume_parser.py    # spaCy NER + regex extraction
│   │   ├── text_extraction.py  # PyMuPDF + python-docx
│   │   └── skill_extractor.py  # 70+ tech keyword matching
│   ├── models/
│   │   └── embedding_model.py  # sentence-transformers singleton
│   ├── services/
│   │   ├── job_embedding_service.py
│   │   ├── resume_embedding_service.py
│   │   └── scheduler.py        # APScheduler every 5 min
│   ├── db/
│   │   ├── job_repository.py
│   │   └── resume_repository.py
│   └── main.py                 # FastAPI + upload endpoint
│
├── matching_api/               # Agentic matching service
│   ├── graph/
│   │   ├── state.py            # LangGraph AgentState TypedDict
│   │   ├── nodes.py            # retrieve → rerank → analyze → output
│   │   ├── edges.py            # Conditional routing logic
│   │   └── agent.py            # Compiled LangGraph graph
│   ├── services/
│   │   └── retriever.py        # pgvector multi-vector RPC
│   ├── routers/
│   │   ├── match.py            # POST /api/match
│   │   ├── explain.py          # POST /api/explain/{job_id}
│   │   ├── cover_letter.py     # POST /api/cover-letter/{job_id}
│   │   └── chat.py             # POST /api/chat/{job_id}
│   └── main.py                 # FastAPI app
│
├── scraper_service/            # Job ingestion pipeline
│   ├── scrapers/
│   │   ├── scrape_indeed.py    # Playwright browser automation
│   │   ├── scrape_naukri.py    # Playwright + pagination
│   │   └── scrape_unstop.py    # REST API scraper
│   ├── data_pipeline/
│   │   ├── fetch_jobs.py       # Adzuna REST API
│   │   └── db_utils.py         # Supabase upsert + cleanup
│   ├── scheduler.py            # Daily pipeline at 2AM
│   └── main.py                 # FastAPI + manual trigger
│
└── frontend_app/               # React TypeScript frontend
    └── src/
        ├── components/
        │   ├── AIInsightsPanel.tsx
        │   ├── JobCard.tsx
        │   ├── JobChat.tsx
        │   ├── MatchScoreRing.tsx
        │   └── ResumeCommandCenter.tsx
        ├── context/
        │   └── AuthContext.tsx
        ├── hooks/
        │   ├── use-matching.ts
        │   ├── useAppliedJobs.ts
        │   └── useSavedJobs.ts
        └── pages/
            ├── Index.tsx
            ├── Profile.tsx
            ├── SavedJobs.tsx
            └── Settings.tsx
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- Groq API key (free at console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/samikshapgaikwad/jobmatcher-ai.git
cd jobmatcher-ai
```

### 2. Set up Supabase
Run this SQL in your Supabase SQL editor to enable pgvector and create the match function:
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE OR REPLACE FUNCTION match_jobs(
  query_embedding vector(384),
  match_count int DEFAULT 20,
  match_threshold float DEFAULT 0.3
)
RETURNS TABLE (
  id bigint, title text, company text,
  location text, description text,
  link text, source text, similarity float
)
LANGUAGE sql STABLE AS $$
  SELECT id, title, company, location, description, link, source,
    1 - (description_embedding <=> query_embedding) AS similarity
  FROM jobs
  WHERE description_embedding IS NOT NULL
    AND 1 - (description_embedding <=> query_embedding) > match_threshold
  ORDER BY description_embedding <=> query_embedding
  LIMIT match_count;
$$;
```

### 3. Start the Embedding Service
```bash
cd embedding_service
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Create .env
cp .env.example .env
# Add: SUPABASE_URL, SUPABASE_SERVICE_KEY

uvicorn main:app --port 8001 --reload
```

### 4. Start the Matching API
```bash
cd matching_api
python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

# Create .env
cp .env.example .env
# Add: SUPABASE_URL, SUPABASE_SERVICE_KEY, GROQ_API_KEY

uvicorn main:app --port 8000 --reload
```

### 5. Start the Frontend
```bash
cd frontend_app
npm install

# Create .env
cp .env.example .env
# Add: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY,
#      VITE_API_URL=http://localhost:8000/api,
#      VITE_EMBEDDING_URL=http://localhost:8001

npm run dev
```

### 6. Seed initial jobs
```bash
cd scraper_service
.\venv\Scripts\activate
pip install -r requirements.txt
python scheduler.py --now
```

---

## 🌐 Production Deployment

All services are containerized with Docker and deployed on Render:

| Service | URL | Runtime |
|---------|-----|---------|
| Frontend | https://jobmatcher-ai.onrender.com | Static |
| Matching API | https://matching-api-hfsa.onrender.com | Docker |
| Embedding Service | https://embedding-service-2r2z.onrender.com | Docker |

### Automated Production Pipeline
```
1:00 AM → Supabase pg_cron deletes expired + empty jobs
2:00 AM → Scraper fetches fresh jobs (Unstop + Adzuna)
Every 5min → Embedding service embeds new jobs automatically
On demand → Matching API serves LangGraph agent requests
```

---

## 🔑 Environment Variables

### embedding_service/.env
```env
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
EMBEDDING_MODEL=all-MiniLM-L6-v2
BATCH_INTERVAL_MINUTES=5
PIPELINE_RUN_TIME=02:00
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
CORS_ORIGINS=*
```

### matching_api/.env
```env
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
GROQ_API_KEY=
CORS_ORIGINS=*
RETRIEVAL_TOP_K=20
CONFIDENCE_THRESHOLD=0.5
MAX_RETRIES=2
```

### frontend_app/.env
```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=
VITE_EMBEDDING_URL=
```

---

## 💡 Key Engineering Decisions

**Why LangGraph over a simple pipeline?**
The conditional retry loop demonstrates agentic behavior — the system self-evaluates confidence and dynamically broadens its search. This is the difference between a pipeline and an agent.

**Why multi-vector retrieval?**
Querying with 3 separate resume embeddings (skills, experience, full_resume) gives significantly better recall than single-vector search. Each embedding captures different semantic aspects of the candidate.

**Why pgvector over Pinecone/Weaviate?**
Keeping vectors in Supabase eliminates a separate service, reduces latency, and simplifies the architecture. For this scale (400+ jobs, <1000 users) pgvector performs identically to dedicated vector databases.

**Why CPU-only torch?**
The free tier provides 512MB RAM. Full torch requires ~800MB. CPU-only torch brings this to ~350MB — fits comfortably in free tier without sacrificing embedding quality.

**Why shared database pattern?**
Services communicate through Supabase rather than direct HTTP calls. This eliminates tight coupling — each service can be updated, restarted, or scaled independently.

---

## 📊 Database Schema

### jobs table
| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| title | text | Job title |
| company | text | Company name |
| location | text | Job location |
| description | text | Full job description |
| link | text | Application URL |
| source | text | Scraper source |
| hash | text | SHA256 dedup key |
| closing_date | date | Auto-cleanup trigger |
| description_embedding | vector(384) | Cosine similarity search |
| title_embedding | vector(384) | Title matching |
| requirements_embedding | vector(384) | Requirements matching |
| responsibilities_embedding | vector(384) | Role matching |
| qualifications_embedding | vector(384) | Qualification matching |

### resumes table
| Column | Type | Description |
|--------|------|-------------|
| user_id | uuid | Supabase auth user |
| name | text | Extracted via spaCy NER |
| email | text | Extracted via regex |
| skills_text | text | Parsed skills section |
| experience_text | text | Parsed experience section |
| skills_embedding | vector(384) | Skills vector |
| experience_embedding | vector(384) | Experience vector |
| full_resume_embedding | vector(384) | Full resume vector |

---

## 🎤 Interview Talking Points

**"Walk me through the LangGraph agent"**
> The agent has 5 nodes connected by edges. After reranking, a conditional edge checks the average confidence score across all matched jobs. If confidence is below 0.5 and we haven't exceeded 2 retries, it routes back to the retrieve node with a larger top_k. This self-evaluation loop is what makes it an agent rather than a pipeline.

**"Why pgvector over a dedicated vector database?"**
> For this scale, pgvector in Supabase eliminates an extra service dependency, reduces network hops, and keeps the architecture simple. The cosine similarity performance is comparable to Pinecone at under 100k vectors.

**"How does multi-vector retrieval work?"**
> I query pgvector three times — once each with the skills embedding, experience embedding, and full resume embedding. Results are union-deduplicated by job ID. This gives better recall because a job might score low on skills similarity but high on experience similarity.

**"How did you handle the 512MB RAM constraint?"**
> The main culprit was PyTorch — full version requires ~800MB. I switched to CPU-only torch which brings RAM usage to ~350MB. The embedding quality is identical since we're running inference not training.

---

## 👩‍💻 Author

**Samiksha Gaikwad**
- GitHub: [@samikshapgaikwad](https://github.com/samikshapgaikwad)
- Email: samikshapgaikwad2005@gmail.com

---

## 📄 License

MIT License — feel free to use this project as a reference or starting point.
