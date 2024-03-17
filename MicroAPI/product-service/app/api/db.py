import os
import sqlalchemy
from databases import Database

DATABASE_URI = os.getenv('DATABASE_URI')

engine = sqlalchemy.create_engine(DATABASE_URI)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column('product_id', sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('price_net', sqlalchemy.Integer),
    sqlalchemy.Column('quantity', sqlalchemy.Integer),
    sqlalchemy.Column('status', sqlalchemy.String(50)),
)

devis = sqlalchemy.Table(
    'devis',
    metadata,
    sqlalchemy.Column('order_id', sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column('status', sqlalchemy.String(50))
)

devis.drop(engine)
devis.create(engine)

products.drop(engine)
products.create(engine)

database = Database(DATABASE_URI)

