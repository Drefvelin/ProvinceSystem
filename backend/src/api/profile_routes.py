"""Profile dashboard API (login session hub)."""

from __future__ import annotations

from fastapi import APIRouter, Header

from src.api.characters_routes import _profile_session_from_auth
from src.characters.creates import list_for_player
from src.characters.lore_items import list_player_custom_items
from src.skins.drinks import list_drink_submissions_for_player
from src.skins.submissions import list_submissions_for_player

profile_router = APIRouter(prefix="/profile", tags=["profile"])


@profile_router.get("")
@profile_router.get("/")
def get_profile_dashboard(
    authorization: str | None = Header(default=None),
):
    """Aggregated account view: characters, submissions, custom kit items."""
    session = _profile_session_from_auth(authorization)
    uuid = session["player_uuid"]
    realm = session.get("realm_id")
    roster = list_for_player(uuid, realm)
    return {
        **roster,
        "skins": list_submissions_for_player(uuid, realm),
        "drinks": list_drink_submissions_for_player(uuid, realm),
        "custom_items": list_player_custom_items(uuid, realm),
    }
