<div align="center">

# Reed

**Your AI Study Assistant — chat with your own notes.**

Upload lecture notes, revision notes, or previous-year papers, then ask
questions and get answers grounded strictly in what you uploaded.

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API](#-api) · [Project Layout](#-project-layout) · [Roadmap](#-roadmap)

</div>

---

## Features

- PDF Ingestion — Upload notes tagged by **course**, **unit**, and **note type** (lecture / revision / PYQ).
- Smart Chunking — Parses PDFs with [Docling](https://github.com/DS4SD/docling) and chunks them with a `HybridChunker` that preserves document headings.
- Hybrid Retrieval — Dense (`all-MiniLM-L6-v2`) + sparse (`BM25`) embeddings stored in [Qdrant](https://qdrant.tech/) for high-quality semantic search.
- Local LLM — Uses [Ollama](https://ollama.com/) (`qwen3:8b` by default) so your notes never leave your machine.
- Grounded Answers — The model is instructed to answer **only** from the retrieved context, or say it couldn't find the answer.
- Minimal Dark UI — A single-page vanilla HTML/CSS/JS client.

---

## Architecture

```
+--------------+    HTTP     +------------------+
|  Frontend    | ----------->|  FastAPI Backend |
|  (HTML/JS)   |             |   /upload /query |
+--------------+             +--------+---------+
                                      |
                       +--------------+--------------+
                       |              |              |
                       v              v              v
                  +---------+   +----------+   +----------+
                  | Docling |   |  Qdrant  |   |  Ollama  |
                  | chunker |   |  hybrid  |   |  qwen3   |
                  +---------+   +----------+   +----------+
```

**Request flow for `/query`:**

1. User asks a question.
2. Backend queries Qdrant for the **top 5** most relevant chunks (hybrid dense + sparse).
3. Chunks are stitched into a context block and sent to the local LLM with a strict "answer only from context" prompt.
4. The answer is returned to the frontend.

---

## Quick Start

### 1. Prerequisites

| Service | Version (tested) | Notes |
| ------- | ---------------- | ----- |
| Python  | 3.10+            | Backend + vectorization |
| Qdrant  | 1.x              | Running on `localhost:6333` |
| Ollama  | latest           | With the `qwen3:8b` model pulled |

### 2. Start the infrastructure

```bash
# Qdrant (Docker is the easiest path)
docker run -p 6333:6333 qdrant/qdrant

# Ollama + model
ollama serve
ollama pull qwen3:8b
```

### 3. Configure environment

Create a `.env` file in the repo root:

```env
COLLECTION_NAME=reed_notes
```

### 4. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" python-dotenv \
            docling docling-core "qdrant-client[fastembed]" \
            ollama tqdm
```

> A `requirements.txt` is on the roadmap — for now, the line above is the authoritative list.

### 5. Run the backend

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### 6. Run the frontend

The frontend is a static page — open it directly or serve it:

```bash
# Option A: open the file
open frontend/index.html

# Option B: serve it
python -m http.server --directory frontend 5500
# then visit http://127.0.0.1:5500
```

> The current backend does not enable CORS. If you serve the frontend from a different origin than `127.0.0.1:8000`, install [`fastapi-cors`](https://fastapi.tiangolo.com/tutorial/cors/) or proxy requests through the FastAPI app.

---

## API

### `GET /`
Health check.

```json
{ "status": "working" }
```

### `POST /upload`
Upload one or more PDFs to be indexed.

**Form fields:**

| Field       | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| `course`    | string | e.g. `DBMS`, `Machine Learning`          |
| `unit`      | int    | Unit number (1, 2, 3, ...)               |
| `note_type` | string | `Lecture Notes`, `Revision Notes`, `PYQ` |
| `file`      | file   | One or more PDF files                    |

**Response:**

```json
{ "status": "success", "uploaded": 1 }
```

### `POST /query`
Ask a question against your uploaded notes.

**Body:**

```json
{ "question": "What is normalization in DBMS?" }
```

**Response:**

```json
{ "answer": "Normalization is the process of ..." }
```

If the answer isn't in your notes, you'll get back:

> _"I could not find that in the uploaded notes."_

---

## Project Layout

```
Reed/
├── backend/
│   ├── main.py              # FastAPI app + routes
│   ├── schemas.py           # Pydantic request models
│   ├── qdrant_Client.py     # Qdrant client (dense + sparse models)
│   └── vectorization.py     # Docling parsing, chunking, embedding
├── frontend/
│   ├── index.html           # Upload + chat UI
│   ├── index.css            # Dark theme styling
│   └── index.js             # Form submit + chat wiring
├── skills/
│   └── chat.py              # Retrieval + Ollama prompt + answer
├── data/                    # Sample unit PDFs (gitignored)
├── .env                     # Your local config (not committed)
└── README.md
```

---

## Configuration

All config is driven by environment variables loaded via `python-dotenv`.

| Variable          | Default    | Purpose                                  |
| ----------------- | ---------- | ---------------------------------------- |
| `COLLECTION_NAME` | _required_ | Qdrant collection to read from / write to |

Embedding models (hard-coded in `backend/qdrant_Client.py`):

| Type   | Model                                       |
| ------ | ------------------------------------------- |
| Dense  | `sentence-transformers/all-MiniLM-L6-v2`    |
| Sparse | `Qdrant/bm25`                               |
| LLM    | `qwen3:8b` (Ollama)                         |

---

## Smoke Test

With Qdrant + Ollama running and `uvicorn` started:

```bash
# 1. Upload a PDF
curl -F course=DBMS -F unit=1 -F note_type="Lecture Notes" \
     -F file=@data/Unit\ 1.pdf \
     http://127.0.0.1:8000/upload

# 2. Ask a question
curl -X POST http://127.0.0.1:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "Summarize Unit 1"}'
```

---

## Roadmap

- [ ] Add `requirements.txt` and a `pyproject.toml`.
- [ ] Enable CORS so the static frontend can call the API cleanly.
- [ ] On-upload embedding only for **new** files (current code re-embeds the full list on every upload).
- [ ] Streaming answers via Server-Sent Events.
- [ ] Source citations (link answers back to the chunk's `heading` and `source` metadata).
- [ ] Multi-PDF upload UX (drag-and-drop, progress).
- [ ] Switchable LLM / embedding model via env vars.
- [ ] Docker Compose for Qdrant + Ollama + backend.

---

## Contributing

1. Fork and create a feature branch.
2. Keep changes focused; favour small PRs.
3. Run the smoke test above before opening a PR.
4. Note that `data/` is gitignored — add a tiny sample PDF under `tests/fixtures/` if you need one.

---

## License

No license has been declared yet. If you're the maintainer, drop a `LICENSE` file (MIT is a sensible default for a student project like this) and link it here.