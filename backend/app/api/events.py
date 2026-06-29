"""Events (Chronicle) CRUD API"""

from __future__ import annotations



from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    tag: str | None = Query(None),
    entity_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event).order_by(Event.date, Event.date_order)
    if date_from:
        stmt = stmt.where(Event.date >= date_from)
    if date_to:
        stmt = stmt.where(Event.date <= date_to)
    if tag:
        stmt = stmt.where(Event.tags.any(tag))
    if entity_id:
        stmt = stmt.where(Event.entity_ids.any(entity_id))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(data: EventCreate, db: AsyncSession = Depends(get_db)):
    event = Event(**data.model_dump())
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, data: EventUpdate, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(event, key, val)
    await db.flush()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    await db.delete(event)
