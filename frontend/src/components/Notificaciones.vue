<template>
  <div class="notificaciones-wrapper" @mouseleave="closeDropdown">
    <button class="noti-bell" @click="toggleDropdown" :title="dropdownOpen ? 'Cerrar notificaciones' : 'Ver notificaciones'">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="28" height="28">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <span v-if="notificaciones.length > 0" class="noti-count">{{ notificaciones.length }}</span>
    </button>
    <div v-if="dropdownOpen" class="noti-dropdown">
      <div v-if="loading" class="noti-loading">Cargando notificaciones...</div>
      <div v-else-if="notificaciones.length === 0" class="noti-empty">No hay notificaciones</div>
      <ul v-else>
        <li v-for="noti in notificaciones" :key="noti.id" class="noti-item">
          <div class="noti-row">
            <span class="noti-icon">{{ iconoTipo(noti.tipo) }}</span>
            <span class="noti-badge" :class="'tipo-' + noti.tipo">{{ traducirTipo(noti.tipo) }}</span>
            <span class="noti-fecha">{{ formatearFecha(noti.fecha_creacion) }}</span>
            <button v-if="user.is_superuser" class="noti-delete" @click="eliminarNotificacion(noti.id)" title="Eliminar notificación">
              🗑️
            </button>
          </div>
          <div class="noti-mensaje">{{ noti.mensaje }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Notificaciones',
  props: {
    user: { type: Object, required: true },
    token: { type: String, required: true }
  },
  data() {
    return {
      notificaciones: [],
      loading: false,
      dropdownOpen: false
    };
  },
  methods: {
    async fetchNotificaciones() {
      if (!this.user || !this.token) return;
      this.loading = true;
      try {
        const res = await axios.get('http://localhost:8000/notificaciones/', {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        this.notificaciones = res.data;
      } catch (e) {
        this.notificaciones = [];
      } finally {
        this.loading = false;
      }
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
      if (this.dropdownOpen) this.fetchNotificaciones();
    },
    closeDropdown() {
      this.dropdownOpen = false;
    },
    traducirTipo(tipo) {
      const map = {
        'publicador_agregado': 'Nuevo publicador',
        'publicador_editado': 'Edición de publicador',
        'publicador_eliminado': 'Eliminación de publicador',
        'rol_cambiado': 'Cambio de rol'
      };
      return map[tipo] || tipo;
    },
    formatearFecha(fecha) {
      const d = new Date(fecha);
      return d.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' });
    },
    async eliminarNotificacion(id) {
      if (!this.token) return;
      if (!confirm('¿Seguro que deseas eliminar esta notificación?')) return;
      try {
        await axios.delete(`http://localhost:8000/notificaciones/${id}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        this.notificaciones = this.notificaciones.filter(n => n.id !== id);
      } catch (e) {
        alert('Error al eliminar notificación');
      }
    },
    iconoTipo(tipo) {
      switch (tipo) {
        case 'publicador_agregado': return '✅';
        case 'publicador_editado': return '✏️';
        case 'publicador_eliminado': return '🗑️';
        case 'rol_cambiado': return '👤';
        default: return '🔔';
      }
    },
    async enviarAnimo(publicadorId) {
      try {
        const res = await axios.post(`http://localhost:8000/publicadores/${publicadorId}/mensaje-animo`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        const numero = res.data.numero.replace(/[^\d]/g, '');
        const mensaje = encodeURIComponent(res.data.mensaje);
        window.open(`https://wa.me/${numero}?text=${mensaje}`, '_blank');
        // Opcional: mostrar feedback visual
      } catch (e) {
        alert('Error al generar o enviar el mensaje de ánimo');
      }
    }
  }
};
</script>

<style scoped>
.notificaciones-wrapper {
  position: relative;
  display: inline-block;
}
.noti-bell {
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
  padding: 0;
}
.noti-count {
  position: absolute;
  top: 0;
  right: 0;
  background: #e74c3c;
  color: #fff;
  border-radius: 50%;
  font-size: 0.8em;
  padding: 2px 6px;
  min-width: 18px;
  text-align: center;
}
.noti-dropdown {
  position: absolute;
  right: 0;
  top: 36px;
  background: var(--card-bg, #fff);
  color: var(--text-color, #222);
  border: 1px solid #ccc;
  border-radius: 8px;
  min-width: 260px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 100;
  max-height: 350px;
  overflow-y: auto;
  animation: fadeIn 0.25s;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.noti-item {
  background: var(--noti-bg, #f7fafd);
  border-radius: 10px;
  margin: 10px 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  padding: 10px 12px 8px 12px;
  border-bottom: none;
  display: flex;
  flex-direction: column;
  transition: background 0.2s;
}
.noti-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.noti-icon {
  font-size: 1.2em;
  margin-right: 2px;
}
.noti-badge {
  font-size: 0.93em;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 8px;
  margin-right: 6px;
  background: #eaf1fb;
  color: #2980b9;
  letter-spacing: 0.5px;
}
.noti-badge.tipo-publicador_agregado { background: #eafbe7; color: #27ae60; }
.noti-badge.tipo-publicador_editado { background: #fffbe7; color: #f39c12; }
.noti-badge.tipo-publicador_eliminado { background: #fdeaea; color: #e74c3c; }
.noti-badge.tipo-rol_cambiado { background: #eaf1fb; color: #2980b9; }
.noti-mensaje {
  margin-left: 28px;
  font-size: 0.98em;
  color: #333;
  margin-top: 2px;
}
.noti-fecha {
  font-size: 0.85em;
  color: #888;
  margin-left: auto;
  margin-right: 4px;
}
.noti-loading, .noti-empty {
  padding: 16px;
  text-align: center;
  color: #888;
}
.noti-delete {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 1.1em;
  cursor: pointer;
  margin-left: 8px;
  align-self: flex-end;
  transition: color 0.2s;
}
.noti-delete:hover {
  color: #c0392b;
}
</style> 