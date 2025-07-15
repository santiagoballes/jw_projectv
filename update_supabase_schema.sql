-- Actualizar el esquema de la tabla publicadores para permitir números grandes
-- Ejecuta este comando en el SQL Editor de Supabase

-- Cambiar el tipo de dato del campo numero de integer a text
ALTER TABLE publicadores 
ALTER COLUMN numero TYPE TEXT;

-- Verificar que el cambio se aplicó correctamente
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'publicadores' AND column_name = 'numero';

-- ========================================
-- NUEVAS TABLAS PARA SISTEMA DE TERRITORIOS
-- ========================================

-- 1. Actualizar tabla usuarios para incluir rol "publicador"
ALTER TABLE usuarios 
ADD CONSTRAINT check_roles 
CHECK (rol IN ('anciano', 'siervo', 'publicador', 'pendiente'));

-- 2. Crear tabla territorios
CREATE TABLE territorios (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  geojson_data JSONB NOT NULL, -- Polígono del territorio en formato GeoJSON
  estado TEXT DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'en_revision')),
  asignado_a UUID REFERENCES usuarios(id),
  fecha_asignacion TIMESTAMP WITH TIME ZONE,
  ultima_visita TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Crear tabla ubicaciones (GPS en tiempo real)
CREATE TABLE ubicaciones (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  latitud DECIMAL(10, 8) NOT NULL,
  longitud DECIMAL(11, 8) NOT NULL,
  precision_gps DECIMAL(5, 2), -- Precisión del GPS en metros
  velocidad DECIMAL(5, 2), -- Velocidad en km/h (opcional)
  direccion TEXT, -- Dirección calculada (opcional)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Crear tabla marcaciones (casas predicadas)
CREATE TABLE marcaciones (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  territorio_id UUID REFERENCES territorios(id) ON DELETE CASCADE,
  latitud DECIMAL(10, 8) NOT NULL,
  longitud DECIMAL(11, 8) NOT NULL,
  tipo TEXT NOT NULL CHECK (tipo IN ('predicacion', 'revisita', 'estudio')),
  observaciones TEXT,
  direccion TEXT, -- Dirección de la casa
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Índice para ubicaciones por usuario y fecha
CREATE INDEX idx_ubicaciones_usuario_fecha ON ubicaciones(usuario_id, created_at DESC);

-- Índice para marcaciones por territorio
CREATE INDEX idx_marcaciones_territorio ON marcaciones(territorio_id);

-- Índice para marcaciones por usuario
CREATE INDEX idx_marcaciones_usuario ON marcaciones(usuario_id);

-- Índice para territorios por estado
CREATE INDEX idx_territorios_estado ON territorios(estado);

-- ========================================
-- HABILITAR RLS (Row Level Security)
-- ========================================

ALTER TABLE territorios ENABLE ROW LEVEL SECURITY;
ALTER TABLE ubicaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE marcaciones ENABLE ROW LEVEL SECURITY;

-- ========================================
-- POLÍTICAS RLS PARA TERRITORIOS
-- ========================================

-- Todos los usuarios autenticados pueden ver territorios activos
CREATE POLICY "Usuarios pueden ver territorios activos" ON territorios
  FOR SELECT USING (
    estado = 'activo' AND
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- Ancianos y superusuarios pueden gestionar territorios
CREATE POLICY "Ancianos pueden gestionar territorios" ON territorios
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND (rol = 'anciano' OR is_superuser = true)
    )
  );

-- ========================================
-- POLÍTICAS RLS PARA UBICACIONES
-- ========================================

-- Usuarios pueden ver ubicaciones de otros publicadores
CREATE POLICY "Usuarios pueden ver ubicaciones" ON ubicaciones
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- Usuarios pueden insertar su propia ubicación
CREATE POLICY "Usuarios pueden insertar su ubicación" ON ubicaciones
  FOR INSERT WITH CHECK (
    usuario_id = auth.uid() AND
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- ========================================
-- POLÍTICAS RLS PARA MARCADORES
-- ========================================

-- Usuarios pueden ver marcaciones de su territorio
CREATE POLICY "Usuarios pueden ver marcaciones" ON marcaciones
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- Usuarios pueden crear marcaciones
CREATE POLICY "Usuarios pueden crear marcaciones" ON marcaciones
  FOR INSERT WITH CHECK (
    usuario_id = auth.uid() AND
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- Usuarios pueden editar sus propias marcaciones
CREATE POLICY "Usuarios pueden editar sus marcaciones" ON marcaciones
  FOR UPDATE USING (
    usuario_id = auth.uid() AND
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id = auth.uid() AND rol IN ('anciano', 'siervo', 'publicador')
    )
  );

-- ========================================
-- FUNCIONES AUXILIARES
-- ========================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_territorios_updated_at 
    BEFORE UPDATE ON territorios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ========================================

-- Insertar un territorio de ejemplo (polígono simple)
INSERT INTO territorios (nombre, descripcion, geojson_data) VALUES (
  'Territorio Centro',
  'Área central de la ciudad',
  '{
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-74.006, 40.7128],
        [-74.006, 40.7228],
        [-73.996, 40.7228],
        [-73.996, 40.7128],
        [-74.006, 40.7128]
      ]]
    },
    "properties": {
      "name": "Territorio Centro"
    }
  }'::jsonb
); 