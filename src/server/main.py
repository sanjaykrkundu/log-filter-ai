from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import os
import sys
import uuid
import shutil

# Setup paths and imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.analyzer.runtime_analyzer import RuntimeAnalyzer
from src.trainer.orchestrator import TrainerOrchestrator

TRAINED_DIR = os.path.join(PROJECT_ROOT, "trained")
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
INCOMING_DIR = os.path.join(PROJECT_ROOT, "incoming")

app = FastAPI(title="Log Filter AI Server")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class FetchRequest(BaseModel):
    type: str # 'issueId', 'username', or 'group'
    query: str

class AnalyzeRequest(BaseModel):
    issue_id: str

# Endpoints
@app.post("/api/issues/fetch")
async def fetch_issues(req: FetchRequest):
    # Simulate network delay for fetching from external bug tracker
    await asyncio.sleep(1.5)
    
    mock_data = [
        {"id": "ISSUE-8492", "title": "Camera Service Crash on Resume", "component": "Camera", "status": "Open"},
        {"id": "ISSUE-9103", "title": "NullPointerException in ISP Node 5", "component": "ISP", "status": "Investigating"}
    ]
    
    if req.type == 'issueId':
        return [mock_data[0]]
    else:
        return mock_data

@app.post("/api/issues/analyze")
async def analyze_issue(req: AnalyzeRequest):
    # Ensure workspace subdirectories exist
    os.makedirs(os.path.join(WORKSPACE_DIR, "extracted_logs"), exist_ok=True)
    
    # Determine the dumpstate path
    ds_path = os.path.join(INCOMING_DIR, f"{req.issue_id}.txt")
    if not os.path.exists(ds_path):
        # Fallback to test file for prototyping
        ds_path = os.path.join(INCOMING_DIR, "new_dumpstate.txt")
        
    if not os.path.exists(ds_path):
        return {"status": "error", "message": f"Dumpstate file not found for {req.issue_id}"}
        
    try:
        analyzer = RuntimeAnalyzer(trained_dir=TRAINED_DIR, workspace_dir=WORKSPACE_DIR)
        # Run heavy FAISS/LLM logic in threadpool to avoid blocking
        result = await run_in_threadpool(analyzer.analyze_dumpstate, ds_path)
        return {"status": "success", "message": f"Analysis complete for {req.issue_id}", "data": result}
    except Exception as e:
        return {"status": "error", "message": f"Analysis failed: {str(e)}"}

@app.post("/api/train")
async def train_ai(
    issue_id: str = Form("AUTO-GENERATE"),
    is_new_issue: bool = Form(False),
    title: Optional[str] = Form(None),
    component: Optional[str] = Form(None),
    snippet: str = Form(""),
    meaning: str = Form(""),
    files: List[UploadFile] = File(default=[])
):
    if issue_id == "AUTO-GENERATE" or not issue_id.strip():
        issue_id = f"ISSUE-{str(uuid.uuid4())[:8].upper()}"
        
    # Save uploaded files for archival
    if files and any(f.filename for f in files):
        raw_dir = os.path.join(PROJECT_ROOT, "training", "raw", issue_id)
        os.makedirs(raw_dir, exist_ok=True)
        for f in files:
            if f.filename:
                file_path = os.path.join(raw_dir, f.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)
                    
    try:
        orchestrator = TrainerOrchestrator(trained_dir=TRAINED_DIR)
        
        # Run heavy FAISS/LLM logic in threadpool
        result = await run_in_threadpool(
            orchestrator.train_issue,
            issue_id,
            title or "",
            component or "",
            snippet,
            meaning
        )
        
        return {"status": "success", "message": f"Successfully trained AI for {issue_id}!", "data": result}
    except Exception as e:
        return {"status": "error", "message": f"Training failed: {str(e)}"}
