<template>
  <div class="container" :data-theme="currentTheme">
    <!-- Theme Toggle Button -->
    <button @click="toggleTheme" class="theme-toggle" :title="currentTheme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'">
      <svg v-if="currentTheme === 'light'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    </button>

    <!-- Header -->
    <div class="header">
      <h1>Sistema de Publicadores</h1>
      <p>Gestión de publicadores del Reino</p>
    </div>

    <!-- Auth Component -->
    <Auth v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

    <!-- Main Dashboard -->
    <div v-else>
      <!-- User Info -->
      <div class="card user-info-bar" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3>Bienvenido, {{ currentUser.nombre }}</h3>
          <p>
            Rol: <span class="badge badge-success">{{ currentUser.rol }}</span>
            <span v-if="currentUser.is_superuser" class="badge badge-warning">Superusuario</span>
          </p>
        </div>
        <div style="display: flex; align-items: center; gap: 18px;">
          <div v-if="currentUser.rol === 'anciano' || currentUser.rol === 'siervo' || currentUser.is_superuser">
            <Notificaciones :user="currentUser" :token="accessToken" />
          </div>
          <button @click="logout" class="btn btn-danger">Cerrar Sesión</button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="card">
        <div class="nav-tabs">
          <button 
            @click="currentView = 'dashboard'" 
            :class="['nav-tab', { 'active': currentView === 'dashboard' }]"
          >
            📊 Dashboard
          </button>
        </div>
      </div>

      <!-- Dashboard View (solo dashboard, sin mapa) -->
      <div v-if="currentView === 'dashboard'">
        <!-- Restrict access for publicadores -->
        <div v-if="currentUser.rol === 'publicador'" class="card">
          <div class="alert alert-warning">
            <h3>Acceso Restringido</h3>
            <p>Como publicador, solo tienes acceso a la información básica. Los ancianos y siervos pueden acceder a las funciones administrativas.</p>
          </div>
        </div>

        <!-- Admin content for ancianos, siervos and superusuarios -->
        <div v-else>
          <!-- Alerts -->
          <div v-if="alert.show" :class="['alert', `alert-${alert.type}`]">
            {{ alert.message }}
          </div>

          <!-- Add Publisher Button -->
          <div class="card">
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
              <button 
                v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" 
                @click="showAddModal = true" 
                class="btn btn-primary"
              >
                Agregar Publicador
              </button>
              <button @click="showStats = !showStats" class="btn btn-success">
                {{ showStats ? 'Ocultar' : 'Mostrar' }} Estadísticas
              </button>
              <button 
                v-if="currentUser.is_superuser" 
                @click="showAdminPanel = !showAdminPanel" 
                class="btn btn-warning"
              >
                {{ showAdminPanel ? 'Ocultar' : 'Mostrar' }} Panel de Admin
              </button>
            </div>
          </div>

          <!-- Admin Panel -->
          <div v-if="showAdminPanel && currentUser.is_superuser" class="card">
            <AdminPanel />
          </div>

          <!-- Statistics Section -->
          <div v-if="showStats" class="card">
            <Statistics :publicadores="publicadores" />
          </div>

          <!-- Publishers List -->
          <div class="card">
            <h3>Lista de Publicadores</h3>
        
        <!-- Buscador y Filtros -->
        <div class="search-section">
          <div class="search-row">
            <div class="form-group">
              <label for="searchNombre">Buscar por nombre:</label>
              <input
                type="text"
                id="searchNombre"
                v-model="filters.nombre"
                class="form-control"
                placeholder="Escriba el nombre..."
              />
            </div>
            <div class="form-group">
              <label for="searchGrupo">Filtrar por grupo:</label>
              <select id="searchGrupo" v-model="filters.grupo" class="form-control">
                <option value="">Todos los grupos</option>
                <option v-for="grupo in gruposDisponibles" :key="grupo" :value="grupo">
                  Grupo {{ grupo }}
                </option>
              </select>
            </div>
          </div>
          <div class="search-row">
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="filters.precursor"
                />
                Solo precursores
              </label>
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="filters.animo"
                />
                Solo con ánimo
              </label>
            </div>
            <div class="form-group">
              <button @click="clearFilters" class="btn btn-danger">
                Limpiar Filtros
              </button>
            </div>
          </div>
        </div>

        <!-- Contador de resultados -->
        <div class="results-info">
          <p>Mostrando {{ publicadoresFiltrados.length }} de {{ publicadores.length }} publicadores</p>
          <p v-if="publicadoresFiltrados.length > 10">Página {{ currentPage }} de {{ totalPages }}</p>
        </div>

        <!-- Sección prioritaria para grupo asignado -->
        <div v-if="currentUser.grupo_asignado && (currentUser.rol === 'anciano' || currentUser.rol === 'siervo')">
          <h4 style="color: #2980b9; margin-top: 18px;">Tu grupo asignado (Grupo {{ currentUser.grupo_asignado }})</h4>
          <div class="publicadores-grid">
            <div v-for="publicador in publicadoresFiltrados.filter(p => p.grupo === currentUser.grupo_asignado)" :key="publicador.id" class="publicador-card destacado">
              <h4>{{ publicador.nombre }}</h4>
              <p><strong>Número:</strong> {{ publicador.numero }}</p>
              <p><strong>Grupo:</strong> {{ publicador.grupo }}</p>
              <div style="margin: 8px 0;">
                <span v-if="publicador.precursor" class="badge badge-success">Precursor</span>
                <span v-if="publicador.animo" class="badge badge-warning">Ánimo</span>
              </div>
              <div class="actions">
                <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="editPublicador(publicador)" class="btn btn-primary">Editar</button>
                <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="deletePublicador(publicador.id)" class="btn btn-danger">Eliminar</button>
                <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="enviarAnimo(publicador.id)" class="btn btn-success" :disabled="publicador.animo" style="margin-left: 6px;">
                  <span v-if="!publicador.animo">Enviar ánimo por WhatsApp</span>
                  <span v-else>Ánimo enviado</span>
                </button>
              </div>
            </div>
          </div>
          <hr style="margin: 24px 0;" />
        </div>
        <!-- Resto de publicadores -->
        <h4 v-if="currentUser.grupo_asignado && (currentUser.rol === 'anciano' || currentUser.rol === 'siervo')">Otros publicadores</h4>
        <div class="publicadores-grid">
          <div v-for="publicador in publicadoresFiltrados.filter(p => !currentUser.grupo_asignado || p.grupo !== currentUser.grupo_asignado)" :key="publicador.id" class="publicador-card">
            <h4>{{ publicador.nombre }}</h4>
            <p><strong>Número:</strong> {{ publicador.numero }}</p>
            <p><strong>Grupo:</strong> {{ publicador.grupo }}</p>
            <div style="margin: 8px 0;">
              <span v-if="publicador.precursor" class="badge badge-success">Precursor</span>
              <span v-if="publicador.animo" class="badge badge-warning">Ánimo</span>
            </div>
            <div class="actions">
              <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="editPublicador(publicador)" class="btn btn-primary">Editar</button>
              <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="deletePublicador(publicador.id)" class="btn btn-danger">Eliminar</button>
              <button v-if="currentUser.rol === 'anciano' || currentUser.is_superuser" @click="enviarAnimo(publicador.id)" class="btn btn-success" :disabled="publicador.animo" style="margin-left: 6px;">
                <span v-if="!publicador.animo">Enviar ánimo por WhatsApp</span>
                <span v-else>Ánimo enviado</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="goToPage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="btn btn-primary"
        >
          ← Anterior
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="goToPage(page)"
            :class="['btn', page === currentPage ? 'btn-primary' : 'btn-secondary']"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="goToPage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="btn btn-primary"
        >
          Siguiente →
        </button>
      </div>

      <!-- Mensaje cuando no hay resultados -->
      <div v-if="publicadoresFiltrados.length === 0 && publicadores.length > 0" class="no-results">
        <p>No se encontraron publicadores con los filtros aplicados.</p>
      </div>

      <!-- Add/Edit Modal -->
      <div v-if="showAddModal || showEditModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ showEditModal ? 'Editar' : 'Agregar' }} Publicador</h3>
            <button @click="closeModal" class="close">&times;</button>
          </div>
          <form @submit.prevent="showEditModal ? updatePublicador() : addPublicador()">
            <div class="form-group">
              <label for="nombre">Nombre:</label>
              <input
                type="text"
                id="nombre"
                v-model="publicadorForm.nombre"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label for="numero">Número:</label>
              <input
                type="text"
                id="numero"
                v-model="publicadorForm.numero"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label for="grupo">Grupo:</label>
              <input
                type="number"
                id="grupo"
                v-model="publicadorForm.grupo"
                class="form-control"
                required
              />
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="publicadorForm.precursor"
                />
                Precursor
              </label>
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  v-model="publicadorForm.animo"
                />
                Ánimo
              </label>
            </div>
            <div style="display: flex; gap: 10px;">
              <button type="submit" class="btn btn-primary">
                {{ showEditModal ? 'Actualizar' : 'Agregar' }}
              </button>
              <button type="button" @click="closeModal" class="btn btn-danger">
                Cancelar
              </button>
            </div>
          </form>
          </div> <!-- Cierre del modal-content -->
        </div> <!-- Cierre del modal -->
          </div> <!-- Cierre del div v-else para contenido administrativo -->
        </div> <!-- Cierre del div v-if="currentView === 'dashboard'" -->
      </div> <!-- Cierre del div v-else para el dashboard principal -->
  </div>
</template>

<script>
import axios from 'axios'
import Statistics from './components/Statistics.vue'
import Auth from './components/Auth.vue'
import AdminPanel from './components/AdminPanel.vue'
import Notificaciones from './components/Notificaciones.vue'
import { supabase } from './supabase.js'

// Configurar axios para usar la URL directa del backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default {
  name: 'App',
  components: {
    Statistics,
    Auth,
    AdminPanel,
    Notificaciones,
  },
  data() {
    return {
      isLoggedIn: false,
      currentUser: null,
      publicadores: [],
      publicadorForm: {
        nombre: '',
        numero: '',
        grupo: '',
        precursor: false,
        animo: false
      },
      showAddModal: false,
      showEditModal: false,
      editingPublicadorId: null,
      alert: {
        show: false,
        type: 'info',
        message: ''
      },
      filters: {
        nombre: '',
        grupo: '',
        precursor: false,
        animo: false
      },
      currentPage: 1,
      itemsPerPage: 10,
      showStats: false,
      showAdminPanel: false,
      currentTheme: 'light',
      accessToken: '',
      currentView: 'dashboard' // 'dashboard' or 'map'
    }
  },
  computed: {
    gruposDisponibles() {
      const grupos = new Set(this.publicadores.map(p => p.grupo));
      return Array.from(grupos).sort((a, b) => a - b);
    },
    publicadoresFiltrados() {
      let filtered = this.publicadores;

      if (this.filters.nombre) {
        filtered = filtered.filter(p => p.nombre.toLowerCase().includes(this.filters.nombre.toLowerCase()));
      }

      if (this.filters.grupo) {
        filtered = filtered.filter(p => p.grupo === this.filters.grupo);
      }

      if (this.filters.precursor) {
        filtered = filtered.filter(p => p.precursor);
      }

      if (this.filters.animo) {
        filtered = filtered.filter(p => p.animo);
      }

      return filtered;
    },
    publicadoresPaginados() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.publicadoresFiltrados.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.publicadoresFiltrados.length / this.itemsPerPage);
    },
    visiblePages() {
      const totalPages = this.totalPages;
      const currentPage = this.currentPage;
      const maxVisiblePages = 5;

      if (totalPages <= maxVisiblePages) {
        return Array.from({ length: totalPages }, (_, i) => i + 1);
      }

      let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
      let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }

      return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
    }
  },
  async mounted() {
    // Initialize theme
    this.initializeTheme()
    
    // Check if user is logged in with Supabase
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
      await this.handleLoginSuccess({
        user: session.user,
        session: session,
        userData: JSON.parse(localStorage.getItem('userData') || '{}')
      })
    }
  },
  methods: {
    async handleLoginSuccess({ user, session, userData }) {
      try {
        // Guardar datos del usuario
        this.currentUser = userData
        this.isLoggedIn = true
        this.accessToken = session.access_token;
        
        // Guardar en localStorage
        localStorage.setItem('userData', JSON.stringify(userData))
        
        // Configurar axios para usar el token de Supabase
        axios.defaults.headers.common['Authorization'] = `Bearer ${session.access_token}`
        
        // Load publicadores
        await this.loadPublicadores()
        
        this.showAlert('success', 'Sesión iniciada correctamente')
      } catch (error) {
        console.error('Error en handleLoginSuccess:', error)
        this.showAlert('error', 'Error al cargar datos del usuario')
      }
    },
    
    async logout() {
      try {
        await supabase.auth.signOut()
        localStorage.removeItem('userData')
        this.isLoggedIn = false
        this.currentUser = null
        this.publicadores = []
        delete axios.defaults.headers.common['Authorization']
        this.showAlert('info', 'Sesión cerrada')
        this.accessToken = '';
      } catch (error) {
        console.error('Error en logout:', error)
        this.showAlert('error', 'Error al cerrar sesión')
      }
    },
    
    async loadPublicadores() {
      try {
        const response = await axios.get(`${API_BASE_URL}/publicadores`)
        this.publicadores = response.data
      } catch (error) {
        console.error('Error al cargar publicadores:', error)
        this.showAlert('error', 'Error al cargar publicadores: ' + error.response?.data?.detail || error.message)
      }
    },
    
    async addPublicador() {
      try {
        const response = await axios.post(`${API_BASE_URL}/publicadores`, this.publicadorForm)
        
        this.publicadores.push(response.data)
        this.closeModal()
        this.showAlert('success', 'Publicador agregado correctamente')
      } catch (error) {
        console.error('Error al agregar publicador:', error)
        this.showAlert('error', 'Error al agregar publicador: ' + error.response?.data?.detail || error.message)
      }
    },
    
    editPublicador(publicador) {
      this.publicadorForm = { ...publicador }
      this.editingPublicadorId = publicador.id
      this.showEditModal = true
    },
    
    async updatePublicador() {
      try {
        const response = await axios.put(`${API_BASE_URL}/publicadores/${this.editingPublicadorId}`, this.publicadorForm)
        
        const index = this.publicadores.findIndex(p => p.id === this.editingPublicadorId)
        if (index !== -1) {
          this.publicadores[index] = response.data
        }
        
        this.closeModal()
        this.showAlert('success', 'Publicador actualizado correctamente')
      } catch (error) {
        console.error('Error al actualizar publicador:', error)
        this.showAlert('error', 'Error al actualizar publicador: ' + error.response?.data?.detail || error.message)
      }
    },
    
    async deletePublicador(id) {
      if (!confirm('¿Estás seguro de que quieres eliminar este publicador?')) {
        return
      }
      
      try {
        await axios.delete(`${API_BASE_URL}/publicadores/${id}`)
        
        this.publicadores = this.publicadores.filter(p => p.id !== id)
        this.showAlert('success', 'Publicador eliminado correctamente')
      } catch (error) {
        console.error('Error al eliminar publicador:', error)
        this.showAlert('error', 'Error al eliminar publicador: ' + error.response?.data?.detail || error.message)
      }
    },
    
    closeModal() {
      this.showAddModal = false
      this.showEditModal = false
      this.editingPublicadorId = null
      this.publicadorForm = {
        nombre: '',
        numero: '',
        grupo: '',
        precursor: false,
        animo: false
      }
    },
    
    showAlert(type, message) {
      this.alert = {
        show: true,
        type,
        message
      }
      setTimeout(() => {
        this.alert.show = false
      }, 5000)
    },

    clearFilters() {
      this.filters = {
        nombre: '',
        grupo: '',
        precursor: false,
        animo: false
      };
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },

    initializeTheme() {
      // Check for saved theme preference or default to 'light'
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        this.currentTheme = savedTheme
      } else {
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          this.currentTheme = 'dark'
        } else {
          this.currentTheme = 'light'
        }
      }
    },

    toggleTheme() {
      this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', this.currentTheme)
    },

    async enviarAnimo(publicadorId) {
      try {
        const publicador = this.publicadores.find(p => p.id === publicadorId);
        if (!publicador) {
          this.showAlert('danger', 'No se encontró el publicador');
          return;
        }
        let numero = String(publicador.numero).replace(/[^\d]/g, '');
        if (numero.length === 10) {
          numero = '57' + numero;
        }
        const mensaje = encodeURIComponent('¡Hola ' + publicador.nombre + '! Solo quería enviarte un saludo y desearte un excelente día.');
        const isMobile = /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(navigator.userAgent);
        const waUrl = isMobile
          ? `whatsapp://send?phone=${numero}&text=${mensaje}`
          : `https://wa.me/${numero}?text=${mensaje}`;
        window.open(waUrl, '_blank');
        this.showAlert('success', 'Enlace de WhatsApp abierto');
      } catch (e) {
        this.showAlert('danger', 'Error al abrir WhatsApp');
      }
    }
  },
  watch: {
    publicadoresFiltrados: {
      handler() {
        // Reset to first page when filters change
        this.currentPage = 1;
      },
      immediate: true
    }
  }
}
</script>

<style>
:root {
  /* Light theme variables */
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --secondary-color: #6b7280;
  --secondary-hover: #4b5563;
  --success-color: #10b981;
  --success-hover: #059669;
  --warning-color: #f59e0b;
  --warning-hover: #d97706;
  --danger-color: #ef4444;
  --danger-hover: #dc2626;
  --info-color: #3b82f6;
  --info-hover: #2563eb;
  
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --text-white: #ffffff;
  
  --border-color: #e5e7eb;
  --input-border: #d1d5db;
  --input-focus-border: #6366f1;
  --input-bg: #ffffff;
  --input-placeholder: #9ca3af;
  
  --card-bg: #ffffff;
  --card-hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  
  --badge-success-bg: #d1fae5;
  --badge-success-text: #065f46;
  --badge-warning-bg: #fef3c7;
  --badge-warning-text: #92400e;
  --badge-error-bg: #fee2e2;
  --badge-error-text: #991b1b;
  
  --alert-success-bg: #d1fae5;
  --alert-success-text: #065f46;
  --alert-success-border: #a7f3d0;
  --alert-error-bg: #fee2e2;
  --alert-error-text: #991b1b;
  --alert-error-border: #fca5a5;
  --alert-info-bg: #dbeafe;
  --alert-info-text: #1e40af;
  --alert-info-border: #93c5fd;
  
  --transition: all 0.3s ease;
}

[data-theme="dark"] {
  /* Dark theme variables */
  --bg-primary: #1f2937;
  --bg-secondary: #111827;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-muted: #9ca3af;
  --text-white: #ffffff;
  
  --border-color: #374151;
  --input-border: #4b5563;
  --input-focus-border: #6366f1;
  --input-bg: #374151;
  --input-placeholder: #6b7280;
  
  --card-bg: #374151;
  --card-hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
  
  --badge-success-bg: #065f46;
  --badge-success-text: #d1fae5;
  --badge-warning-bg: #92400e;
  --badge-warning-text: #fef3c7;
  --badge-error-bg: #991b1b;
  --badge-error-text: #fee2e2;
  
  --alert-success-bg: #065f46;
  --alert-success-text: #d1fae5;
  --alert-success-border: #047857;
  --alert-error-bg: #991b1b;
  --alert-error-text: #fee2e2;
  --alert-error-border: #dc2626;
  --alert-info-bg: #1e40af;
  --alert-info-text: #dbeafe;
  --alert-info-border: #3b82f6;
}

/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: var(--transition);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

/* Button styles */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary {
  background: var(--primary-color);
  color: var(--text-white);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--secondary-color);
  color: var(--text-white);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--secondary-hover);
}

.btn-success {
  background: var(--success-color);
  color: var(--text-white);
}

.btn-success:hover:not(:disabled) {
  background: var(--success-hover);
}

.btn-warning {
  background: var(--warning-color);
  color: var(--text-white);
}

.btn-warning:hover:not(:disabled) {
  background: var(--warning-hover);
}

.btn-danger {
  background: var(--danger-color);
  color: var(--text-white);
}

.btn-danger:hover:not(:disabled) {
  background: var(--danger-hover);
}

/* Badge styles */
.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: var(--badge-success-bg);
  color: var(--badge-success-text);
}

.badge-warning {
  background: var(--badge-warning-bg);
  color: var(--badge-warning-text);
}

.badge-error {
  background: var(--badge-error-bg);
  color: var(--badge-error-text);
}

/* Alert styles */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid;
}

.alert-success {
  background: var(--alert-success-bg);
  color: var(--alert-success-text);
  border-color: var(--alert-success-border);
}

.alert-error {
  background: var(--alert-error-bg);
  color: var(--alert-error-text);
  border-color: var(--alert-error-border);
}

.alert-info {
  background: var(--alert-info-bg);
  color: var(--alert-info-text);
  border-color: var(--alert-info-border);
}

.user-info-bar {
  margin-bottom: 18px;
  background: var(--card-bg, #fff);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 18px 24px;
}

.publicador-card.destacado {
  border: 2px solid #2980b9;
  background: #eaf1fb;
  box-shadow: 0 2px 8px rgba(41,128,185,0.08);
}

/* Navigation tabs */
.nav-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.nav-tab {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 2px solid transparent;
}

.nav-tab:hover {
  background: var(--card-bg);
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--primary-color);
  color: var(--text-white);
  border-color: var(--primary-color);
}

/* Map container styles */
.map-container {
  height: calc(100vh - 200px);
  min-height: 500px;
}
</style> 