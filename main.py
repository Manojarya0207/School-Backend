from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI(title="School Management API", version="1.0")


@app.get("/")
def home():
    return {"message": "API is running"}


# MongoDB connection
client = MongoClient("mongodb+srv://School_DB:Manojarya0207@school-app-backend.7lejyhd.mongodb.net/?appName=School-App-Backend")
db = client["school_db"]
admins_collection = db["admins"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Config
SECRET_KEY = "mysupersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class LoginSchema(BaseModel):
    email: str
    password: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("admin/login")
def login(user: LoginSchema):
    db_user = admins_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": db_user["email"], "role": db_user["role"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}