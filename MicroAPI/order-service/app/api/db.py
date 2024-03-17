import os
import sqlalchemy
from databases import Database

DATABASE_URI = os.getenv('DATABASE_URI')

engine = sqlalchemy.create_engine(DATABASE_URI)
metadata = sqlalchemy.MetaData()

orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('order_id', sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column('customer_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('product_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('quantity', sqlalchemy.BigInteger),
    sqlalchemy.Column('price_net', sqlalchemy.Integer),
    sqlalchemy.Column('status', sqlalchemy.String(250))
)

orders.drop(engine)
orders.create(engine)

database = Database(DATABASE_URI)
