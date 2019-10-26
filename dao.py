from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime


metadata = MetaData()
catalog = Table('catalog', metadata,
                Column('id', Integer, primary_key=True),
                Column('gtin', String),
                Column('quantity', String),
                Column('shop_id', String),
                Column('date', DateTime))


def conn():
    db_address = "postgres://voexynoieveheo:b8e1d89b13851ba61e7cc7a4567d30d3613a55b19610b670a749690f4322dc76@ec2-54-246-92-116.eu-west-1.compute.amazonaws.com:5432/dck1ojnl5uc1sb"
    db = create_engine(db_address)
    return db


def add_catalog(gtin: str, quantity: int, shop_id: str):
    statement = catalog.insert().values(gtin=gtin, quantity=quantity, shop_id=shop_id)
    conn().execute(statement)


def get_all():
    statement = catalog.select()
    result = conn().execute(statement)
    return [dict(row) for row in result]