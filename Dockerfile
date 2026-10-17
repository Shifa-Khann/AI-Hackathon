FROM python:3.12-slim

# System libraries for WeasyPrint + curl for Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Node frontend dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy application sources
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Build Next.js frontend
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV BACKEND_URL=http://127.0.0.1:8001
RUN cd frontend && npm run build

# Make persistent data directory
RUN mkdir -p /app/backend/data /app/data

# Environment defaults
ENV MOCK_LLM=1 \
    DB_PATH=/app/backend/data/fold.db \
    CORS_ORIGINS=*

# Copy and setup startup script
COPY scripts/start-railway.sh /app/start-railway.sh
RUN chmod +x /app/start-railway.sh

EXPOSE 3000
CMD ["/app/start-railway.sh"]
