from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.map_routes import router as map_router
from src.api.data_routes import router as data_router
from src.api.banner_routes import router as banner_router
from src.api.claim_routes import router as claim_router
from src.api.regen_routes import router as regen_router

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(map_router)
app.include_router(data_router)
app.include_router(banner_router)
app.include_router(claim_router)
app.include_router(regen_router)
