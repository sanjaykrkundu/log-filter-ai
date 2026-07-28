Write-Host "Starting Log Filter AI Portal..." -ForegroundColor Green

# Start Python FastAPI Backend in a new window
Write-Host "Starting Python Backend (FastAPI)..."
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; uvicorn src.server.main:app --reload`""

# Start React Frontend in a new window
Write-Host "Starting React Frontend (Vite)..."
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot\web-app'; npm run dev`""

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host "The Python API will be available at: http://localhost:8000"
Write-Host "The Web App will be available at: http://localhost:5173" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Cyan
