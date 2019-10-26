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


def get_all():
    statement = catalog.select()
    result = conn().execute(statement)
    return [dict(row) for row in result]