// Configuración de Supabase para el frontend
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://medhsyunymqxbzhxfsny.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lZGhzeXVueW1xeGJ6aHhmc255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE5NDE1ODcsImV4cCI6MjA2NzUxNzU4N30.B_kxneX-65d47lDalDm-Ddj0olNJk_7MwtODhQVl1mE'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Funciones para usar Supabase directamente desde Vue.js
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

export async function actualizarPublicador(id, cambios) {
  const { data, error } = await supabase
    .from('publicadores')
    .update(cambios)
    .eq('id', id)
    .select()
  
  if (error) {
    console.error('Error al actualizar publicador:', error)
    throw error
  }
  
  return data[0]
}

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