#!/bin/sh
set -e

# Run backend on internal port 8001
echo "Starting backend on 127.0.0.1:8001..."
cd /app
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
for i in $(seq 1 30); do
  if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/api/topics')" >/dev/null 2>&1; then
    echo "Backend is ready!"
    break
  fi
  sleep 1
done

# Start Next.js frontend on public PORT provided by Railway
echo "Starting frontend on port ${PORT:-3000}..."
cd /app/frontend
exec npm start
