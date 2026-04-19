"""JSON-backed profile storage keyed by Supabase user id."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import json
import re


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "profiles.json"
LOCK = Lock()

COMMON_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "next.js",
    "fastapi",
    "spring boot",
    "langchain",
    "pinecone",
    "sql",
    "postgresql",
    "mongodb",
    "docker",
    "redis",
    "git",
    "rest api",
    "machine learning",
    "tensorflow",
    "pytorch",
    "linux",
    "aws",
    "azure",
    "figma",
    "arduino",
    "raspberry pi",
    "prisma",
    "jwt",
    "whisper",
    "demucs",
    "ffmpeg",
    "trpc",
    "vercel blob",
]

SECTION_HEADERS = [
    "SUMMARY",
    "PROFESSIONAL EXPERIENCE",
    "EXPERIENCE",
    "PROJECTS",
    "EDUCATION",
    "SKILLS",
    "ORGANISATIONS",
    "CERTIFICATES & ACHIEVEMENTS",
]

ICON_ARTIFACTS = (
    "/envel",
    "/whatsapp",
    "/linkedin",
    "/github",
    "/gl",
    "/phone",
    "/mail",
)

BULLET_PREFIXES = ("•", "-", "*", "·")

REPLACEMENTS = {
    "Â·": "•",
    "â€¢": "•",
    "·": "•",
    "Â¸": "ş",
    "Â¨": "ü",
    "Ëœ": "ğ",
    "Ä±": "ı",
    "Ä°": "İ",
    "Ã¼": "ü",
    "Ãœ": "Ü",
    "Ã¶": "ö",
    "Ã–": "Ö",
    "Ã§": "ç",
    "Ã‡": "Ç",
    "ÄŸ": "ğ",
    "Äž": "Ğ",
    "ÅŸ": "ş",
    "Åž": "Ş",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "Io T": "IoT",
    "Postgre SQL": "PostgreSQL",
    "Pineconevector": "Pinecone vector",
    "Saa S": "SaaS",
    "t RPC": "tRPC",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text(json.dumps({"profiles": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_store() -> dict:
    _ensure_store()
    with LOCK:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _save_store(store: dict) -> None:
    with LOCK:
        DATA_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def _repair_mojibake(text: str) -> str:
    candidate = text
    try:
        repaired = text.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
        if repaired.count("Ã") + repaired.count("Â") < candidate.count("Ã") + candidate.count("Â"):
            candidate = repaired
    except Exception:
        pass
    return candidate


def _normalize_bullet(line: str) -> str:
    stripped = line.strip()
    for prefix in BULLET_PREFIXES:
        if stripped.startswith(prefix):
            return "• " + stripped[len(prefix):].strip()
    return stripped


def clean_extracted_cv_text(cv_text: str) -> str:
    text = (cv_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return ""

    text = _repair_mojibake(text)
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    text = re.sub(r"([a-zçğıöşü])([A-ZÇĞİÖŞÜ])", r"\1 \2", text)
    text = re.sub(r"([A-Za-zÇĞİÖŞÜçğıöşü])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([A-Za-zÇĞİÖŞÜçğıöşü])", r"\1 \2", text)
    connector_patterns = [
        (r"(?<=[A-Za-z])and(?=[A-Z])", " and "),
        (r"(?<=[A-Za-z])with(?=[A-Z])", " with "),
        (r"(?<=[A-Za-z])for(?=[A-Z])", " for "),
        (r"(?<=[A-Za-z])via(?=[A-Z])", " via "),
        (r"(?<=[A-Za-z])using(?=[A-Z])", " using "),
        (r"(?<=[A-Za-z])into(?=[A-Z])", " into "),
        (r"(?<=[A-Za-z])from(?=[A-Z])", " from "),
        (r"(?<=[A-Za-z])to(?=[A-Z])", " to "),
        (r"(?<=[A-Za-z])of(?=[A-Z])", " of "),
        (r"(?<=[A-Za-z])in(?=[A-Z])", " in "),
    ]
    for pattern, replacement in connector_patterns:
        text = re.sub(pattern, replacement, text)
    post_fixes = {
        "Io T": "IoT",
        "B 2 B": "B2B",
        "B 2 C": "B2C",
        "Saa S": "SaaS",
        "Postgre SQL": "PostgreSQL",
        "t RPC": "tRPC",
    }
    for old, new in post_fixes.items():
        text = text.replace(old, new)

    text = re.sub(r"(?<=[A-Za-z0-9])and(?=\s+[A-Z])", " and", text)
    text = re.sub(r"(?<=[A-Za-z0-9])with(?=\s+[A-Z])", " with", text)
    text = re.sub(r"(?<=[A-Za-z0-9])for(?=\s+[A-Za-z])", " for", text)
    text = re.sub(r"(?<=[A-Za-z0-9])using(?=\s+[A-Z])", " using", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    cleaned_lines = []
    for raw_line in text.splitlines():
        line = _normalize_bullet(raw_line)
        if not line:
            continue

        if any(line.lower().startswith(prefix) for prefix in ICON_ARTIFACTS):
            continue

        line = re.sub(r"/[a-zA-Z0-9_-]+", " ", line)
        line = re.sub(r"\s{2,}", " ", line).strip(" |")
        line = _normalize_bullet(line)
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def _extract_section(lines: list[str], section_name: str) -> list[str]:
    try:
        start_index = lines.index(section_name)
    except ValueError:
        return []

    section_lines = []
    for line in lines[start_index + 1:]:
        if line in SECTION_HEADERS:
            break
        section_lines.append(line)
    return section_lines


def _extract_summary(lines: list[str]) -> str:
    summary_lines = _extract_section(lines, "SUMMARY")
    if summary_lines:
        return " ".join(summary_lines[:3]).strip()[:320]

    sentence_lines = [line for line in lines[:8] if len(line) > 20]
    return " ".join(sentence_lines[:2]).strip()[:320]


def _extract_education(lines: list[str]) -> str:
    education_lines = _extract_section(lines, "EDUCATION")
    if education_lines:
        return " ".join(education_lines[:2]).strip()[:160]

    for line in lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in ["üniversite", "university", "lisans", "yüksek lisans", "bachelor", "master"]):
            return line[:160]
    return ""


def _project_skills(project_text: str) -> list[str]:
    lowered = project_text.lower()
    return [skill for skill in COMMON_SKILLS if skill in lowered][:5]


def _looks_like_project_title(line: str) -> bool:
    normalized = line.strip()
    if not normalized:
        return False

    if normalized.startswith(BULLET_PREFIXES):
        return False

    if normalized.endswith("."):
        return False

    if len(normalized) < 5 or len(normalized) > 100:
        return False

    words = normalized.split()
    if len(words) > 10:
        return False

    action_starters = (
        "built ",
        "developed ",
        "implemented ",
        "integrated ",
        "optimized ",
        "created ",
        "led ",
        "designed ",
        "drove ",
        "transformed ",
        "minimized ",
    )
    if normalized.lower().startswith(action_starters):
        return False

    return True


def _extract_projects(lines: list[str]) -> list[dict]:
    project_lines = _extract_section(lines, "PROJECTS")
    if not project_lines:
        return []

    projects = []
    current_title = ""
    current_points: list[str] = []

    def flush_project() -> None:
        nonlocal current_title, current_points
        if not current_title:
            return

        description = " ".join(current_points[:2]).strip()
        project_text = " ".join([current_title, *current_points]).strip()
        projects.append(
            {
                "title": current_title[:120],
                "description": description[:240],
                "skills": _project_skills(project_text),
            }
        )
        current_title = ""
        current_points = []

    for line in project_lines:
        normalized = line.strip()
        if not normalized:
            continue

        is_bullet = normalized.startswith(BULLET_PREFIXES)
        content = re.sub(r"^[•\-\*·]\s*", "", normalized).strip()

        if _looks_like_project_title(content):
            flush_project()
            current_title = content
            continue

        if is_bullet and current_title and content:
            current_points.append(content)

    flush_project()
    return projects[:6]


def summarize_cv_profile(cv_text: str) -> dict:
    clean_text = clean_extracted_cv_text(cv_text)
    text_lower = clean_text.lower()
    matched_skills = [skill for skill in COMMON_SKILLS if skill in text_lower][:10]
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

    summary = _extract_summary(lines) or "CV yüklendi. Profil özetiniz hazır."
    education_line = _extract_education(lines)
    projects = _extract_projects(lines)

    if any(keyword in text_lower for keyword in ["senior", "lead", "5 yıl", "6 yıl", "7 yıl"]):
        experience_level = "Deneyimli"
    elif any(keyword in text_lower for keyword in ["intern", "staj", "junior", "öğrenci", "student", "3rd year", "junior / 3rd year"]):
        experience_level = "Erken kariyer"
    else:
        experience_level = "Gelişmekte olan profil"

    return {
        "summary": summary[:320],
        "skills": matched_skills,
        "education_summary": education_line[:160],
        "experience_level": experience_level,
        "projects": projects,
        "cv_text": clean_text,
    }


def _empty_profile(user_id: str, email: str) -> dict:
    return {
        "user_id": user_id,
        "email": email,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "cv_filename": "",
        "cv_uploaded_at": None,
        "summary": "",
        "skills": [],
        "education_summary": "",
        "experience_level": "",
        "projects": [],
        "cv_text": "",
    }


def serialize_profile(profile: dict | None) -> dict:
    data = profile or {}
    cv_text = data.get("cv_text", "")
    return {
        "has_cv": bool(cv_text.strip()),
        "cv_filename": data.get("cv_filename", ""),
        "cv_uploaded_at": data.get("cv_uploaded_at"),
        "summary": data.get("summary", ""),
        "skills": data.get("skills", []),
        "education_summary": data.get("education_summary", ""),
        "experience_level": data.get("experience_level", ""),
        "projects": data.get("projects", []),
        "cv_text": cv_text,
    }


def get_or_create_profile(user_id: str, email: str) -> dict:
    store = _load_store()
    for profile in store["profiles"]:
        if profile["user_id"] == user_id:
            if email and profile.get("email") != email:
                profile["email"] = email
                profile["updated_at"] = _now_iso()
                _save_store(store)
            profile.setdefault("projects", [])
            return profile

    profile = _empty_profile(user_id, email)
    store["profiles"].append(profile)
    _save_store(store)
    return profile


def get_profile(user_id: str) -> dict | None:
    store = _load_store()
    for profile in store["profiles"]:
        if profile["user_id"] == user_id:
            profile.setdefault("projects", [])
            return profile
    return None


def update_profile(user_id: str, email: str, profile_update: dict) -> dict:
    store = _load_store()
    for profile in store["profiles"]:
        if profile["user_id"] != user_id:
            continue

        profile.update(profile_update)
        profile.setdefault("projects", [])
        profile["email"] = email or profile.get("email", "")
        profile["updated_at"] = _now_iso()
        _save_store(store)
        return profile

    profile = _empty_profile(user_id, email)
    profile.update(profile_update)
    profile["updated_at"] = _now_iso()
    store["profiles"].append(profile)
    _save_store(store)
    return profile
