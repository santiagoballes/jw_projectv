<template>
  <div class="auth-container">
    <!-- Toggle entre Login y Registro -->
    <div class="auth-toggle">
      <button 
        @click="authMode = 'login'" 
        :class="['btn', authMode === 'login' ? 'btn-primary' : 'btn-secondary']"
      >
        Iniciar Sesión
      </button>
      <button 
        @click="authMode = 'register'" 
        :class="['btn', authMode === 'register' ? 'btn-primary' : 'btn-secondary']"
      >
        Registrarse
      </button>
    </div>

    <!-- Login Form -->
    <div v-if="authMode === 'login'" class="card login-form">
      <h2>Iniciar Sesión</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="loginEmail">Email:</label>
          <input
            type="email"
            id="loginEmail"
            v-model="loginForm.email"
            class="form-control"
            required
            placeholder="tu@email.com"
          />
        </div>
        <div class="form-group">
          <label for="loginPassword">Contraseña:</label>
          <input
            type="password"
            id="loginPassword"
            v-model="loginForm.password"
            class="form-control"
            required
            placeholder="Tu contraseña"
          />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </button>
      </form>
    </div>

    <!-- Register Form -->
    <div v-if="authMode === 'register'" class="card register-form">
      <h2>Registrarse</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="registerName">Nombre:</label>
          <input
            type="text"
            id="registerName"
            v-model="registerForm.nombre"
            class="form-control"
            required
            placeholder="Tu nombre completo"
          />
        </div>
        <div class="form-group">
          <label for="registerEmail">Email:</label>
          <input
            type="email"
            id="registerEmail"
            v-model="registerForm.email"
            class="form-control"
            required
            placeholder="tu@email.com"
          />
        </div>
        <div class="form-group">
          <label for="registerPassword">Contraseña:</label>
          <input
            type="password"
            id="registerPassword"
            v-model="registerForm.password"
            class="form-control"
            required
            placeholder="Mínimo 6 caracteres"
            minlength="6"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirmar Contraseña:</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="registerForm.confirmPassword"
            class="form-control"
            required
            placeholder="Repite tu contraseña"
            minlength="6"
          />
        </div>
        <button type="submit" class="btn btn-success" style="width: 100%" :disabled="loading">
          {{ loading ? 'Registrando...' : 'Registrarse' }}
        </button>
      </form>
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
  name: 'Auth',
  data() {
    return {
      authMode: 'login', // 'login' or 'register'
      loading: false,
      loginForm: {
        email: '',
        password: ''
      },
      registerForm: {
        nombre: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      alert: {
        show: false,
        type: 'info',
        message: ''
      }
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.hideAlert()
      
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: this.loginForm.email,
          password: this.loginForm.password
        })

        if (error) throw error

        // Obtener datos del usuario desde la tabla usuarios
        const { data: userData, error: userError } = await supabase
          .from('usuarios')
          .select('*')
          .eq('id', data.user.id)
          .single()

        if (userError) throw userError

        // Emitir evento de login exitoso
        this.$emit('login-success', {
          user: data.user,
          session: data.session,
          userData: userData
        })

        this.showAlert('success', 'Sesión iniciada correctamente')
        
      } catch (error) {
        console.error('Error en login:', error)
        this.showAlert('error', error.message || 'Error al iniciar sesión')
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      this.loading = true
      this.hideAlert()

      // Validar contraseñas
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.showAlert('error', 'Las contraseñas no coinciden')
        this.loading = false
        return
      }

      if (this.registerForm.password.length < 6) {
        this.showAlert('error', 'La contraseña debe tener al menos 6 caracteres')
        this.loading = false
        return
      }

      try {
        // Registrar usuario en Supabase Auth
        const { data, error } = await supabase.auth.signUp({
          email: this.registerForm.email,
          password: this.registerForm.password
        })

        if (error) throw error

        // Crear registro en la tabla usuarios
        const { error: userError } = await supabase
          .from('usuarios')
          .insert({
            id: data.user.id,
            email: this.registerForm.email,
            nombre: this.registerForm.nombre,
            rol: 'pendiente',
            is_superuser: false
          })

        if (userError) throw userError

        this.showAlert('success', 'Usuario registrado exitosamente. Esperando asignación de rol por el superusuario.')
        
        // Limpiar formulario
        this.registerForm = {
          nombre: '',
          email: '',
          password: '',
          confirmPassword: ''
        }

        // Cambiar a modo login
        this.authMode = 'login'
        
      } catch (error) {
        console.error('Error en registro:', error)
        this.showAlert('error', error.message || 'Error al registrar usuario')
      } finally {
        this.loading = false
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
.auth-container {
  max-width: 400px;
  margin: 0 auto;
}

.auth-toggle {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.auth-toggle .btn {
  flex: 1;
  padding: 12px;
}

.login-form,
.register-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--input-border);
  border-radius: 8px;
  font-size: 16px;
  transition: var(--transition);
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-control:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-control::placeholder {
  color: var(--input-placeholder);
}

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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: var(--text-white);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.btn-secondary {
  background: var(--secondary-color);
  color: var(--text-white);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--secondary-hover);
  transform: translateY(-2px);
}

.btn-success {
  background: var(--success-color);
  color: var(--text-white);
}

.btn-success:hover:not(:disabled) {
  background: var(--success-hover);
  transform: translateY(-2px);
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
</style> 