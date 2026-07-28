from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio

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
    # This is where we will eventually hand off to src.analyzer.runtime_analyzer
    # Simulate analysis delay
    await asyncio.sleep(2)
    return {"status": "success", "message": f"Successfully triggered Log Filter AI analysis for {req.issue_id}!"}

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
    # This is where we will hook into src.trainer.learning_engine or similar
    await asyncio.sleep(1)
    
    file_names = [f.filename for f in files if f.filename]

    if is_new_issue:
        print(f"Defining NEW Issue:\nTitle: {title}\nComponent: {component}\nSnippet: {snippet}\nMeaning: {meaning}\nFiles: {file_names}")
        return {"status": "success", "message": f"Successfully created new issue type: {title} with {len(file_names)} files!"}
    else:
        print(f"Received training data for {issue_id}:\nSnippet: {snippet}\nMeaning: {meaning}\nFiles: {file_names}")
        return {"status": "success", "message": f"Successfully ingested training data for {issue_id} with {len(file_names)} files!"}
