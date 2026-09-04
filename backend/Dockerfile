FROM python:3.10-slim

WORKDIR /app

# Node 20+ for staff review-sheet 3D renderer (backend/render/cli.mjs + Playwright).
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Build context must be ProvinceSystem root so shared/ pack constants are available.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
# constants.py resolves ProvinceSystem/shared via parents[4] → /shared/...
COPY shared /shared

WORKDIR /app/render
RUN npm ci \
    && npx playwright install chromium \
    && npx playwright install-deps chromium

WORKDIR /app

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
