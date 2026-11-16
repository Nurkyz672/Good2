from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from mysite.database.models import Delivery
from mysite.database.schema import DeliveryInputSchema, DeliveryOutSchema
from mysite.database.db import SessionLocal

delivery_router = APIRouter(prefix='/delivery', tags=['Delivery'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@delivery_router.post('/', response_model=DeliveryOutSchema)
async def create_delivery(delivery: DeliveryInputSchema, db: Session = Depends(get_db)):
    # Проверяем, есть ли уже доставка для этого заказа
    existing_delivery = db.query(Delivery).filter(Delivery.order_id == delivery.order_id).first()
    if existing_delivery:
        raise HTTPException(status_code=400, detail="Для этого заказа доставка уже существует")

    delivery_db = Delivery(**delivery.dict(), tracking_code=uuid4().hex[:12].upper())
    db.add(delivery_db)
    db.commit()
    db.refresh(delivery_db)
    return delivery_db


@delivery_router.get('/', response_model=List[DeliveryOutSchema])
async def list_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).all()


@delivery_router.get('/{delivery_id}', response_model=DeliveryOutSchema)
async def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery_db = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery_db:
        raise HTTPException(status_code=404, detail="Доставка не найдена")
    return delivery_db


@delivery_router.put('/{delivery_id}', response_model=DeliveryOutSchema)
async def update_delivery(delivery_id: int, delivery: DeliveryInputSchema, db: Session = Depends(get_db)):
    delivery_db = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery_db:
        raise HTTPException(status_code=404, detail="Доставка не найдена")

    # Проверяем, есть ли уже доставка для этого заказа
    existing_delivery = db.query(Delivery).filter(Delivery.order_id == delivery.order_id, Delivery.id != delivery_id).first()
    if existing_delivery:
        raise HTTPException(status_code=400, detail="Для этого заказа доставка уже существует")

    for key, value in delivery.dict().items():
        setattr(delivery_db, key, value)

    db.commit()
    db.refresh(delivery_db)
    return delivery_db


@delivery_router.delete('/{delivery_id}', response_model=dict)
async def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery_db = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery_db:
        raise HTTPException(status_code=404, detail="Доставка не найдена")

    db.delete(delivery_db)
    db.commit()
    return {'message': 'Доставка удалена'}