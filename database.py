from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# db_url = "postgresql://postgres:admin123@localhost:5432/python_project"
db_url = "mysql+pymysql://root:root@localhost:3306/python_project"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
