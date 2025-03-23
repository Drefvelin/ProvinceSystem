import hashlib
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from src.scripts.bannergen.randombanner import generate_random_banner

from src.scripts.util.imagechecker import get_province  # Adjust if your path is different
from src.scripts.util.queue import enqueue  # Your queue utility
from src.scripts.mapgen.regiongen import generate_regions
from src.scripts.mapgen.mapgen import create_map
from src.scripts.compile.nation_compiler import process_nations
from fastapi import BackgroundTasks

app = FastAPI()

SECRET_KEY = "i_love_tfmc"
HASHED_KEY = hashlib.md5(SECRET_KEY.encode()).hexdigest()

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
NATION_JSON_PATH = os.path.join(os.path.dirname(__file__), "src", "input", "nation.json")
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

@app.post("/data/upload/nation")
async def upload_nation_data(request: Request):
    try:
        data = await request.json()  # Parse incoming JSON
        target_path = os.path.join(INPUTS_DIR, "nation.json")

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return JSONResponse(content={"message": "Nation data saved successfully."}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/generator/banner")
async def generate_banner():
    return JSONResponse(content=generate_random_banner())

@app.get("/{hashed_key}/api/regenerate/{mode}/{regen_type}")
async def regenerate_map(
    hashed_key: str,
    mode: str,
    regen_type: str,
    background_tasks: BackgroundTasks
):
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Queue the heavy work
    def background_job():
        if mode.lower() == "nation":
            process_nations()

        queued = regen_type.lower() != "fullregen"
        create_map(mode, mode+"_map", True)
        generate_regions(mode, borders=True, frontend_save=True, queued_regen=queued)

    background_tasks.add_task(background_job)

    return JSONResponse(content={
        "success": True,
        "mode": mode,
        "regen_type": regen_type,
        "message": "Regeneration started in background."
    })

@app.get("/{hashed_key}/api/claim/{nation_rgb}/{coords}")
async def claim_province(hashed_key: str, nation_rgb: str, coords: str):
    # 1. Validate Hash
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 2. Parse coords and nation_rgb
        x_str, z_str = coords.split(",")
        x, z = int(x_str), int(z_str)
        province_id = get_province(x, z)

        if province_id == 0:
            return JSONResponse(content={"success": False, "message": "No province found at coordinates."}, status_code=404)

        # 3. Load existing nations
        if os.path.exists(NATION_JSON_PATH):
            with open(NATION_JSON_PATH, "r", encoding="utf-8") as f:
                nations = json.load(f)
        else:
            nations = {}

        # 4. Check if province is already claimed
        for nation_info in nations.values():
            if province_id in nation_info.get("provinces", []):
                return JSONResponse(content={
                    "success": False,
                    "province_id": province_id,
                    "message": "Province already claimed."
                }, status_code=409)

        # 5. Find or create nation by RGB
        found_nation_id = None
        for nation_id, data in nations.items():
            if data.get("rgb") == nation_rgb:
                found_nation_id = nation_id
                break

        if not found_nation_id:
            found_nation_id = f"NATION_{len(nations)+1}"
            nations[found_nation_id] = {
                "rgb": nation_rgb,
                "provinces": []
            }

        # 6. Add province to the nation
        nations[found_nation_id]["provinces"].append(province_id)

        # 7. Save updated nation file
        with open(NATION_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(nations, f, indent=2)

        # 8. Enqueue for regeneration
        enqueue("nation", nation_rgb)

        return JSONResponse(content={
            "success": True,
            "province_id": province_id,
            "nation_id": found_nation_id,
            "nation_rgb": nation_rgb,
            "message": f"Province {province_id} claimed by {found_nation_id} and added to queue."
        })

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use x,z")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
