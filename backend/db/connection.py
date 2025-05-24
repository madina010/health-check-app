from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/health"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# получение сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
