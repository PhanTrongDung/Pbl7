from fastapi import APIRouter

from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register_user(payload: UserCreate):
    return {
        "id": 1,
        "name": payload.name,
        "email": payload.email,
        "role": "user",
    }


@router.post("/login")
def login_user():
    return {"message": "Login endpoint ready"}
