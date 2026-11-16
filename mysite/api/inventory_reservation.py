from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import InventoryReservation
from mysite.database.schema import InventoryReservationInputSchema, InventoryReservationOutSchema
from mysite.database.db import SessionLocal

reservation_router = APIRouter(prefix='/reservation', tags=['Reservation'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@reservation_router.post('/', response_model=InventoryReservationOutSchema)
async def create_reservation(reservation: InventoryReservationInputSchema, db: Session = Depends(get_db)):
    reservation_db = InventoryReservation(**reservation.dict())
    db.add(reservation_db)
    db.commit()
    db.refresh(reservation_db)
    return reservation_db


@reservation_router.get('/', response_model=List[InventoryReservationOutSchema])
async def list_reservations(db: Session = Depends(get_db)):
    return db.query(InventoryReservation).all()


@reservation_router.get('/{reservation_id}', response_model=InventoryReservationOutSchema)
async def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation_db = db.query(InventoryReservation).filter(InventoryReservation.id == reservation_id).first()
    if not reservation_db:
        raise HTTPException(status_code=404, detail="Резерв не найден")
    return reservation_db


@reservation_router.put('/{reservation_id}', response_model=InventoryReservationOutSchema)
async def update_reservation(reservation_id: int, reservation: InventoryReservationInputSchema, db: Session = Depends(get_db)):
    reservation_db = db.query(InventoryReservation).filter(InventoryReservation.id == reservation_id).first()
    if not reservation_db:
        raise HTTPException(status_code=404, detail="Резерв не найден")

    for key, value in reservation.dict().items():
        setattr(reservation_db, key, value)

    db.commit()
    db.refresh(reservation_db)
    return reservation_db


@reservation_router.delete('/{reservation_id}', response_model=dict)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation_db = db.query(InventoryReservation).filter(InventoryReservation.id == reservation_id).first()
    if not reservation_db:
        raise HTTPException(status_code=404, detail="Резерв не найден")

    db.delete(reservation_db)
    db.commit()
    return {'message': 'Резерв удалён'}