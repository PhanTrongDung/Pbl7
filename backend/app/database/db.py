from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:@localhost/legal_ai"

engine = create_engine(DATABASE_URL, echo=True, future=True)

__all__ = ["engine", "DATABASE_URL"]
