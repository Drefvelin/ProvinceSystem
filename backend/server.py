from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Directory where maps are stored
INPUTS_DIR = os.path.join(os.path.dirname(__file__), "src", "input")
MAPS_DIR = os.path.join(os.path.dirname(__file__), "src", "output", "maps")

@app.get("/map/png/{map_type}")
async def get_map(map_type: str):
    """
    Serve the requested map image (county, duchy, kingdom).
    """
    filename = f"{map_type}_map.png"
    file_path = os.path.join(MAPS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"error": "Map not found"}
@app.get("/map")
async def get_base_map():
    """
    Serve the requested map image (county, duchy, kingdom).
    """
    filename = "map.png"
    file_path = os.path.join(INPUTS_DIR, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"error": "Map not found"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)