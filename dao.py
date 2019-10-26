import datetime
from typing import List

from sqlalchemy import MetaData, Column, String, DateTime, BigInteger, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import config

Base = declarative_base()

metadata = MetaData()


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(BigInteger, primary_key=True)
    gtin = Column(String)
    quantity = Column(Integer)
    shop_id = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {'gtin': self.gtin,
                'quantity': self.quantity,
                'shop_id': self.shop_id,
                'date': self.date}


class Cache(Base):
    __tablename__ = 'cache'

    gtin = Column(String, primary_key=True)
    image = Column(String)
    name = Column(String)
    description = Column(String)
    department = Column(String)

    def to_dict(self):
        return {'gtin': self.gtin,
                'image': self.image,
                'name': self.name,
                'description': self.description,
                'department': self.department}


class ORM:
    def __init__(self):
        user = config.db['user']
        password = config.db['password']
        host = config.db['host']
        port = config.db['port']
        database = config.db['database']
        db_address = f'postgres://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(db_address)
        self.session = self._get_session()

    def _get_session(self):
        try:
            Session = scoped_session(sessionmaker(bind=self.engine))
            self.session = Session()
            return self.session
        except Exception as e:
            print("Can't connect to db", e)

    def __del__(self):
        self.session.commit()
        self.session.close()
        self.session = None

    def add_catalog(self, gtin: str, quantity: int, shop_id: str):
        catalog = Catalog(gtin=gtin, quantity=quantity, shop_id=shop_id)
        self.session.add(catalog)
        self.session.commit()

    def get_catalog_all(self):
        result = self.session.query(Catalog).all()
        return [row.to_dict() for row in result]

    def get_catalog_by_shop(self, shop_id: str):
        result = self.session.query(Catalog).filter_by(shop_id=shop_id).all()
        return [row.to_dict() for row in result]

    def add_cache(self, gtin: str, name: str, image: str, description: str, department: str):
        cache = Cache(gtin=gtin, name=name, image=image, description=description, department=department)
        self.session.add(cache)
        self.session.commit()

    def get_cache(self, gtin: str) -> List:
        result = self.session.query(Cache).filter_by(gtin=gtin).all()
        return [row.to_dict() for row in result]


if __name__ == '__main__':
    orm = ORM()
    orm.add_catalog('000', 1, '123')
    orm.add_catalog('1', 1, '123')
    orm.add_catalog('2', 1, '123')
    orm.add_catalog('3', 1, '123')

    print(orm.get_catalog_all())
