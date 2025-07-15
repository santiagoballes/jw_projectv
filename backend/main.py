from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, List
import uuid
from datetime import datetime
import requests

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY]):
    raise ValueError("Faltan variables de entorno de Supabase")

# Cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

app = FastAPI(title="API de Publicadores con Supabase Auth", version="2.0.0")
security = HTTPBearer()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://ornate-bonbon-a96471.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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
    grupo_asignado: Optional[int] = None

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
    grupo_asignado: Optional[int] = None

# --- MODELOS NOTIFICACIONES ---
class Notificacion(BaseModel):
    tipo: str  # Ejemplo: 'publicador_agregado', 'publicador_editado', etc.
    mensaje: str

class NotificacionOut(BaseModel):
    id: str
    tipo: str
    mensaje: str
    fecha_creacion: datetime

# Función para verificar JWT de Supabase y obtener usuario
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Verificar token con Supabase
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Obtener datos del usuario desde la tabla usuarios
        response = supabase.table("usuarios").select("*").eq("id", user.user.id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado en la base de datos"
            )
        
        # Asegurar que solo devolvemos un usuario
        if len(response.data) > 1:
            print(f"Advertencia: Múltiples usuarios encontrados para ID {user.user.id}")
        
        return response.data[0]
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

# --- DEPENDENCIAS PARA ROLES ---
def allowed_roles():
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in ["anciano", "siervo", "publicador"] and not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo ancianos, siervos, publicadores o superusuario pueden acceder"
            )
        return current_user
    return checker

# --- DEPENDENCIA PARA ROLES ADMINISTRATIVOS (anciano, siervo, superusuario) ---
def admin_roles():
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in ["anciano", "siervo"] and not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo ancianos, siervos o superusuario pueden acceder a funciones administrativas"
            )
        return current_user
    return checker

# --- DEPENDENCIA PARA ROLES DE MAPA (todos los roles activos) ---
def map_roles():
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in ["anciano", "siervo", "publicador"] and not current_user.get("is_superuser"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con roles activos pueden acceder al mapa"
            )
        return current_user
    return checker

# Rutas de autenticación
@app.post("/register")
async def register(data: RegisterRequest):
    """Registrar un nuevo usuario"""
    try:
        # Crear usuario en Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear usuario"
            )
        
        # Crear registro en la tabla usuarios
        user_data = {
            "id": auth_response.user.id,
            "email": data.email,
            "nombre": data.nombre,
            "rol": "pendiente",
            "is_superuser": False,
            "grupo_asignado": data.grupo_asignado # Incluir grupo_asignado si se proporciona
        }
        
        supabase.table("usuarios").insert(user_data).execute()
        
        return {
            "message": "Usuario registrado exitosamente. Esperando asignación de rol por el superusuario.",
            "user_id": auth_response.user.id
        }
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
        # Autenticar con Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Obtener datos del usuario
        user_response = supabase.table("usuarios").select("*").eq("id", auth_response.user.id).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        user_data = user_response.data[0]
        
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "nombre": user_data["nombre"],
                "rol": user_data["rol"],
                "is_superuser": user_data["is_superuser"]
            }
        }
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
        supabase.auth.sign_out()
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
        response = supabase.table("usuarios").select("*").execute()
        return response.data
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
    """Actualizar rol de usuario y grupo_asignado (solo superusuario)"""
    try:
        if role_data.rol not in ["anciano", "siervo", "pendiente"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no válido"
            )
        update_data = {
            "rol": role_data.rol,
            "is_superuser": role_data.is_superuser
        }
        # Permitir actualizar grupo_asignado si viene en el request
        if hasattr(role_data, "grupo_asignado") and role_data.grupo_asignado is not None:
            update_data["grupo_asignado"] = role_data.grupo_asignado
        response = supabase.table("usuarios").update(update_data).eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        # Notificación automática
        usuario_actualizado = response.data[0]
        crear_notificacion(
            "rol_cambiado",
            f"{superuser['nombre']} cambió el rol de '{usuario_actualizado['nombre']}' a '{role_data.rol}'"
        )
        return {
            "message": "Rol y grupo actualizados exitosamente",
            "user": usuario_actualizado
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en update_user_role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar rol o grupo"
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
        
        response = supabase.table("publicadores").select("*").order("created_at", desc=True).execute()
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en listar_publicadores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener publicadores"
        )

# --- FUNCIÓN AUXILIAR PARA CREAR NOTIFICACIONES ---
def crear_notificacion(tipo: str, mensaje: str):
    try:
        supabase.table("notificaciones").insert({"tipo": tipo, "mensaje": mensaje}).execute()
    except Exception as e:
        print(f"Error al crear notificación automática: {str(e)}")

@app.post("/publicadores", response_model=PublicadorResponse)
async def agregar_publicador(
    pub: Publicador,
    current_user: dict = Depends(check_role("anciano"))
):
    """Agregar un nuevo publicador (solo ancianos)"""
    try:
        publicador_data = {
            "nombre": pub.nombre,
            "numero": pub.numero,
            "grupo": pub.grupo,
            "precursor": pub.precursor,
            "animo": pub.animo,
            "creado_por": current_user["id"]
        }
        
        result = supabase.table("publicadores").insert(publicador_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear publicador"
            )
        
        # Notificación automática
        crear_notificacion(
            "publicador_agregado",
            f"{current_user['nombre']} agregó al publicador '{pub.nombre}'"
        )
        return result.data[0]
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
        # Verificar que el publicador existe
        existing = supabase.table("publicadores").select("*").eq("id", publicador_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicador no encontrado"
            )
        
        publicador_data = {
            "nombre": pub.nombre,
            "numero": pub.numero,
            "grupo": pub.grupo,
            "precursor": pub.precursor,
            "animo": pub.animo,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("publicadores").update(publicador_data).eq("id", publicador_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar publicador"
            )
        
        # Notificación automática
        crear_notificacion(
            "publicador_editado",
            f"{current_user['nombre']} editó al publicador '{pub.nombre}'"
        )
        return result.data[0]
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
        # Verificar que el publicador existe
        existing = supabase.table("publicadores").select("*").eq("id", publicador_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicador no encontrado"
            )
        
        nombre_pub = existing.data[0]["nombre"]
        supabase.table("publicadores").delete().eq("id", publicador_id).execute()
        
        # Notificación automática
        crear_notificacion(
            "publicador_eliminado",
            f"{current_user['nombre']} eliminó al publicador '{nombre_pub}'"
        )
        return {"message": "Publicador eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en eliminar_publicador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar publicador"
        )

# --- ENDPOINTS DE NOTIFICACIONES ---
@app.get("/notificaciones/", response_model=List[NotificacionOut])
async def listar_notificaciones(current_user: dict = Depends(allowed_roles())):
    """Listar notificaciones globales (solo ancianos, siervos y superusuario)"""
    try:
        response = supabase.table("notificaciones").select("*").order("fecha_creacion", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error al listar notificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener notificaciones")

# Renombrar el endpoint POST para evitar conflicto de nombres
@app.post("/notificaciones/", response_model=NotificacionOut)
async def crear_notificacion_endpoint(data: Notificacion, superuser: dict = Depends(get_superuser)):
    """Crear una notificación global (solo superusuario)"""
    try:
        noti_data = {
            "tipo": data.tipo,
            "mensaje": data.mensaje
        }
        response = supabase.table("notificaciones").insert(noti_data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="No se pudo crear la notificación")
        return response.data[0]
    except Exception as e:
        print(f"Error al crear notificación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear notificación")

@app.delete("/notificaciones/{noti_id}")
async def eliminar_notificacion(noti_id: str, superuser: dict = Depends(get_superuser)):
    """Eliminar una notificación por ID (solo superusuario)"""
    try:
        response = supabase.table("notificaciones").delete().eq("id", noti_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        return {"message": "Notificación eliminada"}
    except Exception as e:
        print(f"Error al eliminar notificación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar notificación")

# Ruta de prueba
@app.get("/")
async def root():
    return {"message": "API de Publicadores con Supabase Auth funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
