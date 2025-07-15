from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from supabase_client import supabase
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="API de Publicadores", version="1.0.0")
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "default-secret")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],  # Vue.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Modelos Pydantic
class Publicador(BaseModel):
    nombre: str
    numero: str  # Cambiado de int a str para permitir números grandes
    grupo: int
    precursor: bool
    animo: bool

class PublicadorResponse(Publicador):
    id: str

class Usuario(BaseModel):
    nombre: str
    rol: str

class UsuarioResponse(Usuario):
    id: str

class LoginRequest(BaseModel):
    username: str
    rol: str

# Función para verificar JWT y obtener usuario
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Buscar usuario en Supabase
        response = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return response.data[0]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Función para verificar rol
def check_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] != required_role:
            raise HTTPException(status_code=403, detail=f"Solo {required_role}s pueden realizar esta acción")
        return current_user
    return role_checker

# Rutas de autenticación
@app.post("/login")
async def login(data: LoginRequest):
    username = data.username
    rol = data.rol
    if rol not in ["anciano", "siervo"]:
        raise HTTPException(status_code=400, detail="Rol no permitido")
    
    # Crear o actualizar usuario en Supabase
    user_data = {
        "id": str(uuid.uuid4()),  # En producción usar el ID real de Supabase Auth
        "nombre": username,
        "rol": rol
    }
    
    # Verificar si el usuario ya existe
    existing_user = supabase.table("usuarios").select("*").eq("nombre", username).execute()
    
    if existing_user.data:
        # Actualizar usuario existente
        supabase.table("usuarios").update({"rol": rol}).eq("nombre", username).execute()
        user_id = existing_user.data[0]["id"]
    else:
        # Crear nuevo usuario
        result = supabase.table("usuarios").insert(user_data).execute()
        user_id = result.data[0]["id"]
    
    # Generar token JWT
    token = jwt.encode(
        {"sub": user_id, "rol": rol, "nombre": username}, 
        JWT_SECRET, 
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

# Rutas de publicadores
@app.get("/publicadores", response_model=list[PublicadorResponse])
async def listar_publicadores():
    """Listar todos los publicadores"""
    response = supabase.table("publicadores").select("*").execute()
    return response.data

@app.post("/publicadores", response_model=PublicadorResponse)
async def agregar_publicador(
    pub: Publicador, 
    current_user: dict = Depends(check_role("anciano"))
):
    """Agregar un nuevo publicador (solo ancianos)"""
    publicador_data = {
        "id": str(uuid.uuid4()),
        "nombre": pub.nombre,
        "numero": pub.numero,
        "grupo": pub.grupo,
        "precursor": pub.precursor,
        "animo": pub.animo
    }
    
    result = supabase.table("publicadores").insert(publicador_data).execute()
    return result.data[0]

@app.put("/publicadores/{publicador_id}", response_model=PublicadorResponse)
async def editar_publicador(
    publicador_id: str,
    pub: Publicador, 
    current_user: dict = Depends(get_current_user)
):
    """Editar un publicador (ancianos y siervos)"""
    try:
        if current_user["rol"] not in ["anciano", "siervo"]:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar")
        
        # Verificar que el publicador existe
        existing = supabase.table("publicadores").select("*").eq("id", publicador_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Publicador no encontrado")
        
        publicador_data = {
            "nombre": pub.nombre,
            "numero": pub.numero,
            "grupo": pub.grupo,
            "precursor": pub.precursor,
            "animo": pub.animo
        }
        
        result = supabase.table("publicadores").update(publicador_data).eq("id", publicador_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error al actualizar publicador")
            
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en editar_publicador: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.delete("/publicadores/{publicador_id}")
async def eliminar_publicador(
    publicador_id: str,
    current_user: dict = Depends(check_role("anciano"))
):
    """Eliminar un publicador (solo ancianos)"""
    # Verificar que el publicador existe
    existing = supabase.table("publicadores").select("*").eq("id", publicador_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Publicador no encontrado")
    
    supabase.table("publicadores").delete().eq("id", publicador_id).execute()
    return {"message": "Publicador eliminado exitosamente"}

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "API de Publicadores funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 