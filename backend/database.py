from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Local Postgres connection string for development
# MAC
URL_DATABASE = 'postgresql://admin:admin@localhost:5432/hustlehub'

# WINDOWS
# URL_DATABASE = 'postgresql://postgres:yourpassword@localhost:5432/hustlehub'


engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
