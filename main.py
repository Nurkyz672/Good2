import uvicorn
from fastapi import FastAPI
from mysite.database.db import Base, engine
from mysite.api import (warehouse, inventory,inventory_reservation, courier, courier_location, delivery,
                        route, route_stop, tracking_event)

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Goods Delivery API')


app.include_router(warehouse.warehouse_router)
app.include_router(inventory.inventory_router)
app.include_router(inventory_reservation.reservation_router)
app.include_router(courier.courier_router)
app.include_router(courier_location.courier_location_router)
app.include_router(delivery.delivery_router)
app.include_router(route.route_router)
app.include_router(route_stop.route_stop_router)
app.include_router(tracking_event.tracking_event_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8002)