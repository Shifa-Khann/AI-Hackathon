# start-dev.ps1 - Launch The Fold backend + frontend for local development
# Usage: Right-click then Run with PowerShell  (or: powershell -File .\start-dev.ps1)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "=== The Fold - Dev Server ===" -ForegroundColor Cyan
Write-Host ""

# Kill any stale processes on the ports
foreach ($port in @(8000, 3000)) {
    $procs = netstat -ano | Select-String ":$port "
    foreach ($line in $procs) {
        $pid = ($line.ToString().Trim() -split '\s+')[-1]
        if ($pid -match '^\d+$' -and $pid -ne '0') {
            try { Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}
Start-Sleep -Seconds 1

# Start Backend (uvicorn) in a new window
Write-Host "Starting backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

# Wait for backend to be ready
Write-Host "Waiting for backend..." -NoNewline
$maxWait = 20
$waited = 0
while ($waited -lt $maxWait) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 2 -ErrorAction Stop | Out-Null
        break
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -in @(401, 403, 404, 422)) { break }
    }
    Start-Sleep -Seconds 1
    $waited++
    Write-Host "." -NoNewline
}
Write-Host " Ready!" -ForegroundColor Green

# Start Frontend (Next.js) in a new window
Write-Host "Starting frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Both servers are starting. Open http://localhost:3000 in your browser." -ForegroundColor Cyan
Write-Host "Close the two new terminal windows to stop the servers."
Write-Host ""
