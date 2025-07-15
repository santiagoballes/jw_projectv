#!/bin/bash

echo "🚀 Configurando Sistema de Publicadores..."
echo "=========================================="

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python 3, Node.js y npm están instalados"

# Configurar backend
echo ""
echo "📦 Configurando Backend (FastAPI)..."
cd backend

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias de Python..."
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp env_example.txt .env
    echo "⚠️  IMPORTANTE: Edita el archivo backend/.env con tus credenciales de Supabase"
fi

cd ..

# Configurar frontend
echo ""
echo "📦 Configurando Frontend (Vue.js)..."
cd frontend

# Instalar dependencias
echo "📥 Instalando dependencias de Node.js..."
npm install

cd ..

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura tu proyecto en Supabase (https://supabase.com)"
echo "2. Ejecuta los comandos SQL del README.md en el SQL Editor de Supabase"
echo "3. Edita backend/.env con tus credenciales de Supabase"
echo "4. Ejecuta el backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "5. Ejecuta el frontend: cd frontend && npm run dev"
echo ""
echo "🌐 URLs:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "�� ¡Listo para usar!" 