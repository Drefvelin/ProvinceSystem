from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
INPUTS_DIR = os.path.join(os.path.dirname(__file__), "src", "input")
MAPS_DIR = os.path.join(os.path.dirname(__file__), "src", "output", "maps")
DATA_DIR = os.path.join(os.path.dirname(__file__), "src", "defines")

@app.get("/map/{map_type}")
async def get_map(map_type: str):
    filename = f"{map_type}_map.png"
    file_path = os.path.join(MAPS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    return JSONResponse(content={"error": "Map not found"}, status_code=404)

@app.get("/map")
async def get_base_map():
    """Serve the base map image."""
    filename = "map.png"
    file_path = os.path.join(INPUTS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    return JSONResponse(content={"error": "Map not found"}, status_code=404)

@app.get("/data/{map_type}")
async def get_map(map_type: str):
    filename = f"{map_type}.json"
    file_path = os.path.join(DATA_DIR, filename)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)  # Load JSON content
        return JSONResponse(content=data)  # Return JSON directly

    return JSONResponse(content={"error": "Data not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
