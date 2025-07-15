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

    <!-- Login Form -->
    <div v-if="!isLoggedIn" class="card login-form">
      <h2>Iniciar Sesión</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">Nombre de Usuario:</label>
          <input
            type="text"
            id="username"
            v-model="loginForm.username"
            class="form-control"
            required
          />
        </div>
        <div class="form-group">
          <label for="rol">Rol:</label>
          <select id="rol" v-model="loginForm.rol" class="form-control" required>
            <option value="">Seleccionar rol</option>
            <option value="anciano">Anciano</option>
            <option value="siervo">Siervo</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%">
          Iniciar Sesión
        </button>
      </form>
    </div>

    <!-- Main Dashboard -->
    <div v-else>
      <!-- User Info -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h3>Bienvenido, {{ currentUser.nombre }}</h3>
            <p>Rol: <span class="badge badge-success">{{ currentUser.rol }}</span></p>
          </div>
          <button @click="logout" class="btn btn-danger">Cerrar Sesión</button>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="alert.show" :class="['alert', `alert-${alert.type}`]">
        {{ alert.message }}
      </div>

      <!-- Add Publisher Button -->
      <div class="card">
        <div style="display: flex; gap: 10px; align-items: center;">
          <button 
            v-if="currentUser.rol === 'anciano'" 
            @click="showAddModal = true" 
            class="btn btn-primary"
          >
            Agregar Publicador
          </button>
          <button @click="showStats = !showStats" class="btn btn-success">
            {{ showStats ? 'Ocultar' : 'Mostrar' }} Estadísticas
          </button>
        </div>
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
                Limpiar filtros
              </button>
            </div>
          </div>
        </div>

        <!-- Contador de resultados -->
        <div class="results-info">
          <p>Mostrando {{ publicadoresFiltrados.length }} de {{ publicadores.length }} publicadores</p>
          <p v-if="publicadoresFiltrados.length > 10">Página {{ currentPage }} de {{ totalPages }}</p>
        </div>

        <div class="publicadores-grid">
          <div v-for="publicador in publicadoresPaginados" :key="publicador.id" class="publicador-card">
            <h4>{{ publicador.nombre }}</h4>
            <p><strong>Número:</strong> {{ publicador.numero }}</p>
            <p><strong>Grupo:</strong> {{ publicador.grupo }}</p>
            <div style="margin: 8px 0;">
              <span v-if="publicador.precursor" class="badge badge-success">Precursor</span>
              <span v-if="publicador.animo" class="badge badge-warning">Ánimo</span>
            </div>
            <div class="actions">
              <button @click="editPublicador(publicador)" class="btn btn-primary">
                Editar
              </button>
              <button 
                v-if="currentUser.rol === 'anciano'" 
                @click="deletePublicador(publicador.id)" 
                class="btn btn-danger"
              >
                Eliminar
              </button>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Statistics from './components/Statistics.vue'

// Configurar axios para usar la URL directa del backend
const API_BASE_URL = 'http://localhost:8000'

export default {
  name: 'App',
  components: {
    Statistics
  },
  data() {
    return {
      isLoggedIn: false,
      currentUser: null,
      publicadores: [],
      loginForm: {
        username: '',
        rol: ''
      },
      publicadorForm: {
        nombre: '',
        numero: '',  // Cambiado de number a string
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
      currentTheme: 'light'
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
    
    // Check if user is logged in
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const response = await axios.get(`${API_BASE_URL}/publicadores`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.publicadores = response.data
        this.isLoggedIn = true
        this.currentUser = JSON.parse(localStorage.getItem('user'))
      } catch (error) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  },
  methods: {
    async login() {
      try {
        const response = await axios.post(`${API_BASE_URL}/login`, {
          username: this.loginForm.username,
          rol: this.loginForm.rol
        })
        
        const { access_token } = response.data
        localStorage.setItem('token', access_token)
        localStorage.setItem('user', JSON.stringify({
          nombre: this.loginForm.username,
          rol: this.loginForm.rol
        }))
        
        this.currentUser = {
          nombre: this.loginForm.username,
          rol: this.loginForm.rol
        }
        this.isLoggedIn = true
        
        // Load publicadores
        await this.loadPublicadores()
        
        this.showAlert('success', 'Sesión iniciada correctamente')
      } catch (error) {
        this.showAlert('error', 'Error al iniciar sesión: ' + error.response?.data?.detail || error.message)
      }
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.isLoggedIn = false
      this.currentUser = null
      this.publicadores = []
      this.showAlert('info', 'Sesión cerrada')
    },
    
    async loadPublicadores() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get(`${API_BASE_URL}/publicadores`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        this.publicadores = response.data
      } catch (error) {
        this.showAlert('error', 'Error al cargar publicadores: ' + error.response?.data?.detail || error.message)
      }
    },
    
    async addPublicador() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post(`${API_BASE_URL}/publicadores`, this.publicadorForm, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.publicadores.push(response.data)
        this.closeModal()
        this.showAlert('success', 'Publicador agregado correctamente')
      } catch (error) {
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
        const token = localStorage.getItem('token')
        const response = await axios.put(`${API_BASE_URL}/publicadores/${this.editingPublicadorId}`, this.publicadorForm, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        const index = this.publicadores.findIndex(p => p.id === this.editingPublicadorId)
        if (index !== -1) {
          this.publicadores[index] = response.data
        }
        
        this.closeModal()
        this.showAlert('success', 'Publicador actualizado correctamente')
      } catch (error) {
        this.showAlert('error', 'Error al actualizar publicador: ' + error.response?.data?.detail || error.message)
      }
    },
    
    async deletePublicador(id) {
      if (!confirm('¿Estás seguro de que quieres eliminar este publicador?')) {
        return
      }
      
      try {
        const token = localStorage.getItem('token')
        await axios.delete(`${API_BASE_URL}/publicadores/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        this.publicadores = this.publicadores.filter(p => p.id !== id)
        this.showAlert('success', 'Publicador eliminado correctamente')
      } catch (error) {
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