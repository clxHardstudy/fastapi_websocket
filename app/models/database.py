import time  # database.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from configs.setting import config

USER = config.get('db', 'user')
PWD = config.get('db', 'pwd')
DB_NAME = config.get('db', 'name')
HOST = config.get('db', 'host')
PORT = config.get('db', 'port')

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(bind=engine)


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, db: Session, enforce_update: Optional[dict] = None):
        for k in enforce_update or {}:
            flag_modified(self, k)
        if hasattr(self, "update_time"):
            self.update_time = int(time.time())
        # db.add(self)
        db.commit()
        db.flush()
        db.refresh(self)

    def set_field(self, data: Optional[dict] = None):
        for key in self.__class__.__dict__.keys():
            if key in data:
                if data[key] is None:
                    continue
            if not key.startswith('_') and key in data:
                setattr(self, key, data[key])
            if hasattr(self, 'update_time'):
                setattr(self, 'update_time', int(time.time()))
