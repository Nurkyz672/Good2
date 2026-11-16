from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import Inventory
from mysite.database.schema import InventoryInputSchema, InventoryOutSchema
from mysite.database.db import SessionLocal

inventory_router = APIRouter(prefix='/inventory', tags=['Inventory'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@inventory_router.post('/', response_model=InventoryOutSchema)
async def create_inventory(inventory: InventoryInputSchema, db: Session = Depends(get_db)):
    inventory_db = Inventory(**inventory.dict())
    db.add(inventory_db)
    db.commit()
    db.refresh(inventory_db)
    return inventory_db


@inventory_router.get('/', response_model=List[InventoryOutSchema])
async def list_inventories(db: Session = Depends(get_db)):
    return db.query(Inventory).all()


@inventory_router.get('/{inventory_id}', response_model=InventoryOutSchema)
async def get_inventory(inventory_id: int, db: Session = Depends(get_db)):
    inventory_db = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_db:
        raise HTTPException(status_code=404, detail="Остаток не найден")
    return inventory_db


@inventory_router.put('/{inventory_id}', response_model=InventoryOutSchema)
async def update_inventory(inventory_id: int, inventory: InventoryInputSchema, db: Session = Depends(get_db)):
    inventory_db = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_db:
        raise HTTPException(status_code=404, detail="Остаток не найден")

    for key, value in inventory.dict().items():
        setattr(inventory_db, key, value)

    db.commit()
    db.refresh(inventory_db)
    return inventory_db


@inventory_router.delete('/{inventory_id}', response_model=dict)
async def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    inventory_db = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_db:
        raise HTTPException(status_code=404, detail="Остаток не найден")

    db.delete(inventory_db)
    db.commit()
    return {'message': 'Остаток удалён'}