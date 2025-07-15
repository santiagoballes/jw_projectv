#!/usr/bin/env python3
"""
Script para crear el primer superusuario
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

def create_superuser():
    """Crear el primer superusuario"""
    print("=== Crear Superusuario ===")
    
    # Solicitar datos del usuario
    email = input("Email del superusuario: ")
    nombre = input("Nombre del superusuario: ")
    
    if not email or not nombre:
        print("Error: Email y nombre son obligatorios")
        return
    
    try:
        # Crear usuario en Supabase Auth
        print("Creando usuario en Supabase Auth...")
        auth_response = supabase.auth.admin.create_user({
            "email": email,
            "password": "admin123",  # Contraseña temporal
            "email_confirm": True
        })
        
        if not auth_response.user:
            print("Error: No se pudo crear el usuario en Auth")
            return
        
        user_id = auth_response.user.id
        print(f"Usuario creado en Auth con ID: {user_id}")
        
        # Crear registro en la tabla usuarios
        print("Creando registro en tabla usuarios...")
        user_data = {
            "id": user_id,
            "email": email,
            "nombre": nombre,
            "rol": "anciano",
            "is_superuser": True
        }
        
        result = supabase.table("usuarios").insert(user_data).execute()
        
        if result.data:
            print("✅ Superusuario creado exitosamente!")
            print(f"Email: {email}")
            print(f"Contraseña temporal: admin123")
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        else:
            print("Error: No se pudo crear el registro en la tabla usuarios")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_superuser() 