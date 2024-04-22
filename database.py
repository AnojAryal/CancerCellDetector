from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



SQLALCHEMY_DATABASE_URL = "postgresql://franzy:fastrack@localhost/CancerCellDetection_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal  =sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()


#Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()