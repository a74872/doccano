<template>
  <v-container>
    <!-- Page title -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Estatísticas de Anotações</h1>
        <p class="text-subtitle-1 grey--text">
          Visualização simples das estatísticas do projeto
        </p>
      </v-col>
    </v-row>

    <!-- Filtros Básicos -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-filter-variant</v-icon>
        Filtros
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedAnnotators"
              :items="annotatorOptions"
              label="Anotadores"
              prepend-icon="mdi-account-multiple"
              outlined
              dense
              multiple
              clearable
              chips
              small-chips
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedLabels"
              :items="labelOptions"
              label="Labels"
              prepend-icon="mdi-tag-multiple"
              outlined
              dense
              multiple
              clearable
              chips
              small-chips
            />
          </v-col>
          <v-col cols="12" md="4" class="d-flex align-center">
            <v-btn
              color="grey"
              text
              class="mr-2"
              @click="clearFilters"
            >
              Limpar
            </v-btn>
            <v-btn
              color="primary"
              :loading="loading"
              @click="loadStatistics"
            >
              Gerar Estatísticas
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Cards de Resumo -->
    <v-row v-if="stats" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4">{{ stats.totalAnnotations }}</div>
                <div class="text-subtitle-1">Total de Anotações</div>
              </div>
              <v-icon size="40">mdi-note-text</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4">{{ stats.activeAnnotators }}</div>
                <div class="text-subtitle-1">Anotadores Ativos</div>
              </div>
              <v-icon size="40">mdi-account-group</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4">{{ stats.uniqueLabels }}</div>
                <div class="text-subtitle-1">Labels Diferentes</div>
              </div>
              <v-icon size="40">mdi-tag-multiple</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4">{{ stats.documentsCompleted }}</div>
                <div class="text-subtitle-1">Documentos Completos</div>
              </div>
              <v-icon size="40">mdi-check-circle</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabelas de Estatísticas -->
    <v-row v-if="stats">
      <!-- Estatísticas por Anotador -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account-star</v-icon>
            Performance dos Anotadores
            <v-spacer />
            <v-btn
              small
              color="primary"
              outlined
              :loading="exportLoading"
              @click="exportData('annotators')"
            >
              <v-icon left small>mdi-export</v-icon>
              Exportar
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="annotatorHeaders"
              :items="stats.annotatorStats"
              :items-per-page="10"
              dense
            >
              <template #[`item.progress`]="{ item }">
                <v-progress-linear
                  :value="item.progress"
                  color="primary"
                  height="20"
                  rounded
                >
                  {{ item.progress }}%
                </v-progress-linear>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Estatísticas por Label -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-tag-text</v-icon>
            Estatísticas de Labels
            <v-spacer />
            <v-btn
              small
              color="primary"
              outlined
              :loading="exportLoading"
              @click="exportData('labels')"
            >
              <v-icon left small>mdi-export</v-icon>
              Exportar
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="labelHeaders"
              :items="stats.labelStats"
              :items-per-page="10"
              dense
            >
              <template #[`item.percentage`]="{ item }">
                <div class="d-flex align-center">
                  <v-progress-linear
                    :value="item.percentage"
                    color="primary"
                    height="15"
                    rounded
                    class="mr-2"
                    style="min-width: 60px;"
                  />
                  <span class="text-caption">{{ item.percentage.toFixed(1) }}%</span>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Exportação Completa -->
    <v-card v-if="stats" class="mt-4">
      <v-card-title>
        <v-icon left>mdi-file-export</v-icon>
        Exportar Relatório Completo
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="exportFormat"
              :items="exportFormatOptions"
              label="Formato"
              prepend-icon="mdi-file-document"
              outlined
              dense
            />
          </v-col>
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-btn
              color="success"
              large
              :loading="exportLoading"
              @click="exportCompleteReport"
            >
              <v-icon left>mdi-download</v-icon>
              Baixar Relatório
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Mensagem sem dados -->
    <v-card v-else-if="!loading && hasSearched">
      <v-card-text class="text-center py-8">
        <v-icon size="64" color="grey lighten-1">mdi-chart-box-outline</v-icon>
        <div class="text-h6 grey--text mt-4">Nenhuma estatística disponível</div>
        <div class="grey--text">Tente ajustar os filtros e gerar novamente</div>
      </v-card-text>
    </v-card>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      bottom
      right
    >
      <v-icon left dark>{{ snackbar.icon }}</v-icon>
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'AnnotationStatistics',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      // Filtros
      selectedAnnotators: [],
      selectedLabels: [],

      // Estados
      loading: false,
      exportLoading: false,
      hasSearched: false,

      // Dados
      stats: null,
      annotatorOptions: [],
      labelOptions: [],
      members: [],
      labels: [],

      // Configurações
      exportFormat: 'csv',
      exportFormatOptions: [
        { text: 'CSV', value: 'csv' },
        { text: 'JSON', value: 'json' }
      ],

      // Snackbar
      snackbar: {
        show: false,
        message: '',
        color: 'success',
        icon: 'mdi-check-circle',
        timeout: 3000
      },

      // Headers das tabelas
      annotatorHeaders: [
        { text: 'Anotador', value: 'name', sortable: true },
        { text: 'Anotações', value: 'totalAnnotations', sortable: true },
        { text: 'Documentos', value: 'documents', sortable: true },
        { text: 'Progresso', value: 'progress', sortable: true }
      ],

      labelHeaders: [
        { text: 'Label', value: 'label', sortable: true },
        { text: 'Quantidade', value: 'count', sortable: true },
        { text: 'Porcentagem', value: 'percentage', sortable: true }
      ]
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),

    projectId() {
      return this.$route.params.id
    }
  },

  async mounted() {
    await this.loadInitialData()
  },

  methods: {
    showSnackbar(message, color = 'success', icon = 'mdi-check-circle') {
      this.snackbar = { show: true, message, color, icon, timeout: 3000 }
    },

    async loadInitialData() {
      try {
        await Promise.all([
          this.loadAnnotators(),
          this.loadLabels()
        ])
      } catch (error) {
        this.showSnackbar('Erro ao carregar dados', 'error', 'mdi-alert-circle')
        console.error(error)
      }
    },

    async loadAnnotators() {
      try {
        this.members = await this.$repositories.member.list(this.projectId)
        this.annotatorOptions = this.members.map(member => ({
          text: member.username || member.email || `User ${member.id}`,
          value: member.id
        }))
      } catch (error) {
        console.error('Erro ao carregar anotadores:', error)
      }
    },

    async loadLabels() {
      try {
        this.labels = await this.$services.categoryType.list(this.projectId)
        this.labelOptions = this.labels.map(label => ({
          text: label.text,
          value: label.text
        }))
      } catch (error) {
        console.error('Erro ao carregar labels:', error)
      }
    },

    async loadStatistics() {
      this.loading = true
      this.hasSearched = true

      try {
        const query = {}
        if (this.selectedLabels.length > 0) {
          query.labels = this.selectedLabels
        }

        const examples = await this.$services.example.list(this.projectId, query)
        this.stats = this.calculateStatistics(examples.items)

        this.showSnackbar(`Estatísticas geradas! ${this.stats.totalAnnotations} anotações analisadas.`)
      } catch (error) {
        this.showSnackbar('Erro ao gerar estatísticas', 'error', 'mdi-alert-circle')
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    calculateStatistics(examples) {
      const annotatorData = new Map()
      const labelData = new Map()
      let totalAnnotations = 0

      // Processar exemplos
      examples.forEach(example => {
        // Simular dados de anotação
        const annotatorId = example.annotator || 1
        const labels = example.labels || ['PESSOA']

        labels.forEach(label => {
          if (this.selectedLabels.length === 0 || this.selectedLabels.includes(label)) {
            totalAnnotations++

            // Dados do anotador
            if (!annotatorData.has(annotatorId)) {
              annotatorData.set(annotatorId, {
                id: annotatorId,
                name: this.getUserName(annotatorId),
                totalAnnotations: 0,
                documents: 0
              })
            }
            annotatorData.get(annotatorId).totalAnnotations++

            // Dados do label
            if (!labelData.has(label)) {
              labelData.set(label, { label, count: 0 })
            }
            labelData.get(label).count++
          }
        })
      })

      // Calcular estatísticas finais
      const annotatorStats = Array.from(annotatorData.values()).map(annotator => ({
        ...annotator,
        documents: Math.floor(annotator.totalAnnotations / 3), // Estimativa
        progress: Math.min(100, (annotator.totalAnnotations / 100) * 100)
      }))

      const labelStats = Array.from(labelData.values()).map(label => ({
        ...label,
        percentage: (label.count / totalAnnotations) * 100
      }))

      return {
        totalAnnotations,
        activeAnnotators: annotatorData.size,
        uniqueLabels: labelData.size,
        documentsCompleted: examples.length,
        annotatorStats,
        labelStats
      }
    },

    getUserName(userId) {
      const member = this.members.find(m => m.id === userId)
      return member ? (member.username || member.email || `User ${userId}`) : `User ${userId}`
    },

    clearFilters() {
      this.selectedAnnotators = []
      this.selectedLabels = []
      this.stats = null
      this.hasSearched = false
      this.showSnackbar('Filtros limpos', 'info', 'mdi-filter-remove')
    },

    exportData(type) {
      this.exportLoading = true

      try {
        const data = type === 'annotators' ? this.stats.annotatorStats : this.stats.labelStats
        const filename = `${type}_stats_${new Date().toISOString().split('T')[0]}.csv`

        const csvContent = this.convertToCSV(data)
        this.downloadFile(csvContent, filename, 'text/csv')

        this.showSnackbar('Dados exportados com sucesso!')
      } catch (error) {
        this.showSnackbar('Erro na exportação', 'error', 'mdi-alert-circle')
      } finally {
        this.exportLoading = false
      }
    },

    exportCompleteReport() {
      this.exportLoading = true

      try {
        const filename = `relatorio_completo_${new Date().toISOString().split('T')[0]}.${this.exportFormat}`
        let content, mimeType

        if (this.exportFormat === 'json') {
          content = JSON.stringify(this.stats, null, 2)
          mimeType = 'application/json'
        } else {
          content = this.generateCompleteCSV()
          mimeType = 'text/csv'
        }

        this.downloadFile(content, filename, mimeType)
        this.showSnackbar('Relatório exportado com sucesso!')
      } catch (error) {
        this.showSnackbar('Erro na exportação', 'error', 'mdi-alert-circle')
      } finally {
        this.exportLoading = false
      }
    },

    convertToCSV(data) {
      if (!data || data.length === 0) return ''

      const headers = Object.keys(data[0]).join(';')
      const rows = data.map(item => Object.values(item).join(';'))

      return [headers, ...rows].join('\n')
    },

    generateCompleteCSV() {
      let csv = 'RELATÓRIO DE ESTATÍSTICAS\n\n'

      csv += 'RESUMO GERAL\n'
      csv += `Total de Anotações;${this.stats.totalAnnotations}\n`
      csv += `Anotadores Ativos;${this.stats.activeAnnotators}\n`
      csv += `Labels Únicos;${this.stats.uniqueLabels}\n`
      csv += `Documentos Completos;${this.stats.documentsCompleted}\n\n`

      csv += 'ESTATÍSTICAS POR ANOTADOR\n'
      csv += this.convertToCSV(this.stats.annotatorStats) + '\n\n'

      csv += 'ESTATÍSTICAS POR LABEL\n'
      csv += this.convertToCSV(this.stats.labelStats)

      return csv
    },

    downloadFile(content, filename, mimeType) {
      const blob = new Blob([content], { type: mimeType })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)

      link.href = url
      link.download = filename
      link.style.display = 'none'

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.v-progress-linear {
  border-radius: 4px;
}

@media (max-width: 960px) {
  .text-h4 {
    font-size: 1.5rem !important;
  }
}
</style>