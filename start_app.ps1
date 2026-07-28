param (
    [switch]$Debug
)

Write-Host "Starting Log Filter AI Portal..." -ForegroundColor Green

if ($Debug) {
    Write-Host "Running in DEBUG mode" -ForegroundColor Yellow
    $env:LOG_LEVEL = "DEBUG"
    $uvicornArgs = "--reload --log-level debug"
} else {
    $env:LOG_LEVEL = "INFO"
    $uvicornArgs = "--reload"
}

# Start Python FastAPI Backend in a new window
Write-Host "Starting Python Backend (FastAPI)..."
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; `$env:LOG_LEVEL='$env:LOG_LEVEL'; uvicorn src.server.main:app $uvicornArgs`""

# Start React Frontend in a new window
Write-Host "Starting React Frontend (Vite)..."
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot\web-app'; npm run dev`""

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host "The Python API will be available at: http://localhost:8000"
Write-Host "The Web App will be available at: http://localhost:5173" -ForegroundColor Yellow
if ($Debug) {
    Write-Host "DEBUG mode is ACTIVE. Detailed logs will appear in the backend window." -ForegroundColor Yellow
}
Write-Host "=================================================" -ForegroundColor Cyan
