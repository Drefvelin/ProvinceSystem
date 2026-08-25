docker compose down --volumes --remove-orphans
docker compose build --no-cache
docker compose up -d --force-recreate

# uvicorn
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level warning