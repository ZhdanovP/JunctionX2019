from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime
import config

metadata = MetaData()
catalog = Table('catalog', metadata,
                Column('id', Integer, primary_key=True),
                Column('gtin', String),
                Column('quantity', String),
                Column('shop_id', String),
                Column('date', DateTime))

cache = Table('cache', metadata,
              Column('gtin', String),
              Column('image', String),
              Column('description', String),
              Column('department', String))


def conn():
    user = config.db['user']
    password = config.db['password']
    host = config.db['host']
    port = config.db['port']
    database = config.db['database']
    db_address = "postgres://{}:{}@{}:{}/{}".format(user, password, host, port, database)
    db = create_engine(db_address)
    return db


def add_catalog(gtin: str, quantity: int, shop_id: str):
    statement = catalog.insert().values(gtin=gtin, quantity=quantity, shop_id=shop_id)
    conn().execute(statement)


def get_catalog_all():
    statement = catalog.select()
    result = conn().execute(statement)
    return [dict(row) for row in result]


def get_catalog_by_shop(shop_id: str):
    statement = catalog.select().where(catalog.c.shop_id == shop_id)
    result = conn().execute(statement)
    return [dict(row) for row in result]


def add_cache(gtin: str, image: str, description: str, department: str):
    statement = cache.insert().values(gtin=gtin, image=image, description=description, department=department)
    conn().execute(statement)


def get_cache(gtin: str):
    statement = cache.select().where(cache.c.gtin == gtin)
    result = conn().execute(statement)
    return [dict(row) for row in result]

