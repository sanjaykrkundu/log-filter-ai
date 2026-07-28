from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class TrainRequest(BaseModel):
    issue_id: str
    snippet: str
    meaning: str

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
async def train_ai(req: TrainRequest):
    # This is where we will hook into src.trainer.learning_engine or similar
    await asyncio.sleep(1)
    print(f"Received training data for {req.issue_id}:\nSnippet: {req.snippet}\nMeaning: {req.meaning}")
    return {"status": "success", "message": f"Successfully ingested training data for {req.issue_id}!"}
