import os
import secrets
import shutil
import time
from typing import List

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form, Security
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

# ------------------ Setup ------------------
app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

JWT_SECRET = secrets.token_hex(16)
JWT_ALGORITHM = "HS256"
FERNET_KEY = Fernet.generate_key()
cipher = Fernet(FERNET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ------------------ MongoDB Setup ------------------
MONGO_URL = "mongodb+srv://vaibhavchandelcs:vLK0omkwEi7VCcgW@cluster0.3vyurft.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URL)
db = client["file_sharing"]
user_col = db["users"]
file_col = db["files"]

# ------------------ Models ------------------
class User(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role: str  # 'ops' or 'client'
    email_verified: bool = False

class SignIn(BaseModel):
    email: EmailStr
    password: str

# ------------------ Utility ------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def sign(email: str, role: str) -> str:
    payload = {
        "email": email,
        "role": role,
        "exp": time.time() + 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    data = decode(token)
    user = await user_col.find_one({"email": data["email"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ------------------ Routes ------------------
@app.post("/signup")
async def signup(
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    if role not in ("ops", "client"):
        raise HTTPException(status_code=400, detail="Role must be 'ops' or 'client'")

    if await user_col.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = hash_password(password)
    user = {
        "name": name,
        "email": email,
        "hashed_password": hashed_pw,
        "role": role,
        "email_verified": False
    }
    await user_col.insert_one(user)
    encrypted_email = cipher.encrypt(email.encode()).decode()
    verify_url = f"http://localhost:8000/verify-email/{encrypted_email}"
    return {"verify_url": verify_url, "message": "Signup successful, please verify your email"}

@app.get("/verify-email/{encrypted_email}")
async def verify_email(encrypted_email: str):
    try:
        email = cipher.decrypt(encrypted_email.encode()).decode()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid verification link")

    result = await user_col.update_one({"email": email}, {"$set": {"email_verified": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Email verified successfully"}

@app.post("/signin")
async def signin(req: SignIn):
    user = await user_col.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Wrong password")
    if not user["email_verified"]:
        raise HTTPException(status_code=401, detail="Email not verified")
    token = sign(user["email"], user["role"])
    return {"access_token": token}

@app.post("/upload")
async def upload_file(
    credentials: HTTPAuthorizationCredentials = Security(security),
    file: UploadFile = File(...),
):
    user = await get_current_user(credentials)
    if user["role"] != "ops":
        raise HTTPException(status_code=403, detail="Only Ops users can upload files")

    if not file.filename.endswith((".docx", ".pptx", ".xlsx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: pptx, docx, xlsx")

    safe_filename = f"{secrets.token_hex(4)}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await file_col.insert_one({"filename": safe_filename, "uploader": user["email"]})
    return {"message": "File uploaded successfully", "filename": safe_filename}

@app.get("/list-files")
async def list_files(credentials: HTTPAuthorizationCredentials = Security(security)):
    user = await get_current_user(credentials)
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only Client users can list files")

    files = await file_col.find().to_list(length=None)
    result = []
    for f in files:
        encrypted_name = cipher.encrypt(f["filename"].encode()).decode()
        download_link = f"/secure-download/{encrypted_name}"
        result.append({"filename": f["filename"], "download_link": download_link})

    return {"files": result}

@app.get("/download-file/{filename}")
async def get_download_link(filename: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = await get_current_user(credentials)
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only Client users can request download links")

    file_exists = await file_col.find_one({"filename": filename})
    if not file_exists:
        raise HTTPException(status_code=404, detail="File not found")

    encrypted_name = cipher.encrypt(filename.encode()).decode()
    return {"download_link": f"/secure-download/{encrypted_name}", "message": "success"}

@app.get("/secure-download/{encrypted_name}")
async def download_file(encrypted_name: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    user = await get_current_user(credentials)
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only Client users can download files")

    try:
        filename = cipher.decrypt(encrypted_name.encode()).decode()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid download link")

    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="application/octet-stream", filename=filename)
