import requests
from typing import List
from fastapi import APIRouter, HTTPException, Response
import json
from app.api.models import OrderOut, OrderIn, OrderUpdate, DevisIn, ValidateDevis
from app.api import db_manager
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post('/', status_code=201)
async def create_order(payload: OrderIn):
    order_id = await db_manager.add_order(payload)
    response = {
        'order_id': order_id,
        **payload.dict()
    }

    data = {
        "order_id": response["order_id"],
        "product_id": response["product_id"],
        "quantity": response["quantity"]
    }

    req = requests.post(f'http://product_service:8000/api/v1/products/send_event', data=json.dumps(data))
    return req.json()


@router.get('/', response_model=List[OrderOut])
async def get_orders():
    return await db_manager.get_all_orders()


@router.get('/{id}/', response_model=OrderOut)
async def get_order(id: int):
    order = await db_manager.get_order(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/validate_devis")
async def validate_devis(payload: ValidateDevis):

    def get_devis_message(data):
        if data["isValid"]:
            return "Devis validated"
        return "Devis refused"

    data = payload.dict()
    req = requests.post(f'http://product_service:8000/api/v1/products/validate_devis_listener', data=json.dumps(data))
    logging.info("Validate Devis:   Finish requesting")
    return {
        "message": get_devis_message(data)
    }


@router.post("/send_event_devis")
async def get_devis(payload: DevisIn):

    id = payload.dict()["id"]
    order = await db_manager.get_order(id)
    order_dict = order._mapping

    data = {
        "order_id": order_dict["order_id"],
        "customer_id": order_dict["customer_id"],
        "product_id": order_dict["product_id"],
        "quantity": order_dict["quantity"],
        "price_net": order_dict["price_net"],
        "status": order_dict["status"]
    }

    req = requests.post(f'http://product_service:8000/api/v1/products/get_devis', data=json.dumps(data))
    response = Response(content=req.content, media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=quote_table.pdf"

    return response
    

@router.put('/{id}/', response_model=OrderOut)
async def update_order(id: int, payload: OrderUpdate):
    order = await db_manager.get_order(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    update_data = payload.dict(exclude_unset=True)
    order_in_db = OrderIn(**order)
    updated_order = order_in_db.copy(update=update_data)
    return await db_manager.update_order(id, updated_order)

@router.delete('/{id}', response_model=None)
async def delete_order(id: int):
    order = await db_manager.get_order(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return await db_manager.delete_order(id)
