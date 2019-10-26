import datetime
from typing import List

from sqlalchemy import MetaData, Column, String, DateTime, BigInteger, Integer, Float
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
    weight = Column(Float)
    price = Column(Float)

    def to_dict(self):
        return {'gtin': self.gtin,
                'image': self.image,
                'name': self.name,
                'description': self.description,
                'weight': self.weight,
                'price': self.price,
                'department': self.department}


class Shop(Base):
    __tablename__ = 'shop'

    id = Column(String, primary_key=True)
    address = Column(String)
    type = Column(String)
    name = Column(String)
    lon = Column(Float)
    lat = Column(Float)

    def to_dict(self):
        return {'id': self.id,
                'address': self.address,
                'type': self.type,
                'name': self.name,
                'lon': self.lon,
                'lat': self.lat}


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
        try:
            self.session.commit()
            self.session.close()
            self.session = None
        except Exception as e:
            print(e)

    def __add_sth(self, added_type, **args):
        try:
            sth = added_type(**args)
            self.session.add(sth)
            self.session.commit()
        except Exception as e:
            print(f'Exception was raised during adding {added_type} with params {args}. {e}')
            self.session.rollback()

    def __get_sth_by_values(self, returned_class, **values):
        result = self.session.query(returned_class).filter_by(**values).all()
        return [row.to_dict() for row in result]

    def add_catalog(self, gtin: str, quantity: int, shop_id: str):
        self.__add_sth(Catalog, gtin=gtin, quantity=quantity, shop_id=shop_id)

    def get_catalog_all(self):
        result = self.session.query(Catalog).all()
        return [row.to_dict() for row in result]

    def get_catalog_by_shop(self, shop_id: str):
        return self.__get_sth_by_values(Catalog, shop_id=shop_id)

    def add_cache(self, gtin: str, name: str, image: str, description: str, department: str, weight: float,
                  price: float):
        self.__add_sth(Cache, gtin=gtin, name=name, image=image, description=description, department=department,
                       weight=weight, price=price)

    def get_cache(self, gtin: str) -> List:
        return self.__get_sth_by_values(Cache, gtin=gtin)

    def add_shop(self, _id: str, address: str, _type: str, name: str, lon: float, lat: float):
        self.__add_sth(Shop, id=_id, address=address, type=_type, name=name, lon=lon, lat=lat)

    def get_shop_by_id(self, shop_id):
        return self.__get_sth_by_values(Shop, id=shop_id)


if __name__ == '__main__':
    orm = ORM()
    shop_id = "fdacbf60-7b73-4678-86f4-266b86750e3b"
    orm.add_shop(shop_id, "Budapest, VIII. kerület", "Expressz",
                 "TESCO Expressz Bp. - Mátyás tér", 19.079964, 47.492391)

    orm.add_catalog('0', 1, shop_id)
    orm.add_catalog('1', 1, shop_id)
    orm.add_catalog('2', 1, shop_id)
    orm.add_catalog('3', 1, shop_id)



    print(orm.get_shop_by_id(shop_id))
