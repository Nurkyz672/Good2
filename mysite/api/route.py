from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.models import Route
from mysite.database.schema import RouteInputSchema, RouteOutSchema
from mysite.database.db import SessionLocal

route_router = APIRouter(prefix='/route', tags=['Route'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@route_router.post('/', response_model=RouteOutSchema)
async def create_route(route: RouteInputSchema, db: Session = Depends(get_db)):
    route_db = Route(**route.dict())
    db.add(route_db)
    db.commit()
    db.refresh(route_db)
    return route_db


@route_router.get('/', response_model=List[RouteOutSchema])
async def list_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()


@route_router.get('/{route_id}', response_model=RouteOutSchema)
async def get_route(route_id: int, db: Session = Depends(get_db)):
    route_db = db.query(Route).filter(Route.id == route_id).first()
    if not route_db:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    return route_db


@route_router.put('/{route_id}', response_model=RouteOutSchema)
async def update_route(route_id: int, route: RouteInputSchema, db: Session = Depends(get_db)):
    route_db = db.query(Route).filter(Route.id == route_id).first()
    if not route_db:
        raise HTTPException(status_code=404, detail="Маршрут не найден")

    for key, value in route.dict().items():
        setattr(route_db, key, value)

    db.commit()
    db.refresh(route_db)
    return route_db


@route_router.delete('/{route_id}', response_model=dict)
async def delete_route(route_id: int, db: Session = Depends(get_db)):
    route_db = db.query(Route).filter(Route.id == route_id).first()
    if not route_db:
        raise HTTPException(status_code=404, detail="Маршрут не найден")

    db.delete(route_db)
    db.commit()
    return {'message': 'Маршрут удалён'}