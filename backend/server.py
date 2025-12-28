from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --------------------------------
# CORS MUST BE ADDED BEFORE ROUTERS
# --------------------------------

origins = [
    "https://www.tfminecraft.net",
    "https://tfminecraft.net",  # optional
    "http://localhost:3000"
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

# Now import routers
from src.api.map_routes import map_router
from src.api.data_routes import data_router
from src.api.banner_routes import banner_router
from src.api.claim_routes import claim_router
from src.api.regen_routes import regen_router
from src.api.file_routes import file_router

# And include them AFTER CORS
app.include_router(map_router)
app.include_router(data_router)
app.include_router(banner_router)
app.include_router(claim_router)
app.include_router(regen_router)
app.include_router(file_router)
