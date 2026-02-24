from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class LyricVerse(BaseModel):
    label: str
    text: str


class Hymn(BaseModel):
    ID: int
    Number: int
    Title: str
    Author: Optional[str] = None
    Key: str = ""
    Stanzas: int = 0
    Category: int
    CategoryName: str = ""
    Lyrics: List[LyricVerse] = []
    Active: int = 1
    CrossReference: Optional[str] = None


class HymnSummary(BaseModel):
    ID: int
    Number: int
    Title: str
    Author: Optional[str] = None
    Key: str = ""
    Stanzas: int = 0
    Category: int
    CategoryName: str = ""
    Active: int = 1
    CrossReference: Optional[str] = None


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[HymnSummary]


# ---------------------------------------------------------------------------
# Data store (populated at startup)
# ---------------------------------------------------------------------------

hymns_db: List[Hymn] = []
hymns_by_id: dict = {}

DEAD_FIELDS = {"AssignTo", "Category_Description_10ADAA54", "Description", "Cross_reference"}

DATA_PATH = Path(__file__).parent / "hymnal_export.json"


def _load_hymns() -> None:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for entry in raw:
        for key in DEAD_FIELDS:
            entry.pop(key, None)
        hymn = Hymn(**entry)
        hymns_db.append(hymn)
        hymns_by_id[hymn.ID] = hymn


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_hymns()
    yield


app = FastAPI(title="Hymnal API", lifespan=lifespan)


def _to_summary(hymn: Hymn) -> HymnSummary:
    return HymnSummary(**hymn.dict(exclude={"Lyrics"}))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/hymns", response_model=PaginatedResponse)
def list_hymns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[int] = None,
    number: Optional[int] = None,
    active: Optional[int] = None,
):
    filtered = hymns_db
    if category is not None:
        filtered = [h for h in filtered if h.Category == category]
    if number is not None:
        filtered = [h for h in filtered if h.Number == number]
    if active is not None:
        filtered = [h for h in filtered if h.Active == active]

    total = len(filtered)
    items = [_to_summary(h) for h in filtered[skip : skip + limit]]
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)


@app.get("/hymns/search", response_model=PaginatedResponse)
def search_hymns(
    q: str = Query(..., min_length=1),
    category: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    query = q.lower()
    results: List[Hymn] = []
    for h in hymns_db:
        if category is not None and h.Category != category:
            continue
        if query in h.Title.lower():
            results.append(h)
            continue
        if any(query in v.text.lower() for v in h.Lyrics):
            results.append(h)

    total = len(results)
    items = [_to_summary(h) for h in results[skip : skip + limit]]
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)


@app.get("/hymns/by-number/{number}", response_model=List[Hymn])
def get_hymns_by_number(number: int):
    matches = [h for h in hymns_db if h.Number == number]
    if not matches:
        raise HTTPException(status_code=404, detail=f"No hymns with number {number}")
    return matches


@app.get("/hymns/{hymn_id}", response_model=Hymn)
def get_hymn(hymn_id: int):
    hymn = hymns_by_id.get(hymn_id)
    if hymn is None:
        raise HTTPException(status_code=404, detail=f"Hymn {hymn_id} not found")
    return hymn
