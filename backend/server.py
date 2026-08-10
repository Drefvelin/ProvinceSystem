import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --------------------
# Logging (warnings+)
# --------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s"
)
logger = logging.getLogger("startup")

app = FastAPI()

# --------------------
# Startup confirmation
# --------------------
@app.on_event("startup")
async def startup_log():
    from src.skins.db import migrate

    migrate()
    logger.warning("ProvinceSystem API started on http://0.0.0.0:8000")

# --------------------------------
# CORS MUST BE ADDED BEFORE ROUTERS
# --------------------------------
origins = [
    "https://www.tfminecraft.net",
    "https://tfminecraft.net",  # optional
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:13001",
    "http://127.0.0.1:13001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # required for images
)

@app.get("/ping")
def ping():
    return {"ok": True}

# --------------------
# Routers (AFTER CORS)
# --------------------
from src.api.map_routes import map_router
from src.api.data_routes import data_router
from src.api.banner_routes import banner_router
from src.api.claim_routes import claim_router
from src.api.regen_routes import regen_router
from src.api.file_routes import file_router
from src.api.skins_routes import skins_router
from src.api.characters_routes import characters_router

app.include_router(map_router)
app.include_router(data_router)
app.include_router(banner_router)
app.include_router(claim_router)
app.include_router(regen_router)
app.include_router(file_router)
app.include_router(skins_router)
app.include_router(characters_router)
