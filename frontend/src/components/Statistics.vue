<template>
  <div class="statistics-container">
    <!-- Tarjetas de estadísticas principales -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3>{{ stats.total }}</h3>
          <p>Total Publicadores</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <h3>{{ stats.precursores }}</h3>
          <p>Precursores</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">💪</div>
        <div class="stat-content">
          <h3>{{ stats.conAnimo }}</h3>
          <p>Con Ánimo</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3>{{ stats.gruposUnicos }}</h3>
          <p>Grupos Activos</p>
        </div>
      </div>
    </div>

    <!-- Gráficos -->
    <div class="charts-container">
      <!-- Gráfico de distribución por grupo -->
      <div class="chart-card">
        <h3>Distribución por Grupo</h3>
        <canvas ref="gruposChart" width="400" height="200"></canvas>
      </div>
      
      <!-- Gráfico de precursores vs no precursores -->
      <div class="chart-card">
        <h3>Precursores vs No Precursores</h3>
        <canvas ref="precursoresChart" width="400" height="200"></canvas>
      </div>
      
      <!-- Gráfico de ánimo -->
      <div class="chart-card">
        <h3>Estado de Ánimo</h3>
        <canvas ref="animoChart" width="400" height="200"></canvas>
      </div>
      
      <!-- Gráfico de tendencias (últimos 7 días) -->
      <div class="chart-card full-width">
        <h3>Actividad Reciente</h3>
        <canvas ref="tendenciasChart" width="800" height="200"></canvas>
      </div>
    </div>

    <!-- Tabla de estadísticas detalladas -->
    <div class="stats-table-container">
      <h3>Estadísticas por Grupo</h3>
      <div class="stats-table">
        <div class="table-header">
          <div class="header-cell">Grupo</div>
          <div class="header-cell">Total</div>
          <div class="header-cell">Precursores</div>
          <div class="header-cell">Con Ánimo</div>
          <div class="header-cell">% Precursor</div>
        </div>
        <div 
          v-for="grupo in stats.porGrupo" 
          :key="grupo.grupo" 
          class="table-row"
        >
          <div class="table-cell">{{ grupo.grupo }}</div>
          <div class="table-cell">{{ grupo.total }}</div>
          <div class="table-cell">{{ grupo.precursores }}</div>
          <div class="table-cell">{{ grupo.conAnimo }}</div>
          <div class="table-cell">{{ grupo.porcentajePrecursor }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'Statistics',
  props: {
    publicadores: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      charts: {}
    }
  },
    computed: {
    isDarkMode() {
      return document.documentElement.getAttribute('data-theme') === 'dark'
    },
    chartColors() {
      return {
        primary: this.isDarkMode ? '#6366f1' : '#4f46e5',
        secondary: this.isDarkMode ? '#9ca3af' : '#6b7280',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        text: this.isDarkMode ? '#f9fafb' : '#1f2937',
        grid: this.isDarkMode ? '#374151' : '#e5e7eb',
        background: this.isDarkMode ? 'rgba(31, 41, 55, 0.8)' : 'rgba(255, 255, 255, 0.8)'
      }
    },
    stats() {
      const total = this.publicadores.length
      const precursores = this.publicadores.filter(p => p.precursor).length
      const conAnimo = this.publicadores.filter(p => p.animo).length
      
      // Agrupar por grupo
      const porGrupo = {}
      this.publicadores.forEach(p => {
        if (!porGrupo[p.grupo]) {
          porGrupo[p.grupo] = {
            grupo: p.grupo,
            total: 0,
            precursores: 0,
            conAnimo: 0
          }
        }
        porGrupo[p.grupo].total++
        if (p.precursor) porGrupo[p.grupo].precursores++
        if (p.animo) porGrupo[p.grupo].conAnimo++
      })
      
      // Calcular porcentajes
      Object.values(porGrupo).forEach(grupo => {
        grupo.porcentajePrecursor = grupo.total > 0 
          ? Math.round((grupo.precursores / grupo.total) * 100) 
          : 0
      })
      
      return {
        total,
        precursores,
        conAnimo,
        gruposUnicos: Object.keys(porGrupo).length,
        porGrupo: Object.values(porGrupo).sort((a, b) => a.grupo - b.grupo)
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.createCharts()
    })
  },
  watch: {
    publicadores: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts()
        })
      },
      deep: true
    },
    isDarkMode: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts()
        })
      }
    }
  },
  methods: {
    createCharts() {
      this.createGruposChart()
      this.createPrecursoresChart()
      this.createAnimoChart()
      this.createTendenciasChart()
    },
    
    createGruposChart() {
      const ctx = this.$refs.gruposChart.getContext('2d')
      const data = this.stats.porGrupo.map(g => ({
        grupo: `Grupo ${g.grupo}`,
        total: g.total
      }))
      
      this.charts.grupos = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(d => d.grupo),
          datasets: [{
            label: 'Publicadores por Grupo',
            data: data.map(d => d.total),
            backgroundColor: [
              this.chartColors.primary, this.chartColors.success, this.chartColors.warning, this.chartColors.danger,
              '#9966FF', '#FF9F40', '#FF6384', this.chartColors.secondary
            ],
            borderWidth: 1,
            borderColor: this.chartColors.grid
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              ticks: {
                color: this.chartColors.text
              },
              grid: {
                color: this.chartColors.grid
              }
            },
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                color: this.chartColors.text
              },
              grid: {
                color: this.chartColors.grid
              }
            }
          }
        }
      })
    },
    
    createPrecursoresChart() {
      const ctx = this.$refs.precursoresChart.getContext('2d')
      const precursores = this.stats.precursores
      const noPrecursores = this.stats.total - precursores
      
      this.charts.precursores = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Precursores', 'No Precursores'],
          datasets: [{
            data: [precursores, noPrecursores],
            backgroundColor: [this.chartColors.success, this.chartColors.secondary],
            borderWidth: 2,
            borderColor: this.isDarkMode ? '#374151' : '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: this.chartColors.text
              }
            }
          }
        }
      })
    },
    
    createAnimoChart() {
      const ctx = this.$refs.animoChart.getContext('2d')
      const conAnimo = this.stats.conAnimo
      const sinAnimo = this.stats.total - conAnimo
      
      this.charts.animo = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['Con Ánimo', 'Sin Ánimo'],
          datasets: [{
            data: [conAnimo, sinAnimo],
            backgroundColor: [this.chartColors.warning, this.chartColors.primary],
            borderWidth: 2,
            borderColor: this.isDarkMode ? '#374151' : '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: this.chartColors.text
              }
            }
          }
        }
      })
    },
    
    createTendenciasChart() {
      const ctx = this.$refs.tendenciasChart.getContext('2d')
      
      // Simular datos de tendencias (en un caso real vendrían de la base de datos)
      const labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
      const data = labels.map(() => Math.floor(Math.random() * 10) + 1)
      
      this.charts.tendencias = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Publicadores Activos',
            data: data,
            borderColor: this.chartColors.primary,
            backgroundColor: this.isDarkMode ? 'rgba(99, 102, 241, 0.1)' : 'rgba(79, 70, 229, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              ticks: {
                color: this.chartColors.text
              },
              grid: {
                color: this.chartColors.grid
              }
            },
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                color: this.chartColors.text
              },
              grid: {
                color: this.chartColors.grid
              }
            }
          }
        }
      })
    },
    
    updateCharts() {
      // Destruir gráficos existentes
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy()
      })
      
      // Recrear gráficos
      this.createCharts()
    }
  },
  beforeUnmount() {
    // Limpiar gráficos al destruir el componente
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy()
    })
  }
}
</script> 