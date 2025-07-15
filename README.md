# Sistema de Publicadores con Autenticación Real

Este proyecto implementa un sistema completo de gestión de publicadores con autenticación real usando Supabase, incluyendo roles de usuario y un panel de administración.

## 🚀 Características

- **Autenticación Real**: Registro e inicio de sesión con Supabase Auth
- **Gestión de Roles**: Sistema de roles (anciano, siervo, pendiente)
- **Panel de Administración**: Superusuarios pueden asignar roles
- **Gestión de Publicadores**: CRUD completo con permisos por rol
- **Estadísticas**: Dashboard con gráficos usando Chart.js
- **Modo Oscuro**: Interfaz con tema claro/oscuro
- **Responsive**: Diseño adaptativo para móviles

## 📋 Requisitos Previos

- Node.js 16+ y npm
- Python 3.8+
- Cuenta en Supabase (gratuita)

## 🛠️ Configuración

### 1. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. Ve a Settings > API y copia:
   - Project URL
   - Anon Key
   - Service Role Key

### 2. Configurar Base de Datos

Ejecuta estos scripts SQL en el SQL Editor de Supabase:

#### Crear tabla usuarios:
```sql
CREATE TABLE usuarios (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  nombre TEXT NOT NULL,
  rol TEXT DEFAULT 'pendiente' CHECK (rol IN ('anciano', 'siervo', 'pendiente')),
  is_superuser BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Políticas RLS
CREATE POLICY "Usuarios pueden ver su propio perfil" ON usuarios
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Usuarios pueden actualizar su propio perfil" ON usuarios
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Superusuarios pueden ver todos los usuarios" ON usuarios
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND is_superuser = true
    )
  );
```

#### Crear tabla publicadores:
```sql
CREATE TABLE publicadores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  numero TEXT NOT NULL,
  grupo INTEGER NOT NULL,
  precursor BOOLEAN DEFAULT FALSE,
  animo BOOLEAN DEFAULT FALSE,
  creado_por UUID REFERENCES usuarios(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS
ALTER TABLE publicadores ENABLE ROW LEVEL SECURITY;

-- Políticas RLS
CREATE POLICY "Usuarios con rol pueden ver publicadores" ON publicadores
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo')
    )
  );

CREATE POLICY "Ancianos pueden crear publicadores" ON publicadores
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol = 'anciano'
    )
  );

CREATE POLICY "Ancianos pueden actualizar publicadores" ON publicadores
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol = 'anciano'
    )
  );

CREATE POLICY "Ancianos pueden eliminar publicadores" ON publicadores
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol = 'anciano'
    )
  );
```

### 3. Configurar Backend

1. Ve al directorio `backend/`
2. Copia `env_example.txt` como `.env`:
   ```bash
   cp env_example.txt .env
   ```
3. Edita `.env` con tus credenciales de Supabase:
   ```env
   SUPABASE_URL=https://tu-proyecto-id.supabase.co
   SUPABASE_ANON_KEY=tu-anon-key
   SUPABASE_SERVICE_KEY=tu-service-role-key
   ```
4. Instala dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Ejecuta el servidor:
   ```bash
   python main.py
   ```

### 4. Configurar Frontend

1. Ve al directorio `frontend/`
2. Copia `env.example` como `.env`:
   ```bash
   cp env.example .env
   ```
3. Edita `.env` con tus credenciales:
   ```env
   VITE_SUPABASE_URL=https://tu-proyecto-id.supabase.co
   VITE_SUPABASE_ANON_KEY=tu-anon-key
   VITE_API_BASE_URL=http://localhost:8000
   ```
4. Instala dependencias:
   ```bash
   npm install
   ```
5. Ejecuta el servidor de desarrollo:
   ```bash
   npm run dev
   ```

## 👥 Flujo de Usuario

### 1. Registro
- Los usuarios se registran con email y contraseña
- Inicialmente tienen rol "pendiente"
- No pueden acceder al sistema hasta que se les asigne un rol

### 2. Asignación de Roles
- El superusuario accede al "Panel de Admin"
- Puede asignar roles: "anciano", "siervo" o "pendiente"
- Puede marcar usuarios como superusuarios

### 3. Uso del Sistema
- **Ancianos**: Pueden crear, editar y eliminar publicadores
- **Siervos**: Pueden ver publicadores
- **Superusuarios**: Acceso completo + panel de administración

## 🔧 Estructura del Proyecto

```
jw_project/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── requirements.txt     # Dependencias Python
│   └── .env                 # Variables de entorno
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Componente principal
│   │   ├── components/
│   │   │   ├── Auth.vue     # Autenticación
│   │   │   ├── AdminPanel.vue # Panel de admin
│   │   │   └── Statistics.vue # Estadísticas
│   │   └── supabase.js      # Configuración Supabase
│   ├── package.json
│   └── .env                 # Variables de entorno
└── README.md
```

## 🚀 Uso

1. **Iniciar Backend**: `cd backend && python main.py`
2. **Iniciar Frontend**: `cd frontend && npm run dev`
3. **Acceder**: http://localhost:5173

## 🔐 Seguridad

- Autenticación JWT con Supabase
- Row Level Security (RLS) en PostgreSQL
- Validación de roles en backend y frontend
- Tokens de acceso seguros

## 🎨 Características de UI/UX

- Modo oscuro/claro
- Diseño responsive
- Animaciones suaves
- Feedback visual inmediato
- Validación de formularios

## 📊 Estadísticas

- Gráfico de distribución por grupos
- Contador de precursores
- Estadísticas de ánimo
- Visualización con Chart.js

## 🐛 Solución de Problemas

### Error de CORS
- Verifica que las URLs en el backend coincidan con el frontend
- Asegúrate de que el puerto 8000 esté disponible

### Error de Autenticación
- Verifica las credenciales de Supabase en `.env`
- Asegúrate de que las políticas RLS estén configuradas correctamente

### Error de Base de Datos
- Verifica que las tablas existan en Supabase
- Revisa los logs del backend para errores específicos

## 📝 Notas

- Los usuarios con rol "pendiente" no pueden acceder al sistema
- Solo los superusuarios pueden asignar roles
- Los tokens JWT se renuevan automáticamente
- Los datos se sincronizan en tiempo real con Supabase

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. 