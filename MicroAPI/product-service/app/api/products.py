from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response
import pika
from app.api.models import ProductOut, ProductIn, ProductUpdate, OrderDetails, Order, Devis, DevisValidation
from app.api import db_manager
import logging
from app.api.pdf_generator import PDF

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post('/', response_model=ProductOut, status_code=201)
async def create_product(payload: ProductIn):
    product_id = await db_manager.add_product(payload)
    response = {
        'product_id': product_id,
        **payload.dict()
    }
    return response

@router.get('/', response_model=List[ProductOut])
async def get_products(name: Optional[str] = None, status: Optional[str] = None):
    return await db_manager.get_all_products(name, status)

@router.get('/{id}/', response_model=ProductOut)
async def get_product(id: int):
    product = await db_manager.get_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post('/check_availability', response_model=ProductOut)
async def get_product(payload: OrderDetails):
    product = await db_manager.get_product(payload.dict()["product_id"])
    if not product:
        logging.info("Product not found")
        raise HTTPException(status_code=404, detail="Product not found")
    
    def check_product_quantity(requested_quantity: int, available_quantity):
        if requested_quantity > available_quantity:
            return False
        return True
    
    if check_product_quantity(payload.dict()["quantity"], product._mapping['quantity']):
        pass
    else:
        raise HTTPException(status_code=404, detail="Quantity requested isn't available")
    return product


def send_event_mq(data, queue_name):
    credentials = pika.PlainCredentials('admin', 'food')
    parameters = pika.ConnectionParameters('rabbitmq',
                                       5672,
                                       '/',
                                       credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    
    message = str(data)
    channel.basic_publish(exchange='',  
                          routing_key=queue_name,
                          body=message)
    logging.info(f"[x] Sent {message}")
    connection.close()


@router.post("/send_event")
async def send_event(event_data: OrderDetails):
    logging.info(f"Data posted {event_data}")
    event_data = event_data.dict()
    event_data["status"] = "accepted"
    send_event_mq(event_data, "events")
    return {"message": "Command received!"}


@router.post("/get_devis")
async def get_devis(new_data: Order):
    order_dict = new_data.dict()
    new_data = {order_dict["order_id"]: {"quantity": order_dict["quantity"], "price": order_dict["price_net"]}}

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.chapter_title("Quote Details")
    pdf.chapter_body(new_data)

    pdf_output = pdf.output(dest='S').encode('latin1')
    response = Response(content=pdf_output, media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=quote_table.pdf"

    devis_data = {
        "order_id": order_dict["order_id"],
        "status": "waiting approval"
    }
    
    all_devis = await db_manager.get_all_devis()
    all_devis_orders = [dv["order_id"] for dv in all_devis]
    if order_dict["order_id"] not in all_devis_orders:
        devis = await db_manager.add_devis(devis_data)
        return response
    return response


@router.get('/get_devis/{id}/', response_model=Devis)
async def get_devis(id: int):
    devis = await db_manager.get_devis(id)
    if not devis:
        raise HTTPException(status_code=404, detail="Devis not found")
    return devis

@router.get('/get_all_devis')
async def get_all_devis():
    all_devis = await db_manager.get_all_devis()
    return all_devis

@router.put('/{id}/', response_model=ProductOut)
async def update_product(id: int, payload: ProductUpdate):
    product = await db_manager.get_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = payload.dict(exclude_unset=True)
    product_in_db = ProductIn(**product)
    updated_product = product_in_db.copy(update=update_data)
    return await db_manager.update_product(id, updated_product)

@router.delete('/{id}', response_model=None)
async def delete_product(id: int):
    product = await db_manager.get_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await db_manager.delete_product(id)


@router.post("/validate_devis_listener")
async def validate_devis(payload: DevisValidation):

    def get_status(isValid: bool):
        if isValid:
            return "devis accepted"
        return "devis refused"
    
    data = payload.dict()
    new_data = {
        "order_id": data["order_id"],
        "status": get_status(data["isValid"])
    }

    all_devis = await db_manager.update_devis(new_data["order_id"], new_data)

    def get_order_status(isValid: bool):
        if isValid:
            return "preparation done"
        return "refused"

    new = {
        "order_id": data["order_id"],
        "status": get_order_status(data["isValid"])
    }
    send_event_mq(new, "events")
    
    return "Devis status updated"