from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import TrackingEvent
from mysite.database.schema import TrackingEventInputSchema, TrackingEventOutSchema
from mysite.database.db import SessionLocal

tracking_event_router = APIRouter(prefix='/tracking-event', tags=['Tracking Event'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tracking_event_router.post('/', response_model=TrackingEventOutSchema)
async def create_event(event: TrackingEventInputSchema, db: Session = Depends(get_db)):
    event_db = TrackingEvent(**event.dict())
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db


@tracking_event_router.get('/', response_model=List[TrackingEventOutSchema])
async def list_events(db: Session = Depends(get_db)):
    return db.query(TrackingEvent).all()


@tracking_event_router.get('/{event_id}', response_model=TrackingEventOutSchema)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event_db = db.query(TrackingEvent).filter(TrackingEvent.id == event_id).first()
    if not event_db:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event_db


@tracking_event_router.put('/{event_id}', response_model=TrackingEventOutSchema)
async def update_event(event_id: int, event: TrackingEventInputSchema, db: Session = Depends(get_db)):
    event_db = db.query(TrackingEvent).filter(TrackingEvent.id == event_id).first()
    if not event_db:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    for key, value in event.dict().items():
        setattr(event_db, key, value)

    db.commit()
    db.refresh(event_db)
    return event_db


@tracking_event_router.delete('/{event_id}', response_model=dict)
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    event_db = db.query(TrackingEvent).filter(TrackingEvent.id == event_id).first()
    if not event_db:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    db.delete(event_db)
    db.commit()
    return {'message': 'Событие удалено'}