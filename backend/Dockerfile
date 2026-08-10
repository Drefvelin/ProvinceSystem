FROM python:3.10-slim

WORKDIR /app

# Build context must be ProvinceSystem root so shared/ pack constants are available.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
# constants.py resolves ProvinceSystem/shared via parents[4] → /shared/...
COPY shared /shared

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
