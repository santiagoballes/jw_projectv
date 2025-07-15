#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    print("Error: Faltan variables de entorno de Supabase")
    sys.exit(1)

# Cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_users():
    """Verificar usuarios en la base de datos"""
    print("=== Verificando Usuarios ===")
    
    try:
        # Obtener todos los usuarios
        response = supabase.table("usuarios").select("*").execute()
        
        print(f"Total de usuarios: {len(response.data)}")
        
        for user in response.data:
            print(f"- ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Nombre: {user['nombre']}")
            print(f"  Rol: {user['rol']}")
            print(f"  Superusuario: {user['is_superuser']}")
            print("---")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def check_auth_users():
    """Verificar usuarios en auth.users"""
    print("\n=== Verificando Auth Users ===")
    
    try:
        # Obtener usuarios de auth (esto requiere permisos de admin)
        response = supabase.auth.admin.list_users()
        
        print(f"Total de usuarios en auth: {len(response.users)}")
        
        for user in response.users:
            print(f"- ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Confirmado: {user.email_confirmed_at is not None}")
            print("---")
            
    except Exception as e:
        print(f"Error al verificar auth users: {str(e)}")

if __name__ == "__main__":
    check_users()
    check_auth_users() 