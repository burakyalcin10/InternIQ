"""Listings Router — Staj Radar"""

import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Query

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "listings.json"


def load_listings():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/listings")
async def get_listings(
    search: Optional[str] = Query(None, description="Arama terimi"),
    type: Optional[str] = Query(None, description="İlan tipi: Remote, On-site, Hybrid"),
    limit: Optional[int] = Query(None, description="Maksimum sonuç sayısı"),
):
    """Staj ilanlarını listele, opsiyonel filtreleme ile."""
    listings = load_listings()

    # Search filter
    if search:
        q = search.lower()
        listings = [
            l for l in listings
            if q in l["position"].lower()
            or q in l["company"].lower()
            or any(q in tag.lower() for tag in l["tags"])
        ]

    # Type filter
    if type and type != "all":
        listings = [l for l in listings if l["type"] == type]

    # Limit
    if limit:
        listings = listings[:limit]

    return {"listings": listings, "total": len(listings)}


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: int):
    """Tek bir staj ilanı getir."""
    listings = load_listings()
    listing = next((l for l in listings if l["id"] == listing_id), None)
    if not listing:
        return {"error": "Listing not found"}, 404
    return listing
