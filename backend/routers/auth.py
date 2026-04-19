"""Supabase-backed auth/profile routes for InternIQ."""

from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from routers.cv import extract_text_from_pdf
from services.profile_store import get_or_create_profile, serialize_profile, summarize_cv_profile, update_profile
from services.supabase_auth import require_authenticated_user

router = APIRouter()


def _serialize_user(user) -> dict:
    user_metadata = getattr(user, "user_metadata", {}) or {}
    return {
        "id": str(getattr(user, "id", "")),
        "name": user_metadata.get("full_name") or user_metadata.get("name") or "InternIQ Kullanıcısı",
        "email": getattr(user, "email", ""),
        "created_at": getattr(user, "created_at", ""),
    }


@router.get("/auth/me")
async def me(authorization: str | None = Header(default=None)):
    user = require_authenticated_user(authorization)
    profile = get_or_create_profile(str(user.id), user.email or "")
    return {
        "user": _serialize_user(user),
        "profile": serialize_profile(profile),
    }


@router.get("/profile/me")
async def profile_me(authorization: str | None = Header(default=None)):
    user = require_authenticated_user(authorization)
    profile = get_or_create_profile(str(user.id), user.email or "")
    return serialize_profile(profile)


@router.post("/profile/cv")
async def upload_profile_cv(
    authorization: str | None = Header(default=None),
    cv_file: UploadFile | None = File(default=None),
    cv_text: str = Form(default=""),
):
    user = require_authenticated_user(authorization)

    extracted_cv_text = cv_text.strip()
    filename = ""

    if cv_file and cv_file.filename:
        file_bytes = await cv_file.read()
        filename = cv_file.filename
        if cv_file.filename.lower().endswith(".pdf"):
            extracted_cv_text = extract_text_from_pdf(file_bytes)
        else:
            extracted_cv_text = file_bytes.decode("utf-8", errors="ignore")

    if not extracted_cv_text.strip():
        raise HTTPException(status_code=400, detail="Bir PDF yükleyin veya CV metni girin.")

    summary = summarize_cv_profile(extracted_cv_text)
    updated_profile = update_profile(
        str(user.id),
        user.email or "",
        {
            **summary,
            "cv_filename": filename,
            "cv_uploaded_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {
        "message": "CV profilinize kaydedildi.",
        "user": _serialize_user(user),
        "profile": serialize_profile(updated_profile),
    }
