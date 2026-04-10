from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth.models import User
from auth.deps import verify_password, hash_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class AuthRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

@router.post("/register")
def register(req: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=req.username, hashed_password=hash_password(req.password))
    db.add(user)
    db.commit()
    return {"message": "注册成功"}

@router.post("/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user.id), "user": {"id": user.id, "username": user.username}}

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}