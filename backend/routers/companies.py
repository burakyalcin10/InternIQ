"""Companies Router — Company Intel"""

import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "companies.json"


def load_companies():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/companies")
async def get_companies():
    """Tüm şirket profillerini listele."""
    companies = load_companies()
    return {"companies": companies, "total": len(companies)}


@router.get("/companies/{company_id}")
async def get_company(company_id: int):
    """Tek bir şirket profili getir."""
    companies = load_companies()
    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return {"error": "Company not found"}, 404
    return company
