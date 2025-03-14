from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, User as UserModel
import secrets
from dotenv import load_dotenv
import os

app = FastAPI()

# Configuración de seguridad
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ----- MODELOS -----
class User(BaseModel):
    username: str
    full_name: str = None
    disabled: bool = False
    role: str = "user"

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "user"

# ----- FUNCIONES -----
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

async def get_current_admin_user(current_user: UserModel = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    return current_user

# ----- ENDPOINTS -----

@app.post("/register", summary="Registro de usuario en base de datos")
def register(user: UserRegister, db: Session = Depends(get_db)):
    username = user.username
    password = user.password
    role = user.role

    # Validar si el usuario ya existe
    existing_user = db.query(UserModel).filter(UserModel.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = get_password_hash(password)

    # Crear el nuevo usuario
    new_user = UserModel(
        username=username,
        full_name=username.capitalize(),
        hashed_password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"Usuario '{username}' registrado correctamente como '{role}'"}

@app.post("/login", summary="Inicio de sesión y generación de JWT")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", summary="Consultar usuario autenticado")
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "disabled": current_user.disabled,
        "role": current_user.role
    }

@app.get("/admin/dashboard", summary="Panel solo para administradores")
async def admin_dashboard(admin_user: UserModel = Depends(get_current_admin_user)):
    return {
        "message": f"Bienvenido Admin {admin_user.username} al dashboard privado"
    }

