from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import Warehouse
from mysite.database.schema import WarehouseInputSchema, WarehouseOutSchema
from mysite.database.db import SessionLocal

warehouse_router = APIRouter(prefix='/warehouse', tags=['Warehouse'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@warehouse_router.post('/', response_model=WarehouseOutSchema)
async def create_warehouse(warehouse: WarehouseInputSchema, db: Session = Depends(get_db)):
    existing_warehouse = db.query(Warehouse).filter(Warehouse.code == warehouse.code).first()
    if existing_warehouse:
        raise HTTPException(status_code=400, detail="Склад с таким кодом уже существует")

    warehouse_db = Warehouse(**warehouse.dict())
    db.add(warehouse_db)
    db.commit()
    db.refresh(warehouse_db)
    return warehouse_db


@warehouse_router.get('/', response_model=List[WarehouseOutSchema])
async def list_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()


@warehouse_router.get('/{warehouse_id}', response_model=WarehouseOutSchema)
async def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse_db = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse_db:
        raise HTTPException(status_code=404, detail="Склад не найден")
    return warehouse_db


@warehouse_router.put('/{warehouse_id}', response_model=WarehouseOutSchema)
async def update_warehouse(warehouse_id: int, warehouse: WarehouseInputSchema, db: Session = Depends(get_db)):
    warehouse_db = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse_db:
        raise HTTPException(status_code=404, detail="Склад не найден")

    existing_warehouse = db.query(Warehouse).filter(Warehouse.code == warehouse.code,
                                                    Warehouse.id != warehouse_id).first()
    if existing_warehouse:
        raise HTTPException(status_code=400, detail="Склад с таким кодом уже существует")

    for key, value in warehouse.dict().items():
        setattr(warehouse_db, key, value)

    db.commit()
    db.refresh(warehouse_db)
    return warehouse_db


@warehouse_router.delete('/{warehouse_id}', response_model=dict)
async def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse_db = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse_db:
        raise HTTPException(status_code=404, detail="Склад не найден")

    db.delete(warehouse_db)
    db.commit()
    return {'message': 'Склад удалён'}