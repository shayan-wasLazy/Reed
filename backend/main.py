from fastapi import UploadFile, File, Form
from fastapi import FastAPI
from backend.schemas import QueryRequest
from backend.vectorization import initialize
from skills.chat import ask_rag
from skills.createFF import createWorkspace, CreateFolder, getWorkspace
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware






# @app.on_event("startup")
# def startup():

#     initialize()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    createWorkspace()
    yield
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "working"
    }
    
    
@app.post("/query")
def query(req: QueryRequest):

    answer = ask_rag(req.question)

    return {
        "answer": answer
    }
    
from pathlib import Path
from fastapi import UploadFile, File, Form

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/workspace")
def workspace():
    return getWorkspace()



from pathlib import Path
from fastapi import HTTPException

WORKSPACE = Path("Workspace")


@app.get("/file")
def get_file(path: str):

    file_path = (
        WORKSPACE / path
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return {
        "content":
        file_path.read_text(
            encoding="utf-8"
        )
    }

@app.post("/upload")
async def test_upload(
    course: str = Form(...),
    unit: int = Form(...),
    note_type: str = Form(...),
    file: UploadFile = File(...)
):
    uploaded_files = []
    
        
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    uploaded_files.append({
            "path": file_path,
            "course": course,
            "unit": unit,
            "note_type": note_type
        })
    
        
    
    initialize(uploaded_files)
    
    return {
        "status": "success",
        "uploaded": len(uploaded_files)
    }
    