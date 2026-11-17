from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Annotated
from mysite.database.models import Courier
from mysite.database.schema import CourierCreateSchema, CourierOutSchema
from mysite.database.db import SessionLocal
from mysite.config import SECRET_KEY, ALGORITHM

courier_router = APIRouter(prefix='/courier', tags=['Courier'])

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_id(token: Annotated[str, Depends(oauth2_schema)]) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Токен жараксыз",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception


def get_own_courier(courier_id: int, user_id: int, db: Session) -> Courier:
    courier_db = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер табылган жок")
    if courier_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="Бул сиздин профиль эмес")
    return courier_db


@courier_router.post('/', response_model=CourierOutSchema)
async def create_courier(
    courier: CourierCreateSchema,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),):
    existing_courier = db.query(Courier).filter(Courier.user_id == user_id).first()
    if existing_courier:
        raise HTTPException(status_code=400, detail="Бул колдонуучу мурунтан эле курьер")

    courier_db = Courier(user_id=user_id, **courier.model_dump())
    try:
        db.add(courier_db)
        db.commit()
        db.refresh(courier_db)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Курьерди сактоодо ката кетти")
    return courier_db


@courier_router.get('/', response_model=List[CourierOutSchema])
async def list_couriers(db: Session = Depends(get_db)):
    return db.query(Courier).all()


@courier_router.get('/me/', response_model=CourierOutSchema)
async def get_my_courier(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),):
    courier_db = db.query(Courier).filter(Courier.user_id == user_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер табылган жок")
    return courier_db


@courier_router.get('/{courier_id}', response_model=CourierOutSchema)
async def get_courier(courier_id: int, db: Session = Depends(get_db)):
    courier_db = db.query(Courier).filter(Courier.id == courier_id).first()
    if not courier_db:
        raise HTTPException(status_code=404, detail="Курьер табылган жок")
    return courier_db


@courier_router.put('/{courier_id}', response_model=CourierOutSchema)
async def update_courier(
    courier_id: int,
    courier: CourierCreateSchema,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),):
    courier_db = get_own_courier(courier_id, user_id, db)

    for key, value in courier.model_dump().items():
        setattr(courier_db, key, value)

    try:
        db.commit()
        db.refresh(courier_db)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Курьерди жаңыртууда ката кетти")
    return courier_db


@courier_router.delete('/{courier_id}', response_model=dict)
async def delete_courier(
    courier_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),):
    courier_db = get_own_courier(courier_id, user_id, db)

    db.delete(courier_db)
    db.commit()
    return {'message': 'Курьер өчүрүлдү'}