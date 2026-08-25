# VeriJust

**AI forensics for project integrity.** VeriJust ingests audio and video evidence, transcribes it, and runs credibility analysis across the transcript — flagging hesitation markers, logical inconsistencies, manipulative phrasing, and sentiment shifts — then compiles the findings into a forensic report tied to a verifiable chain of custody.

<p>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white">
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-16-black?logo=next.js">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="AWS Bedrock" src="https://img.shields.io/badge/AWS-Bedrock%20Nova-FF9900?logo=amazonaws&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
</p>

> **Status: early development.** The core pipeline is in place, but several services are still being wired up. See [Roadmap](#roadmap) before deploying anywhere near real casework.

---

## Table of contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [API overview](#api-overview)
- [Development](#development)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What it does

| Capability | Description |
|---|---|
| **Evidence intake** | Upload audio/video files. Every file is hashed (SHA-256) and stored in encrypted S3 with a presigned-URL access model. |
| **Signal integrity checks** | Waveform-level inspection for signs of splicing, re-encoding, or other tampering before any semantic analysis runs. |
| **Credibility analysis** | Amazon Nova (via Bedrock) reviews the transcript for bluffing, hesitation, inconsistency, and manipulative phrasing, returning a per-segment confidence score. |
| **Tone & sentiment** | AWS Comprehend classifies sentiment and emotional tone per transcript segment. |
| **Speaker-aware transcripts** | Diarized segments with timestamps, speaker labels, sentiment, and bluff-confidence stored alongside `pgvector` embeddings for semantic search. |
| **Case management** | Group evidence under cases with client name, internal case number, and status. |
| **Chain of custody** | Every action against a piece of evidence is recorded with actor and timestamp — the audit trail that makes findings defensible. |
| **Async processing** | Long-running analysis runs on Celery workers so uploads return immediately with a task ID to poll. |
| **Guest access** | Short-lived demo tokens with reduced upload limits, so the product can be trialled without an account. |

---

## Architecture

```
                    ┌──────────────────────┐
                    │   Next.js frontend   │
                    │      (port 3000)     │
                    └───────────┬──────────┘
                                │  JWT (verijust_token cookie)
                                ▼
                    ┌──────────────────────┐         ┌──────────────┐
                    │   FastAPI backend    │────────▶│  PostgreSQL  │
                    │      (port 8000)     │         │  + pgvector  │
                    └───────────┬──────────┘         └──────────────┘
                                │  enqueue
                                ▼
                    ┌──────────────────────┐
                    │   Redis (broker)     │
                    └───────────┬──────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │    Celery worker     │
                    └───────────┬──────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
    ┌──────────┐         ┌─────────────┐       ┌────────────┐
    │  AWS S3  │         │   Bedrock   │       │ Comprehend │
    │ evidence │         │ Nova (LLM)  │       │   (tone)   │
    └──────────┘         └─────────────┘       └────────────┘
```

**Analysis pipeline** (`app/tasks.py::process_audio_pipeline`):

1. Generate a presigned S3 URL for the uploaded evidence.
2. Run signal-integrity forensics to detect forgery/tampering.
3. Send the transcript to Amazon Nova for credibility analysis.
4. Compile the forensic report.
5. Notify the user by email.

Failed tasks retry up to three times with a 60-second backoff.

---

## Tech stack

**Backend** — FastAPI · SQLAlchemy 2.0 (async) · Alembic · Celery · Redis · PostgreSQL with pgvector · boto3 · python-jose (JWT) · passlib · slowapi (rate limiting) · librosa + mutagen (audio processing) · fastapi-mail

**Frontend** — Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · Supabase JS · lucide-react

**Infrastructure** — Docker Compose · AWS S3, Bedrock (Nova Pro), Comprehend

---

## Project structure

```
verijust/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, startup migrations
│   │   ├── tasks.py             # Celery task definitions
│   │   ├── core/                # config, auth middleware, AWS clients, logging
│   │   ├── db/                  # SQLAlchemy models & session
│   │   ├── routers/             # auth, forensics, users, storage, reporting
│   │   ├── services/            # aws_nova, forensic_service, storage, email
│   │   └── processing/          # tone_analyzer
│   ├── alembic/                 # migrations
│   ├── scripts/                 # start.sh, start-prod.sh, migrate.py
│   ├── API_DOCUMENTATION.md
│   ├── AUTHENTICATION_GUIDE.md
│   └── POSTMAN_TESTING_GUIDE.md
├── frontend/
│   ├── app/                     # App Router pages (/, /login, /analyze)
│   ├── components/
│   │   ├── forensics/           # ForensicView, Waveform, Transcript
│   │   ├── contextual/          # ContextView
│   │   ├── layout/              # Sidebar, TopNav
│   │   └── ui/                  # FileCard, MetricRow
│   ├── utils/supabase/          # client/server/middleware helpers
│   └── middleware.ts            # route protection
├── docker-compose.yml
└── scripts/start.sh
```

---

## Getting started

### Prerequisites

- Docker and Docker Compose
- A PostgreSQL instance with the `pgvector` extension enabled
- An AWS account with access to S3, Bedrock (Amazon Nova), and Comprehend

> The `db` service in `docker-compose.yml` is currently commented out, so `DATABASE_URL` must point at a Postgres instance you provide. Uncomment that block if you'd rather run Postgres locally — just remember to add the `pgvector` extension, since `TranscriptSegment.embedding` depends on it.

### 1. Clone and configure

```bash
git clone https://github.com/muhridlo24/verijust.git
cd verijust
cp backend/.env.example backend/.env   # create this file if it doesn't exist yet
```

Fill in `backend/.env` — see [Configuration](#configuration) for the full list. At minimum you need `SECRET_KEY`, `DATABASE_URL`, and your AWS credentials.

Generate a secret key with:

```bash
openssl rand -hex 32
```

### 2. Run everything

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Migrations run automatically on backend startup via the migration helper, so there's no separate migrate step in development.

### Running without Docker

<details>
<summary>Backend</summary>

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start the worker (Redis must be running):

```bash
celery -A app.core.celery_app.celery_app worker --loglevel=info
```
</details>

<details>
<summary>Frontend</summary>

```bash
cd frontend
npm install
npm run dev
```
</details>

---

## Configuration

All backend settings live in `backend/.env` and are loaded through `pydantic-settings`.

| Variable | Required | Default | Notes |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | JWT signing key |
| `DATABASE_URL` | ✅ | — | e.g. `postgresql+asyncpg://user:pass@host/db` |
| `ALGORITHM` | | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | `30` | Token lifetime |
| `AWS_ACCESS_KEY_ID` | | — | Omit if using an IAM role |
| `AWS_SECRET_ACCESS_KEY` | | — | Omit if using an IAM role |
| `AWS_REGION` | | `us-east-1` | |
| `S3_BUCKET_NAME` | | `verijust-uploads` | Created and hardened on startup |
| `S3_PRESIGNED_URL_EXPIRATION` | | `3600` | Seconds |
| `UPLOAD_MAX_SIZE_MB` | | `200` | Registered users |
| `GUEST_UPLOAD_MAX_SIZE_MB` | | `5` | Guest tokens |
| `BEDROCK_MODEL_ID` | | `amazon.nova-pro-v1:0` | Verify the ID in your AWS console |
| `CELERY_BROKER_URL` | | `redis://redis:6379/0` | |
| `CELERY_RESULT_BACKEND` | | `redis://redis:6379/0` | |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | | — | SMTP credentials |
| `MAIL_FROM` | | `noreply@verijust.ai` | |
| `MAIL_SERVER` / `MAIL_PORT` | | `smtp.gmail.com` / `587` | |

The frontend reads `NEXT_PUBLIC_API_URL` (set to `http://localhost:8000` by Compose).

---

## API overview

Protected routes expect `Authorization: Bearer <token>`. Full request/response examples live in [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md).

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/guest` | Issue a short-lived guest token |

### Forensics

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/forensics/upload` | Upload evidence and kick off analysis |
| `GET` | `/forensics/evidence` | List evidence (paginated) |
| `GET` | `/forensics/evidence/{id}` | Evidence detail |
| `GET` | `/forensics/analysis/{evidence_id}` | Analysis results |
| `GET` | `/forensics/transcript/{evidence_id}` | Diarized transcript segments |
| `GET` | `/forensics/task-status/{task_id}` | Poll a running analysis |
| `DELETE` | `/forensics/evidence/{id}` | Remove evidence |

### Cases & users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/profile` | Current user profile |
| `GET` | `/users/cases` | List cases |
| `POST` | `/users/cases` | Create a case |
| `GET` | `/users/cases/{id}` | Case detail |

Additional guides: [`AUTHENTICATION_GUIDE.md`](backend/AUTHENTICATION_GUIDE.md) and [`POSTMAN_TESTING_GUIDE.md`](backend/POSTMAN_TESTING_GUIDE.md).

---

## Development

**Creating a migration**

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

**Linting the frontend**

```bash
cd frontend
npm run lint
```

**Hot reload** works in both containers — the backend runs Uvicorn with `--reload` and the frontend uses `WATCHPACK_POLLING` so file changes propagate into the container.

---

## Roadmap

- [ ] Full email delivery on analysis completion (currently a placeholder in the Celery task)
- [ ] Speech-to-text integration so `analyze_transcript` receives real transcript text rather than a file URL
- [ ] Reconcile authentication: the backend issues its own JWTs while the frontend also ships Supabase helpers
- [ ] Restore a first-class Postgres service in Compose with `pgvector` preinstalled
- [ ] Test suite and CI
- [ ] Exportable PDF forensic reports
- [ ] Replace the deprecated `@app.on_event("startup")` hook with a lifespan handler

---

## Contributing

Issues and pull requests are welcome. For anything substantial, please open an issue first so we can discuss the approach.

1. Fork the repo and create a branch off `main`
2. Make your change
3. Open a pull request describing what changed and why

---

## Disclaimer

VeriJust produces **investigative signals, not verdicts.** Credibility scoring from speech analysis is probabilistic and can be affected by accent, recording quality, stress, neurodivergence, and cultural communication norms. Output should support human judgment in a review process, never replace it, and should not be treated as admissible proof of deception on its own.

---

## License

No license has been specified yet. Until one is added, all rights are reserved by the repository owner — see [choosealicense.com](https://choosealicense.com/) if you'd like to pick one.
