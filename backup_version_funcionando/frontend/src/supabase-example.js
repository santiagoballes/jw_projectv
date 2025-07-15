// Ejemplo de cómo conectar Vue.js directamente a Supabase
// Este archivo muestra cómo usar Supabase desde el frontend sin pasar por FastAPI

import { createClient } from '@supabase/supabase-js'

// Configuración de Supabase
const supabaseUrl = 'https://tu-proyecto.supabase.co'
const supabaseKey = 'tu-anon-key' // Usa la anon key, NO la service role key

export const supabase = createClient(supabaseUrl, supabaseKey)

// Ejemplos de uso en componentes Vue:

// 1. Obtener todos los publicadores
export async function getPublicadores() {
  const { data, error } = await supabase
    .from('publicadores')
    .select('*')
    .order('nombre')
  
  if (error) {
    console.error('Error al obtener publicadores:', error)
    throw error
  }
  
  return data
}

// 2. Obtener publicadores por grupo
export async function getPublicadoresPorGrupo(grupo) {
  const { data, error } = await supabase
    .from('publicadores')
    .select('*')
    .eq('grupo', grupo)
    .order('nombre')
  
  if (error) {
    console.error('Error al obtener publicadores del grupo:', error)
    throw error
  }
  
  return data
}

// 3. Obtener solo precursores
export async function getPrecursores() {
  const { data, error } = await supabase
    .from('publicadores')
    .select('*')
    .eq('precursor', true)
    .order('nombre')
  
  if (error) {
    console.error('Error al obtener precursores:', error)
    throw error
  }
  
  return data
}

// 4. Insertar un nuevo publicador
export async function crearPublicador(publicador) {
  const { data, error } = await supabase
    .from('publicadores')
    .insert([{
      nombre: publicador.nombre,
      numero: publicador.numero,
      grupo: publicador.grupo,
      precursor: publicador.precursor,
      animo: publicador.animo
    }])
    .select()
  
  if (error) {
    console.error('Error al crear publicador:', error)
    throw error
  }
  
  return data[0]
}

// 5. Actualizar un publicador
export async function actualizarPublicador(id, cambios) {
  const { data, error } = await supabase
    .from('publicadores')
    .update(changes)
    .eq('id', id)
    .select()
  
  if (error) {
    console.error('Error al actualizar publicador:', error)
    throw error
  }
  
  return data[0]
}

// 6. Eliminar un publicador
export async function eliminarPublicador(id) {
  const { error } = await supabase
    .from('publicadores')
    .delete()
    .eq('id', id)
  
  if (error) {
    console.error('Error al eliminar publicador:', error)
    throw error
  }
  
  return true
}

// 7. Búsqueda de publicadores
export async function buscarPublicadores(termino) {
  const { data, error } = await supabase
    .from('publicadores')
    .select('*')
    .ilike('nombre', `%${termino}%`)
    .order('nombre')
  
  if (error) {
    console.error('Error al buscar publicadores:', error)
    throw error
  }
  
  return data
}

// 8. Estadísticas
export async function obtenerEstadisticas() {
  const { data, error } = await supabase
    .from('publicadores')
    .select('*')
  
  if (error) {
    console.error('Error al obtener estadísticas:', error)
    throw error
  }
  
  const total = data.length
  const precursores = data.filter(p => p.precursor).length
  const conAnimo = data.filter(p => p.animo).length
  
  // Agrupar por grupo
  const porGrupo = data.reduce((acc, p) => {
    acc[p.grupo] = (acc[p.grupo] || 0) + 1
    return acc
  }, {})
  
  return {
    total,
    precursores,
    conAnimo,
    porGrupo
  }
}

// Ejemplo de uso en un componente Vue:
/*
<template>
  <div>
    <h2>Publicadores</h2>
    <div v-for="publicador in publicadores" :key="publicador.id">
      {{ publicador.nombre }} - Grupo {{ publicador.grupo }}
    </div>
  </div>
</template>

<script>
import { getPublicadores, crearPublicador } from './supabase-example.js'

export default {
  data() {
    return {
      publicadores: []
    }
  },
  async mounted() {
    try {
      this.publicadores = await getPublicadores()
    } catch (error) {
      console.error('Error:', error)
    }
  },
  methods: {
    async agregarPublicador(nuevoPublicador) {
      try {
        const publicador = await crearPublicador(nuevoPublicador)
        this.publicadores.push(publicador)
      } catch (error) {
        console.error('Error al agregar:', error)
      }
    }
  }
}
</script>
*/

// Configuración de Row Level Security (RLS) en Supabase:
/*
Para usar RLS y controlar acceso basado en autenticación:

1. Habilitar RLS en las tablas:
   ALTER TABLE publicadores ENABLE ROW LEVEL SECURITY;

2. Crear políticas para permitir acceso:
   -- Permitir lectura a todos los usuarios autenticados
   CREATE POLICY "Usuarios autenticados pueden leer publicadores" 
   ON publicadores FOR SELECT 
   TO authenticated 
   USING (true);

   -- Permitir inserción solo a ancianos
   CREATE POLICY "Solo ancianos pueden crear publicadores" 
   ON publicadores FOR INSERT 
   TO authenticated 
   WITH CHECK (
     EXISTS (
       SELECT 1 FROM usuarios 
       WHERE usuarios.id = auth.uid() 
       AND usuarios.rol = 'anciano'
     )
   );

   -- Permitir actualización a ancianos y siervos
   CREATE POLICY "Ancianos y siervos pueden actualizar publicadores" 
   ON publicadores FOR UPDATE 
   TO authenticated 
   USING (
     EXISTS (
       SELECT 1 FROM usuarios 
       WHERE usuarios.id = auth.uid() 
       AND usuarios.rol IN ('anciano', 'siervo')
     )
   );

   -- Permitir eliminación solo a ancianos
   CREATE POLICY "Solo ancianos pueden eliminar publicadores" 
   ON publicadores FOR DELETE 
   TO authenticated 
   USING (
     EXISTS (
       SELECT 1 FROM usuarios 
       WHERE usuarios.id = auth.uid() 
       AND usuarios.rol = 'anciano'
     )
   );
*/ 