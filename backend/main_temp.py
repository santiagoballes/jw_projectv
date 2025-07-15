from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
from typing import Optional, List
import uuid
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="API de Publicadores - Versión Temporal", version="2.0.0")
security = HTTPBearer()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Almacenamiento temporal en memoria
usuarios_temp = {
    "admin@test.com": {
        "id": "admin-123",
        "email": "admin@test.com",
        "nombre": "Administrador",
        "rol": "anciano",
        "is_superuser": True
    }
}

publicadores_temp = []

# Modelos Pydantic
class Publicador(BaseModel):
    nombre: str
    numero: str
    grupo: int
    precursor: bool
    animo: bool

class PublicadorResponse(Publicador):
    id: str
    creado_por: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Usuario(BaseModel):
    email: EmailStr
    nombre: str
    rol: str = "pendiente"
    is_superuser: bool = False

class UsuarioResponse(Usuario):
    id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str

class RoleUpdateRequest(BaseModel):
    user_id: str
    rol: str
    is_superuser: bool = False

# Función para verificar JWT temporal
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Verificación temporal - buscar por email en el token
        if token in usuarios_temp:
            return usuarios_temp[token]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except Exception as e:
        print(f"Error en get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

# Función para verificar si es superusuario
async def get_superuser(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere ser superusuario"
        )
    return current_user

# Función para verificar rol específico
def check_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] != required_role and not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Solo {required_role}s pueden realizar esta acción"
            )
        return current_user
    return role_checker

# Rutas de autenticación
@app.post("/register")
async def register(data: RegisterRequest):
    """Registrar un nuevo usuario"""
    try:
        if data.email in usuarios_temp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario ya existe"
            )
        
        # Crear usuario temporal
        user_data = {
            "id": str(uuid.uuid4()),
            "email": data.email,
            "nombre": data.nombre,
            "rol": "pendiente",
            "is_superuser": False
        }
        
        usuarios_temp[data.email] = user_data
        
        return {
            "message": "Usuario registrado exitosamente. Esperando asignación de rol por el superusuario.",
            "user_id": user_data["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en register: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@app.post("/login")
async def login(data: LoginRequest):
    """Iniciar sesión"""
    try:
        # Verificar credenciales temporales
        if data.email not in usuarios_temp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        user_data = usuarios_temp[data.email]
        
        # Para pruebas, aceptar cualquier contraseña
        if data.password == "test123" or data.email == "admin@test.com":
            return {
                "access_token": data.email,  # Usar email como token temporal
                "refresh_token": "temp-refresh-token",
                "user": user_data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al iniciar sesión"
        )

@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Cerrar sesión"""
    try:
        return {"message": "Sesión cerrada exitosamente"}
    except Exception as e:
        print(f"Error en logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cerrar sesión"
        )

# Rutas de administración (solo superusuario)
@app.get("/admin/users", response_model=List[UsuarioResponse])
async def list_users(superuser: dict = Depends(get_superuser)):
    """Listar todos los usuarios (solo superusuario)"""
    try:
        return list(usuarios_temp.values())
    except Exception as e:
        print(f"Error en list_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuarios"
        )

@app.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: RoleUpdateRequest,
    superuser: dict = Depends(get_superuser)
):
    """Actualizar rol de usuario (solo superusuario)"""
    try:
        if role_data.rol not in ["anciano", "siervo", "pendiente"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no válido"
            )
        
        # Buscar usuario por ID
        user_email = None
        for email, user in usuarios_temp.items():
            if user["id"] == user_id:
                user_email = email
                break
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar usuario
        usuarios_temp[user_email]["rol"] = role_data.rol
        usuarios_temp[user_email]["is_superuser"] = role_data.is_superuser
        
        return {
            "message": "Rol actualizado exitosamente",
            "user": usuarios_temp[user_email]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en update_user_role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar rol"
        )

# Rutas de publicadores
@app.get("/publicadores", response_model=List[PublicadorResponse])
async def listar_publicadores(current_user: dict = Depends(get_current_user)):
    """Listar todos los publicadores"""
    try:
        # Verificar que el usuario tenga rol válido
        if current_user["rol"] not in ["anciano", "siervo"] and not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver publicadores"
            )
        
        return publicadores_temp
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en listar_publicadores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener publicadores"
        )

@app.post("/publicadores", response_model=PublicadorResponse)
async def agregar_publicador(
    pub: Publicador,
    current_user: dict = Depends(check_role("anciano"))
):
    """Agregar un nuevo publicador (solo ancianos)"""
    try:
        publicador_data = {
            "id": str(uuid.uuid4()),
            "nombre": pub.nombre,
            "numero": pub.numero,
            "grupo": pub.grupo,
            "precursor": pub.precursor,
            "animo": pub.animo,
            "creado_por": current_user["id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        publicadores_temp.append(publicador_data)
        return publicador_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en agregar_publicador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear publicador"
        )

@app.put("/publicadores/{publicador_id}", response_model=PublicadorResponse)
async def editar_publicador(
    publicador_id: str,
    pub: Publicador,
    current_user: dict = Depends(check_role("anciano"))
):
    """Editar un publicador (solo ancianos)"""
    try:
        # Buscar publicador
        publicador_index = None
        for i, p in enumerate(publicadores_temp):
            if p["id"] == publicador_id:
                publicador_index = i
                break
        
        if publicador_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicador no encontrado"
            )
        
        # Actualizar publicador
        publicadores_temp[publicador_index].update({
            "nombre": pub.nombre,
            "numero": pub.numero,
            "grupo": pub.grupo,
            "precursor": pub.precursor,
            "animo": pub.animo,
            "updated_at": datetime.utcnow()
        })
        
        return publicadores_temp[publicador_index]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en editar_publicador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar publicador"
        )

@app.delete("/publicadores/{publicador_id}")
async def eliminar_publicador(
    publicador_id: str,
    current_user: dict = Depends(check_role("anciano"))
):
    """Eliminar un publicador (solo ancianos)"""
    try:
        # Buscar y eliminar publicador
        publicador_index = None
        for i, p in enumerate(publicadores_temp):
            if p["id"] == publicador_id:
                publicador_index = i
                break
        
        if publicador_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicador no encontrado"
            )
        
        publicadores_temp.pop(publicador_index)
        
        return {"message": "Publicador eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en eliminar_publicador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar publicador"
        )

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "API de Publicadores - Versión Temporal funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 