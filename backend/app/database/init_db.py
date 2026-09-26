from app.database.session import engine
from app.models.base import Base
import app.models  # noqa: F401


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
