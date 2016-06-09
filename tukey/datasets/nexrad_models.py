from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Date
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy import create_engine
Base = declarative_base()

class IndexRecordHash(Base):
    '''
    Base index record hash representation.
    '''
    __tablename__ = 'index_record_hash'

    did = Column(String, primary_key=True)
    hash_type = Column(String, primary_key=True)
    hash_value = Column(String)

class AliasRecordHash(Base):
    '''
    Base alias record hash representation.
    '''
    __tablename__ = 'alias_record_hash'

    name = Column(String, primary_key=True)
    hash_type = Column(String, primary_key=True)
    hash_value = Column(String)

class NOAAMetadata(Base):
    '''
    Base index record url representation.
    '''
    __tablename__ = 'noaa_metadata'

    did = Column(String, primary_key=True)
    instrument = Column(String)
    location = Column(String)
    date = Column(Date)

class SQLAlchemyIndexDriver(object):

    def __init__(self, conn, **config):
        self.engine = create_engine(conn, **config)

        Base.metadata.bind = self.engine
        Base.metadata.create_all()

        self.Session = sessionmaker(bind=self.engine)

    @property
    @contextmanager
    def session(self):
        '''
        Provide a transactional scope around a series of operations.
        '''
        session = self.Session()

        yield session

        try: session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
