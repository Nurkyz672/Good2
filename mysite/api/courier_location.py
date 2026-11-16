from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import CourierLocation
from mysite.database.schema import CourierLocationInputSchema, CourierLocationOutSchema
from mysite.database.db import SessionLocal

courier_location_router = APIRouter(prefix='/courier-location', tags=['Courier Location'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@courier_location_router.post('/', response_model=CourierLocationOutSchema)
async def create_location(location: CourierLocationInputSchema, db: Session = Depends(get_db)):
    location_db = CourierLocation(**location.dict())
    db.add(location_db)
    db.commit()
    db.refresh(location_db)
    return location_db


@courier_location_router.get('/', response_model=List[CourierLocationOutSchema])
async def list_locations(db: Session = Depends(get_db)):
    return db.query(CourierLocation).all()


@courier_location_router.get('/{location_id}', response_model=CourierLocationOutSchema)
async def get_location(location_id: int, db: Session = Depends(get_db)):
    location_db = db.query(CourierLocation).filter(CourierLocation.id == location_id).first()
    if not location_db:
        raise HTTPException(status_code=404, detail="Локация не найдена")
    return location_db


@courier_location_router.put('/{location_id}', response_model=CourierLocationOutSchema)
async def update_location(location_id: int, location: CourierLocationInputSchema, db: Session = Depends(get_db)):
    location_db = db.query(CourierLocation).filter(CourierLocation.id == location_id).first()
    if not location_db:
        raise HTTPException(status_code=404, detail="Локация не найдена")

    for key, value in location.dict().items():
        setattr(location_db, key, value)

    db.commit()
    db.refresh(location_db)
    return location_db


@courier_location_router.delete('/{location_id}', response_model=dict)
async def delete_location(location_id: int, db: Session = Depends(get_db)):
    location_db = db.query(CourierLocation).filter(CourierLocation.id == location_id).first()
    if not location_db:
        raise HTTPException(status_code=404, detail="Локация не найдена")

    db.delete(location_db)
    db.commit()
    return {'message': 'Локация удалена'}