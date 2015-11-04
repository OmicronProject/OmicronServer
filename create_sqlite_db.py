from db_schema import metadata
from sqlalchemy import create_engine
from config import DATABASE_URI

engine = create_engine(DATABASE_URI)

metadata.create_all(bind=engine)

