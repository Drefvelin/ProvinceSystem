from fastapi import APIRouter, Header

from .map_access import list_accessible_maps

maps_router = APIRouter(tags=["maps"])


@maps_router.get("/maps/accessible")
async def get_accessible_maps(
    authorization: str | None = Header(default=None),
):
    return {
        "maps": [
            entry.to_public_dict()
            for entry in list_accessible_maps(authorization)
        ]
    }
