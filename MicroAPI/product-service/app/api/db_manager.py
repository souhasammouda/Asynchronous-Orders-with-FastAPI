from app.api.models import ProductIn, Devis
from app.api.db import products, database, devis


async def add_product(payload: ProductIn):
    query = products.insert().values(**payload.dict())
    return await database.execute(query=query)

async def add_devis(payload):
    query = devis.insert().values(**payload)
    return await database.execute(query=query)

async def get_devis(id):
    query = devis.select(devis.c.order_id==id)
    return await database.fetch_one(query=query)

async def get_all_devis():
    query = devis.select()
    return await database.fetch_all(query=query)

async def get_all_products(name, status):
    if name and status:
        query = products.select(products.c.name==name and products.c.status==status)
    elif name:
        query = products.select(products.c.name==name)
    elif status:
        query = products.select(products.c.status==status)
    else:
        query = products.select()
    return await database.fetch_all(query=query)

async def get_product(id):
    query = products.select(products.c.product_id==id)
    return await database.fetch_one(query=query)

async def delete_product(id: int):
    query = products.delete().where(products.c.product_id==id)
    return await database.execute(query=query)

async def update_product(id: int, payload: ProductIn):
    query = (
        products
        .update()
        .where(products.c.product_id == id)
        .values(**payload.dict())
    )
    return await database.execute(query=query)

async def update_devis(id: int, payload: Devis):
    query = (
        devis
        .update()
        .where(devis.c.order_id == id)
        .values(**payload)
    )
    return await database.execute(query=query)