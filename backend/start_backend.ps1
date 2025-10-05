# Start Backend Services
# PostgreSQL and Redis are already running in Docker

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Creative Analysis Platform Backend" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL and Redis are running
Write-Host "Checking services..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}"

if ($containers -match "creative_analysis_db") {
    Write-Host "[OK] PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "[ERROR] PostgreSQL is not running" -ForegroundColor Red
    Write-Host "Run: docker compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

if ($containers -match "creative_analysis_redis") {
    Write-Host "[OK] Redis is running" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Redis is not running" -ForegroundColor Red
    Write-Host "Run: docker compose up -d redis" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting FastAPI backend on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
