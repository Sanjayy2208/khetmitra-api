from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./khetmitra.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LedgerDB(Base):
    __tablename__ = "ledger"
    id = Column(String, primary_key=True, index=True)
    kind = Column(String)
    category = Column(String)
    label = Column(String)
    amount = Column(Float)
    date = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)