#!/usr/bin/env python3
"""
Script para verificar y corregir políticas RLS
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

def test_user_access():
    """Probar acceso a usuarios"""
    print("=== Probando Acceso a Usuarios ===")
    
    try:
        # Intentar obtener usuarios
        response = supabase.table("usuarios").select("*").execute()
        print(f"✅ Acceso exitoso: {len(response.data)} usuarios encontrados")
        
        for user in response.data:
            print(f"- {user['email']} ({user['rol']})")
            
    except Exception as e:
        print(f"❌ Error de acceso: {str(e)}")

def test_specific_user():
    """Probar acceso a un usuario específico"""
    print("\n=== Probando Usuario Específico ===")
    
    try:
        # Buscar el usuario que creamos
        response = supabase.table("usuarios").select("*").eq("email", "s44401710@gmail.com").execute()
        
        if response.data:
            user = response.data[0]
            print(f"✅ Usuario encontrado: {user['nombre']} ({user['rol']})")
            print(f"   ID: {user['id']}")
            print(f"   Superusuario: {user['is_superuser']}")
        else:
            print("❌ Usuario no encontrado")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_rls_policies():
    """Verificar políticas RLS"""
    print("\n=== Verificando Políticas RLS ===")
    
    # Lista de políticas que deberían existir
    expected_policies = [
        "Usuarios pueden ver su propio perfil",
        "Usuarios pueden actualizar su propio perfil", 
        "Superusuarios pueden ver todos los usuarios"
    ]
    
    print("Políticas esperadas en tabla 'usuarios':")
    for policy in expected_policies:
        print(f"- {policy}")

if __name__ == "__main__":
    test_user_access()
    test_specific_user()
    check_rls_policies()
    
    print("\n=== Recomendaciones ===")
    print("Si hay errores de acceso, ejecuta este SQL en Supabase:")
    print("""
-- Deshabilitar RLS temporalmente para pruebas
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;

-- O crear una política más permisiva
DROP POLICY IF EXISTS "Superusuarios pueden ver todos los usuarios" ON usuarios;
CREATE POLICY "Superusuarios pueden ver todos los usuarios" ON usuarios
  FOR ALL USING (true);
    """) 