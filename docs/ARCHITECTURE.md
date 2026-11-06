# OutbreakWatch System Architecture

## 1. Overview
**OutbreakWatch** is an infectious disease surveillance and public case reporting system. It connects health authorities (who declare and manage outbreaks like Ebola, Cholera, or Mpox) with community members and healthcare workers (who submit suspect case reports).

```
   [Public / Clinicians]                     [Admin / Epidemiologists]
           |                                             |
   (Submit Case Report)                         (Declare Outbreak)
           |                                             |
           v                                             v
+-----------------------------------------------------------------+
|                       Frontend (HTML/CSS/JS)                   |
|   - index.html (Outbreaks Directory)                           |
|   - report.html (Dynamic Case Intake Form)                     |
|   - admin/index.html (Surveillance Case Triage)                |
|   - admin/outbreaks.html (Outbreak Declaration & Config)       |
+-----------------------------------------------------------------+
                                |
                   HTTP REST / JSON (FastAPI)
                                |
                                v
+-----------------------------------------------------------------+
|                    Python Backend (FastAPI)                    |
|   - Outbreak Management Service                                |
|   - Triage Engine (Priority Scoring: Emergency/Urgent/Routine) |
|   - Case Intake & Validation (Pydantic)                        |
+-----------------------------------------------------------------+
                                |
                   Supabase Client (PostgreSQL)
                                |
                                v
+-----------------------------------------------------------------+
|                       Supabase Platform                         |
|   - Table: public.outbreaks                                     |
|   - Table: public.case_reports                                  |
|   - Row-Level Security (RLS) Policies                           |
|   - Real-time Subscriptions & Automated Count Triggers          |
+-----------------------------------------------------------------+
```

## 2. Core Components

### Frontend (`frontend/`)
- Pure HTML5, modern CSS with Tailwind CSS utilities and responsive layouts.
- Dynamic questionnaire generation: selecting an outbreak dynamically renders that specific pathogen's symptom checklist.
- Client API layer (`assets/js/api.js`) handles all communication with backend routes.
- Ready for UI enrichment and styling using **Stitch MCP**.

### Backend (`backend/`)
- **FastAPI (Python 3.12)**: Asynchronous REST API with automatic OpenAPI documentation.
- **Pydantic**: Strict validation of outbreak definitions and incoming patient reports.
- **Triage Priority Calculation**: Automatic rule-based scoring (symptom severity, contact history, high-risk flags) classifies reports into `emergency`, `urgent`, or `routine`.
- **In-Memory Fallback**: Fully functional out of the box even before remote Supabase credentials are provided.

### Database (`database/` & Supabase)
- **PostgreSQL schema** with UUID keys, foreign key constraints, and check constraints.
- **Row-Level Security (RLS)**: Public write access for reports, public read access for active outbreaks, protected admin access for management.
- **Automated Trigger**: `update_outbreak_case_count()` keeps outbreak stats up to date as reports are received and verified.

## 3. Stitch MCP Integration
When you are ready to design new screens, generate visual variants, or create a design system:
1. Use `create_project` / `create_design_system` via Stitch MCP.
2. Generate screen layouts for mobile health surveillance workers or public portals.
3. Export generated screens or styles into `frontend/`.

