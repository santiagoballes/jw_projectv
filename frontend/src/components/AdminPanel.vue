<template>
  <div class="admin-panel">
    <div class="card">
      <h2>Panel de Administración</h2>
      <p class="admin-description">Gestiona los roles de los usuarios registrados</p>
      
      <!-- Lista de usuarios -->
      <div class="users-list">
        <h3>Usuarios Registrados</h3>
        
        <div v-if="loading" class="loading">
          Cargando usuarios...
        </div>
        
        <div v-else-if="users.length === 0" class="no-users">
          No hay usuarios registrados
        </div>
        
        <div v-else class="users-grid">
          <div v-for="user in users" :key="user.id" class="user-card">
            <div class="user-info">
              <h4>{{ user.nombre }}</h4>
              <p class="user-email">{{ user.email }}</p>
              <div class="user-status">
                <span :class="['badge', getRoleBadgeClass(user.rol)]">
                  {{ user.rol }}
                </span>
                <span v-if="user.is_superuser" class="badge badge-warning">
                  Superusuario
                </span>
              </div>
            </div>
            
            <div class="user-actions">
              <div class="form-group">
                <label>Rol:</label>
                <select 
                  v-model="user.rol" 
                  class="form-control"
                  @change="updateUserRole(user)"
                >
                  <option value="pendiente">Pendiente</option>
                  <option value="siervo">Siervo</option>
                  <option value="anciano">Anciano</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    v-model="user.is_superuser"
                    @change="updateUserRole(user)"
                  />
                  Superusuario
                </label>
              </div>
              <div class="form-group" v-if="user.rol === 'anciano' || user.rol === 'siervo'">
                <label>Grupo asignado:</label>
                <input type="number" min="1" v-model.number="user.grupo_asignado" class="form-control" @change="updateUserRole(user)" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Alert Messages -->
    <div v-if="alert.show" :class="['alert', `alert-${alert.type}`]">
      {{ alert.message }}
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase.js'

export default {
  name: 'AdminPanel',
  data() {
    return {
      users: [],
      loading: true,
      alert: {
        show: false,
        type: 'info',
        message: ''
      }
    }
  },
  async mounted() {
    await this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const { data, error } = await supabase
          .from('usuarios')
          .select('*')
          .order('nombre', { ascending: true })

        if (error) throw error

        this.users = data || []
      } catch (error) {
        console.error('Error cargando usuarios:', error)
        this.showAlert('error', 'Error al cargar usuarios')
      } finally {
        this.loading = false
      }
    },

    async updateUserRole(user) {
      try {
        const { error } = await supabase
          .from('usuarios')
          .update({
            rol: user.rol,
            is_superuser: user.is_superuser,
            grupo_asignado: user.grupo_asignado ?? null
          })
          .eq('id', user.id)

        if (error) throw error

        this.showAlert('success', `Rol y grupo de ${user.nombre} actualizados`)
      } catch (error) {
        console.error('Error actualizando rol o grupo:', error)
        this.showAlert('error', 'Error al actualizar rol o grupo')
        
        // Revertir cambios en caso de error
        await this.loadUsers()
      }
    },

    getRoleBadgeClass(rol) {
      switch (rol) {
        case 'anciano':
          return 'badge-success'
        case 'siervo':
          return 'badge-warning'
        case 'pendiente':
          return 'badge-secondary'
        default:
          return 'badge-secondary'
      }
    },

    showAlert(type, message) {
      this.alert = {
        show: true,
        type,
        message
      }
      setTimeout(() => {
        this.hideAlert()
      }, 5000)
    },

    hideAlert() {
      this.alert.show = false
    }
  }
}
</script>

<style scoped>
.admin-panel {
  margin-top: 20px;
}

.admin-description {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.users-list h3 {
  margin-bottom: 15px;
  color: var(--text-primary);
}

.loading,
.no-users {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

.users-grid {
  display: grid;
  gap: 20px;
}

.user-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: var(--transition);
}

.user-card:hover {
  box-shadow: var(--card-hover-shadow);
  transform: translateY(-2px);
}

.user-info h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.user-email {
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  font-size: 0.9rem;
}

.user-status {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

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

.badge-secondary {
  background: var(--secondary-color);
  color: var(--text-white);
}

.user-actions {
  display: grid;
  gap: 15px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid var(--input-border);
  border-radius: 6px;
  font-size: 14px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-control:focus {
  outline: none;
  border-color: var(--input-focus-border);
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

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

/* Responsive */
@media (max-width: 768px) {
  .users-grid {
    grid-template-columns: 1fr;
  }
  
  .user-card {
    padding: 15px;
  }
  
  .user-actions {
    gap: 10px;
  }
}
</style> 