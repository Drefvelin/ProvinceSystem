from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..scripts.bannergen.randombanner import generate_random_banner

banner_router = APIRouter()

@banner_router.get("/generator/banner")
async def generate_banner():
    return JSONResponse(content=generate_random_banner())