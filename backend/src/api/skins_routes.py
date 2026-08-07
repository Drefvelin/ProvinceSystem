from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from src.skins.auth import (
    AuthError,
    HEADER_PLUGIN_KEY,
    HEADER_STAFF_KEY,
    require_plugin_key,
    require_staff_key,
)
from src.skins.codes import CodeError, get_session, issue_code, redeem_code
from src.skins.discord_link import LinkError, complete_link, start_link
from src.skins.naming import SlugError
from src.skins.notifications import (
    NotificationError,
    ack_notification,
    list_undelivered,
)
from src.skins.review_sheet import ReviewSheetError, build_review_sheet
from src.skins.storage import StorageError
from src.skins.submissions import (
    SlugConflictError,
    SubmissionError,
    approve_submission,
    create_submission,
    deny_submission,
    get_submission_for_owner,
    list_approved_pending_apply,
    list_pending,
    mark_applied,
    resolve_submission_file,
)

logger = logging.getLogger("skins.routes")

skins_router = APIRouter(prefix="/skins", tags=["skins"])


class IssueCodeBody(BaseModel):
    player_uuid: str = Field(..., min_length=1)


class RedeemBody(BaseModel):
    code: str = Field(..., min_length=1)


class DenyBody(BaseModel):
    reason: str = Field(..., min_length=1)


class AppliedBody(BaseModel):
    submission_ids: list[str]


class LinkStartBody(BaseModel):
    player_uuid: str = Field(..., min_length=1)
    minecraft_name: str | None = None


class LinkCompleteBody(BaseModel):
    code: str = Field(..., min_length=1)
    discord_user_id: str = Field(..., min_length=1)


def _session_from_auth(authorization: str | None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization Bearer token")
    token = authorization[7:].strip()
    row = get_session(token)
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return row


def _require_plugin(x_plugin_key: str | None) -> None:
    try:
        require_plugin_key(x_plugin_key)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


def _require_staff(x_staff_key: str | None) -> None:
    try:
        require_staff_key(x_staff_key)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@skins_router.post("/codes")
def post_codes(
    body: IssueCodeBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    try:
        return issue_code(body.player_uuid)
    except CodeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@skins_router.post("/discord/link/start")
def post_discord_link_start(
    body: LinkStartBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    try:
        return start_link(body.player_uuid, body.minecraft_name)
    except LinkError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@skins_router.post("/discord/link/complete")
def post_discord_link_complete(
    body: LinkCompleteBody,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        return complete_link(body.code, body.discord_user_id)
    except LinkError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@skins_router.post("/redeem")
def post_redeem(body: RedeemBody):
    try:
        return redeem_code(body.code)
    except CodeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@skins_router.post("/submissions")
async def post_submissions(
    authorization: str | None = Header(default=None),
    kind: str = Form(...),
    display_name: str = Form(...),
    slug: str | None = Form(default=None),
    grip_preset: str | None = Form(default=None),
    helmet: UploadFile | None = File(default=None),
    chestplate: UploadFile | None = File(default=None),
    leggings: UploadFile | None = File(default=None),
    boots: UploadFile | None = File(default=None),
    layer_1: UploadFile | None = File(default=None),
    layer_2: UploadFile | None = File(default=None),
    texture: UploadFile | None = File(default=None),
):
    session = _session_from_auth(authorization)

    uploads = {
        "helmet": helmet,
        "chestplate": chestplate,
        "leggings": leggings,
        "boots": boots,
        "layer_1": layer_1,
        "layer_2": layer_2,
        "texture": texture,
    }
    files_bytes: dict[str, bytes] = {}
    filenames: dict[str, str | None] = {}
    for name, upload in uploads.items():
        if upload is not None:
            files_bytes[name] = await upload.read()
            filenames[name] = upload.filename

    try:
        return create_submission(
            session,
            kind,
            display_name,
            files_bytes,
            grip_preset=grip_preset,
            slug=slug,
            filenames=filenames,
        )
    except SlugConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except (SlugError, StorageError, SubmissionError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@skins_router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: str,
    authorization: str | None = Header(default=None),
):
    session = _session_from_auth(authorization)
    row = get_submission_for_owner(submission_id, session["player_uuid"])
    if row is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return row


@skins_router.get("/submissions/{submission_id}/review-sheet")
def get_review_sheet(
    submission_id: str,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        data = build_review_sheet(submission_id)
    except ReviewSheetError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if data is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return Response(content=data, media_type="image/png")


@skins_router.post("/submissions/{submission_id}/approve")
def post_approve(
    submission_id: str,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        result = approve_submission(submission_id)
    except SubmissionError as e:
        status = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e)) from e
    logger.info("would notify discord submission=%s action=approve", submission_id)
    return result


@skins_router.post("/submissions/{submission_id}/deny")
def post_deny(
    submission_id: str,
    body: DenyBody,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        result = deny_submission(submission_id, body.reason)
    except SubmissionError as e:
        status = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e)) from e
    logger.info("would notify discord submission=%s action=deny", submission_id)
    return result


@skins_router.get("/staff/pending")
def staff_pending(
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    return {"submissions": list_pending()}


@skins_router.get("/staff/notifications")
def staff_notifications(
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    return {"notifications": list_undelivered()}


@skins_router.post("/staff/notifications/{notification_id}/ack")
def staff_notification_ack(
    notification_id: int,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    try:
        return ack_notification(notification_id)
    except NotificationError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@skins_router.get("/staff/submissions/{submission_id}/files/{filename}")
def staff_file(
    submission_id: str,
    filename: str,
    x_staff_key: str | None = Header(default=None, alias=HEADER_STAFF_KEY),
):
    _require_staff(x_staff_key)
    path = resolve_submission_file(submission_id, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    media = "image/png" if filename.lower().endswith(".png") else "application/octet-stream"
    return FileResponse(path, media_type=media, filename=filename)


@skins_router.get("/plugin/approved")
def plugin_approved(
    since: str | None = None,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    return {"submissions": list_approved_pending_apply(since)}


@skins_router.get("/plugin/submissions/{submission_id}/files/{filename}")
def plugin_file(
    submission_id: str,
    filename: str,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    path = resolve_submission_file(submission_id, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    media = "image/png" if filename.lower().endswith(".png") else "application/octet-stream"
    return FileResponse(path, media_type=media, filename=filename)


@skins_router.post("/plugin/applied")
def plugin_applied(
    body: AppliedBody,
    x_plugin_key: str | None = Header(default=None, alias=HEADER_PLUGIN_KEY),
):
    _require_plugin(x_plugin_key)
    applied = mark_applied(body.submission_ids)
    return {"applied": applied}
