from fastapi import FastAPI, Form, File, UploadFile, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import os
import sys
import uuid
import shutil
import json

# Setup paths and imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.analyzer.runtime_analyzer import RuntimeAnalyzer
from src.trainer.orchestrator import TrainerOrchestrator
from src.server.analytics import AnalyticsManager
from sqlalchemy.orm import Session
from src.server.database import get_db, init_db, User, Issue
from src.server.auth import verify_password, get_password_hash, create_access_token, get_current_admin

TRAINED_DIR = os.path.join(PROJECT_ROOT, "trained")
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
INCOMING_DIR = os.path.join(PROJECT_ROOT, "incoming")

app = FastAPI(title="Log Filter AI Server")

# Load central config
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "app_config.json")
with open(CONFIG_PATH, "r") as f:
    app_config = json.load(f)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
def on_startup():
    init_db()
    db = next(get_db())
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(username="admin", hashed_password=get_password_hash("admin123"))
        db.add(admin)
        
    if db.query(Issue).count() == 0:
        db.add(Issue(id="ISSUE-8492", title="Camera Service Crash on Resume", component="Camera", status="Open"))
        db.add(Issue(id="ISSUE-9103", title="NullPointerException in ISP Node 5", component="ISP", status="Investigating"))
        
    db.commit()

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config["backend"]["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class FetchRequest(BaseModel):
    type: str # 'issueId', 'username', or 'group'
    query: str
    page: int = 1
    limit: int = 50

class AnalyzeRequest(BaseModel):
    issue_id: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Endpoints
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/issues/fetch")
async def fetch_issues(req: FetchRequest, db: Session = Depends(get_db)):
    query_obj = db.query(Issue)
    if req.type == 'issueId' and req.query:
        query_obj = query_obj.filter(Issue.id.like(f"%{req.query}%"))
    elif req.type == 'group' and req.query:
        query_obj = query_obj.filter(Issue.component.like(f"%{req.query}%"))
        
    total_count = query_obj.count()
    issues = query_obj.offset((req.page - 1) * req.limit).limit(req.limit).all()
        
    return {
        "total": total_count,
        "page": req.page,
        "limit": req.limit,
        "issues": [{"id": i.id, "title": i.title, "component": i.component, "status": i.status} for i in issues]
    }

@app.post("/api/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        return {"status": "error", "message": "Invalid username or password"}
        
    access_token = create_access_token(data={"sub": user.username})
    return {"status": "success", "token": access_token}

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
        
        # Record live analytics
        analytics = AnalyticsManager(WORKSPACE_DIR)
        findings = result.get("findings", [])
        is_success = len(findings) > 0
        category = "Unknown Issue"
        if is_success:
            category = findings[0].get("analysis", {}).get("issue_name", "Unknown Issue")
        analytics.record_analysis(success=is_success, category_name=category)
        await manager.broadcast('{"type": "analytics_update"}')
        
        return {"status": "success", "message": f"Analysis complete for {req.issue_id}", "data": result}
    except Exception as e:
        return {"status": "error", "message": f"Analysis failed: {str(e)}"}

@app.get("/api/analytics")
async def get_analytics():
    analytics = AnalyticsManager(WORKSPACE_DIR)
    return analytics.get_stats()

@app.post("/api/train")
async def train_ai(
    issue_id: str = Form("AUTO-GENERATE"),
    is_new_issue: bool = Form(False),
    title: Optional[str] = Form(None),
    component: Optional[str] = Form(None),
    snippet: str = Form(""),
    meaning: str = Form(""),
    files: List[UploadFile] = File(default=[]),
    admin: User = Depends(get_current_admin)
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
        
        await manager.broadcast('{"type": "analytics_update"}')
        return {"status": "success", "message": f"Successfully trained AI for {issue_id}!", "data": result}
    except Exception as e:
        return {"status": "error", "message": f"Training failed: {str(e)}"}
