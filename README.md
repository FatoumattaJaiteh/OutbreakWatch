# OutbreakWatch

> An extensible public health surveillance system for infectious disease outbreak monitoring, traveler health screening, epidemiological triage, and real-time community case reporting.

---

## 📌 Project Overview

OutbreakWatch enables public health agencies to:
1. **Declare and Monitor Outbreaks**: Administrators can register new outbreaks (e.g. *Ebola Virus Disease*, *Cholera*, *Mpox*), define disease severity, epicenter locations, and customize the clinical symptoms checklist.
2. **Public Case Reporting**: Individuals, family members, or field clinicians fill out responsive intake forms tailored to the specific outbreak.
3. **Automated Triage Scoring**: Incoming reports are scored automatically by the backend into `routine`, `urgent`, or `emergency` priority based on symptom severity and direct exposure history.
4. **Epidemiological Case Management**: Surveillance officers verify suspect cases, track status (`suspected` → `probable` → `confirmed` → `discarded`), and monitor outbreak metrics.

---

## 🗂️ Project Directory Structure

```text
OutbreakWatch/
├── .env.example                 # Environment variables template (Supabase, API port, keys)
├── .gitignore                   # Git ignore patterns for Python, logs, and environments
├── LICENSE                      # Project license
├── README.md                    # Project documentation & quickstart guide
│
├── backend/                     # Python Backend (FastAPI + Supabase)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/                 # API Routes & Versioning
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py    # Route aggregator
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── analytics.py  # Surveillance statistics & metric endpoints
│   │   │           ├── outbreaks.py  # Outbreak CRUD endpoints
│   │   │           └── reports.py    # Public case reporting & triage endpoints
│   │   ├── core/                # Core configurations & clients
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Settings & environment variables
│   │   │   └── supabase.py      # Supabase client factory (Anon & Service Role)
│   │   ├── schemas/             # Pydantic data models & request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── outbreak.py      # OutbreakCreate, OutbreakResponse, etc.
│   │   │   └── report.py        # CaseReportCreate, CaseReportResponse, etc.
│   │   └── services/            # Business logic & database integration
│   │       ├── __init__.py
│   │       ├── outbreak_service.py # Outbreak queries & fallbacks
│   │       └── report_service.py   # Report ingestion & triage priority scoring
│   ├── main.py                  # FastAPI application entrypoint & CORS middleware
│   └── requirements.txt         # Python dependencies (FastAPI, uvicorn, supabase, etc.)
│
├── database/                    # Database & Supabase Assets
│   ├── schema.sql               # Complete PostgreSQL / Supabase DDL schema with RLS & triggers
│   ├── migrations/              # Database migration scripts
│   │   └── 001_initial_schema.sql
│   └── seeds/                   # Seed data (sample Ebola & Cholera outbreaks, sample cases)
│       └── sample_data.sql
│
├── frontend/                    # Web Application (HTML, Tailwind CSS, JavaScript)
│   ├── index.html               # Public surveillance homepage & outbreaks directory
│   ├── report.html              # Public case intake & dynamic symptom questionnaire
│   ├── admin/                   # Administrative Surveillance Portal
│   │   ├── index.html           # Case management dashboard & triage review
│   │   └── outbreaks.html       # Outbreak creation & configuration console
│   └── assets/                  # Frontend static assets
│       ├── css/
│       │   └── style.css        # Custom styles & design enhancements
│       ├── js/
│       │   ├── api.js           # Centralized API fetch client
│       │   └── main.js          # Shared UI helpers, badges, and toasts
│       └── images/              # Icons, logos, and placeholders
│
└── docs/                        # Specifications, API reference, & architecture
    ├── API.md                   # Complete REST API endpoint reference
    └── ARCHITECTURE.md          # System architecture & data flow diagrams
```

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, Tailwind CSS, Modern JS | Clean, responsive UI with dynamic form generation. Compatible with Stitch MCP for UI design systems. |
| **Backend** | Python 3.12, FastAPI, Uvicorn | High-performance asynchronous API with Pydantic validation & automated Swagger docs. |
| **Database** | Supabase (PostgreSQL) | Managed relational database with Row Level Security (RLS) and real-time triggers. |
| **UI Design** | Stitch MCP | Design system and screen generator integration for rapid visual styling. |

---

## 🚀 Quickstart Guide

### 1. Environment Setup
Copy the `.env.example` file to create `.env`:
```bash
copy .env.example .env
```
Fill in your Supabase credentials once obtained:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

*(Note: The backend has built-in demo memory fallback so you can run and test immediately even before setting up Supabase).*

### 2. Run the Python Backend
In a terminal, navigate to `backend/` and install dependencies:
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# Install dependencies:
pip install -r requirements.txt
# Start the API server:
python main.py
```
The API server will run at: **`http://localhost:8000`**  
Interactive Swagger documentation is available at: **`http://localhost:8000/api/v1/docs`**

### 3. Run or View the Frontend
You can open `frontend/index.html` directly in your browser or run a simple local web server:
```bash
# Using Python:
python -m http.server 3000 --directory frontend

# Or using PHP:
php -S localhost:3000 -t frontend
```
Then visit:
- **Public Outbreak Portal**: `http://localhost:3000/index.html`
- **Case Intake Form**: `http://localhost:3000/report.html`
- **Admin Case Console**: `http://localhost:3000/admin/index.html`
- **Admin Outbreak Management**: `http://localhost:3000/admin/outbreaks.html`

### 4. Supabase Database Migration
When you have your Supabase project ready:
1. Open your **Supabase Dashboard** -> **SQL Editor**.
2. Run the SQL script found in [`database/schema.sql`](database/schema.sql).
3. (Optional) Run [`database/seeds/sample_data.sql`](database/seeds/sample_data.sql) to populate initial data.

---

## 📦 Next Steps
- Drop your documentation into the `docs/` folder.
- Share your Supabase keys to connect the live database.
- Utilize Stitch MCP to generate design variants or component screens as needed!
