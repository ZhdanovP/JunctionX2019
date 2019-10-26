from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
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


class ORM:
    def __init__(self):
        user = config.db['user']
        password = config.db['password']
        host = config.db['host']
        port = config.db['port']
        database = config.db['database']
        db_address = "postgres://{}:{}@{}:{}/{}".format(user, password, host, port, database)
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
        statement = catalog.insert().values(gtin=gtin, quantity=quantity, shop_id=shop_id)
        self.session.execute(statement)
        self.session.commit()

    def get_catalog_all(self):
        statement = catalog.select()
        result = self.session.execute(statement)
        return [dict(row) for row in result]

    def get_catalog_by_shop(self, shop_id: str):
        statement = catalog.select().where(catalog.c.shop_id == shop_id)
        result = self.session.execute(statement)
        return [dict(row) for row in result]

    def add_cache(self, gtin: str, image: str, description: str, department: str):
        statement = self.session.insert().values(gtin=gtin, image=image, description=description, department=department)
        self.session.execute(statement)
        self.session.commit()

    def get_cache(self, gtin: str):
        statement = cache.select().where(cache.c.gtin == gtin)
        result = self.session.execute(statement)
        return [dict(row) for row in result]
