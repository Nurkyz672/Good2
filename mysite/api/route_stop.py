from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import RouteStop
from mysite.database.schema import RouteStopInputSchema, RouteStopOutSchema
from mysite.database.db import SessionLocal

route_stop_router = APIRouter(prefix='/route-stop', tags=['Route Stop'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@route_stop_router.post('/', response_model=RouteStopOutSchema)
async def create_stop(stop: RouteStopInputSchema, db: Session = Depends(get_db)):
    stop_db = RouteStop(**stop.dict())
    db.add(stop_db)
    db.commit()
    db.refresh(stop_db)
    return stop_db


@route_stop_router.get('/', response_model=List[RouteStopOutSchema])
async def list_stops(db: Session = Depends(get_db)):
    return db.query(RouteStop).all()


@route_stop_router.get('/{stop_id}', response_model=RouteStopOutSchema)
async def get_stop(stop_id: int, db: Session = Depends(get_db)):
    stop_db = db.query(RouteStop).filter(RouteStop.id == stop_id).first()
    if not stop_db:
        raise HTTPException(status_code=404, detail="Остановка не найдена")
    return stop_db


@route_stop_router.put('/{stop_id}', response_model=RouteStopOutSchema)
async def update_stop(stop_id: int, stop: RouteStopInputSchema, db: Session = Depends(get_db)):
    stop_db = db.query(RouteStop).filter(RouteStop.id == stop_id).first()
    if not stop_db:
        raise HTTPException(status_code=404, detail="Остановка не найдена")

    for key, value in stop.dict().items():
        setattr(stop_db, key, value)

    db.commit()
    db.refresh(stop_db)
    return stop_db


@route_stop_router.delete('/{stop_id}', response_model=dict)
async def delete_stop(stop_id: int, db: Session = Depends(get_db)):
    stop_db = db.query(RouteStop).filter(RouteStop.id == stop_id).first()
    if not stop_db:
        raise HTTPException(status_code=404, detail="Остановка не найдена")

    db.delete(stop_db)
    db.commit()
    return {'message': 'Остановка удалена'}