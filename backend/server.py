from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
INPUTS_DIR = os.path.join(os.path.dirname(__file__), "src", "input")
MAPS_DIR = os.path.join(os.path.dirname(__file__), "src", "output", "maps")

@app.get("/map/png/{map_type}")
async def get_map(map_type: str):
    """Serve the requested map image (county, duchy, kingdom)."""
    filename = f"{map_type}_map.png"
    file_path = os.path.join(MAPS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png", headers={"Access-Control-Allow-Origin": "*"})  # ✅ Add CORS headers

    return JSONResponse(content={"error": "Map not found"}, status_code=404)

@app.get("/map")
async def get_base_map():
    """Serve the base map image."""
    filename = "map.png"
    file_path = os.path.join(INPUTS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png", headers={"Access-Control-Allow-Origin": "*"})  # ✅ Add CORS headers

    return JSONResponse(content={"error": "Map not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
