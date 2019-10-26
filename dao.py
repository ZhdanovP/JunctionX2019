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
    db_string = "postgres://voexynoieveheo:b8e1d89b13851ba61e7cc7a4567d30d3613a55b19610b670a749690f4322dc76@ec2-54-246-92-116.eu-west-1.compute.amazonaws.com:5432/dck1ojnl5uc1sb"
    db = create_engine(db_string)
    return db


def add_catalog(gtin, quantity, shop_id):
    st = catalog.insert().values(gtin=gtin, quantity=quantity, shop_id=shop_id)
    conn().execute(st)


def get_all():
    st = catalog.select()
    result = conn().execute(st)
    return [dict(row) for row in result]