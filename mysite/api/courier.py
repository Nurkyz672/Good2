from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import Courier
from mysite.database.schema import CourierInputSchema, CourierOutSchema
from mysite.database.db import SessionLocal

courier_router = APIRouter(prefix='/courier', tags=['Courier'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@courier_router.post('/', response_model=CourierOutSchema)
async def create_courier(courier: CourierInputSchema, db: Session = Depends(get_db)):
    # Проверяем, является ли пользователь уже курьером
    existing_courier = db.query(Courier).filter(Courier.user_id == courier.user_id).first()
    if existing_courier:
        raise HTTPException(status_code=400, detail="Этот пользователь уже является курьером")

    courier_db = Courier(**courier.dict())
    db.add(courier_db)
    db.commit()
    db.refresh(courier_db)
    return courier_db


@courier_router.get('/', response_model=List[CourierOutSchema])
async def list_couriers(db: Session = Depends(get_db)):
    return db.query(Courier).all()


@courier_router.get('/{courier_id}', response_model=CourierOutSchema)
async def get_courier(courier_id: int, db: Session = Depends(get_db)):
    courier_db = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер не найден")
    return courier_db


@courier_router.put('/{courier_id}', response_model=CourierOutSchema)
async def update_courier(courier_id: int, courier: CourierInputSchema, db: Session = Depends(get_db)):
    courier_db = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер не найден")

    # Проверяем, является ли пользователь уже курьером
    existing_courier = db.query(Courier).filter(Courier.user_id == courier.user_id, Courier.id != courier_id).first()
    if existing_courier:
        raise HTTPException(status_code=400, detail="Этот пользователь уже является курьером")

    for key, value in courier.dict().items():
        setattr(courier_db, key, value)

    db.commit()
    db.refresh(courier_db)
    return courier_db


@courier_router.delete('/{courier_id}', response_model=dict)
async def delete_courier(courier_id: int, db: Session = Depends(get_db)):
    courier_db = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер не найден")

    db.delete(courier_db)
    db.commit()
    return {'message': 'Курьер удалён'}