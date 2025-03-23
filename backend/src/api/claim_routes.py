from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json

from src.scripts.util.imagechecker import get_province
from src.scripts.util.queue import enqueue
from src.scripts.util.auth import HASHED_KEY, NATION_JSON_PATH

router = APIRouter()

@router.post("/{hashed_key}/api/enqueue/{nation_rgb}")
async def enqueue(hashed_key: str, nation_rgb: str):
    # 1. Validate Hash
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 3. Load existing nation data
        if os.path.exists(NATION_JSON_PATH):
            with open(NATION_JSON_PATH, "r", encoding="utf-8") as f:
                nations = json.load(f)
        else:
            nations = {}
        # 5. Match or create nation entry by RGB
        found_nation_id = None
        for nation_id, data in nations.items():
            if data.get("rgb") == nation_rgb:
                found_nation_id = nation_id
                break

        if not found_nation_id:
            raise HTTPException(status_code=400, detail="No nation found with this rgb")

        # 8. Enqueue for regen
        enqueue("nation", nation_rgb)

        return JSONResponse(
            content={
                "success": True,
            }
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use x,z")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{hashed_key}/api/claim/{nation_rgb}/{coords}")
async def claim_province(hashed_key: str, nation_rgb: str, coords: str):
    # 1. Validate Hash
    if hashed_key != HASHED_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # 2. Parse coordinates
        x_str, z_str = coords.split(",")
        x, z = int(x_str), int(z_str)
        province_id = get_province(x, z)

        if province_id == 0:
            return JSONResponse(
                content={
                        "province_id": 0,
                    },
                status_code=404,
            )

        # 3. Load existing nation data
        if os.path.exists(NATION_JSON_PATH):
            with open(NATION_JSON_PATH, "r", encoding="utf-8") as f:
                nations = json.load(f)
        else:
            nations = {}

        # 4. Check if province is already claimed
        for nation_info in nations.values():
            if province_id in nation_info.get("provinces", []):
                return JSONResponse(
                    content={
                        "province_id": -1,
                    },
                    status_code=409,
                )

        # 5. Match or create nation entry by RGB
        found_nation_id = None
        for nation_id, data in nations.items():
            if data.get("rgb") == nation_rgb:
                found_nation_id = nation_id
                break

        if not found_nation_id:
            found_nation_id = f"NATION_{len(nations) + 1}"
            nations[found_nation_id] = {
                "rgb": nation_rgb,
                "provinces": []
            }

        # 6. Append province to nation
        nations[found_nation_id]["provinces"].append(province_id)

        # 7. Save changes
        with open(NATION_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(nations, f, indent=2)

        # 8. Enqueue for regen
        enqueue("nation", nation_rgb)

        return JSONResponse(
            content={
                "province_id": province_id,
            }
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use x,z")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
