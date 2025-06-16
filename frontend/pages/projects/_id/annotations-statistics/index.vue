<template>
  <v-container>
    <!-- Page title -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Estatísticas de Anotações</h1>
        <p class="text-subtitle-1 grey--text">
          Visualização detalhada das estatísticas do projeto
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

    <!-- Loading -->
    <v-card v-if="loading" class="mb-4">
      <v-card-text class="text-center py-8">
        <v-progress-circular indeterminate size="50" color="primary" />
        <div class="mt-4 text-h6">Gerando estatísticas...</div>
      </v-card-text>
    </v-card>

    <!-- Cards de Resumo -->
    <v-row v-if="stats && !loading" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h4">{{ stats.totalAnnotations.toLocaleString() }}</div>
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
                <div class="text-h4">{{ stats.documentsAnnotated }}</div>
                <div class="text-subtitle-1">Documentos Anotados</div>
              </div>
              <v-icon size="40">mdi-file-check</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabelas de Estatísticas -->
    <v-row v-if="stats && !loading">
      <!-- Estatísticas por Anotador -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account-star</v-icon>
            Performance dos Anotadores
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="annotatorHeaders"
              :items="stats.annotatorStats"
              :items-per-page="10"
              dense
              sort-by="totalAnnotations"
              sort-desc
            >
              <template #[`item.totalAnnotations`]="{ item }">
                <v-chip small color="primary" outlined>
                  {{ item.totalAnnotations.toLocaleString() }}
                </v-chip>
              </template>
              <template #[`item.documentsAnnotated`]="{ item }">
                <span>{{ item.documentsAnnotated }}</span>
              </template>
              <template #[`item.averageAnnotationsPerDocument`]="{ item }">
                <span>{{ item.averageAnnotationsPerDocument.toFixed(1) }}</span>
              </template>
              <template #[`item.topLabels`]="{ item }">
                <v-chip-group column>
                  <v-chip
                    v-for="label in item.topLabels.slice(0, 2)"
                    :key="label.label"
                    x-small
                    color="info"
                    text-color="white"
                  >
                    {{ label.label }} ({{ label.count }})
                  </v-chip>
                  <v-chip
                    v-if="item.topLabels.length > 2"
                    x-small
                    color="grey"
                    text-color="white"
                  >
                    +{{ item.topLabels.length - 2 }}
                  </v-chip>
                </v-chip-group>
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
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="labelHeaders"
              :items="stats.labelStats"
              :items-per-page="10"
              dense
              sort-by="count"
              sort-desc
            >
              <template #[`item.count`]="{ item }">
                <v-chip small color="success" outlined>
                  {{ item.count.toLocaleString() }}
                </v-chip>
              </template>
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
              <template #[`item.uniqueAnnotators`]="{ item }">
                <span>{{ item.uniqueAnnotators }}</span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Estatísticas Adicionais -->
    <v-row v-if="stats && !loading">
      <!-- Distribuição Temporal -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-calendar</v-icon>
            Atividade por Período
          </v-card-title>
          <v-card-text>
            <v-simple-table dense>
              <thead>
                <tr>
                  <th>Período</th>
                  <th>Anotações</th>
                  <th>Percentual</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="period in stats.periodStats" :key="period.period">
                  <td>{{ period.period }}</td>
                  <td>
                    <v-chip small color="info" outlined>
                      {{ period.count }}
                    </v-chip>
                  </td>
                  <td>
                    <v-progress-linear
                      :value="period.percentage"
                      color="info"
                      height="10"
                      rounded
                      style="min-width: 80px;"
                    />
                  </td>
                </tr>
              </tbody>
            </v-simple-table>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Documentos -->
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-file-star</v-icon>
            Documentos Mais Anotados
          </v-card-title>
          <v-card-text>
            <v-simple-table dense>
              <thead>
                <tr>
                  <th>Documento</th>
                  <th>Anotações</th>
                  <th>Anotadores</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in stats.topDocuments" :key="doc.id">
                  <td>
                    <span class="text-truncate" style="max-width: 200px;">
                      {{ doc.text.substring(0, 50) }}...
                    </span>
                  </td>
                  <td>
                    <v-chip small color="primary" outlined>
                      {{ doc.annotationCount }}
                    </v-chip>
                  </td>
                  <td>{{ doc.annotatorCount }}</td>
                </tr>
              </tbody>
            </v-simple-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Mensagem sem dados -->
    <v-card v-else-if="!loading && hasSearched">
      <v-card-text class="text-center py-8">
        <v-icon size="64" color="grey lighten-1">mdi-chart-box-outline</v-icon>
        <div class="text-h6 grey--text mt-4">Nenhuma estatística disponível</div>
        <div class="grey--text">Tente ajustar os filtros e gerar novamente</div>
      </v-card-text>
    </v-card>

    <!-- Mensagem inicial -->
    <v-card v-else-if="!loading && !hasSearched">
      <v-card-text class="text-center py-8">
        <v-icon size="64" color="primary">mdi-chart-line</v-icon>
        <div class="text-h6 mt-4">Pronto para gerar estatísticas</div>
        <div class="grey--text">Configure os filtros desejados e clique em "Gerar Estatísticas"</div>
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
      hasSearched: false,

      // Dados
      stats: null,
      annotatorOptions: [],
      labelOptions: [],
      members: [],
      labels: [],
      annotations: [],
      examples: [],

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
        { text: 'Documentos', value: 'documentsAnnotated', sortable: true },
        { text: 'Média/Doc', value: 'averageAnnotationsPerDocument', sortable: true },
        { text: 'Top Labels', value: 'topLabels', sortable: false }
      ],

      labelHeaders: [
        { text: 'Label', value: 'label', sortable: true },
        { text: 'Quantidade', value: 'count', sortable: true },
        { text: 'Porcentagem', value: 'percentage', sortable: true },
        { text: 'Anotadores', value: 'uniqueAnnotators', sortable: true }
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
        this.showSnackbar('Erro ao carregar dados iniciais', 'error', 'mdi-alert-circle')
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
        throw error
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
        throw error
      }
    },

    async loadStatistics() {
      this.loading = true
      this.hasSearched = true

      try {
        // Carregar exemplos/documentos
        const examplesResponse = await this.$services.example.list(this.projectId)
        this.examples = examplesResponse.items || examplesResponse

        // Carregar anotações para cada exemplo
        const annotationsPromises = this.examples.map(async (example) => {
          try {
            // Ajuste aqui baseado na sua API de anotações
            const annotations = await this.$services.annotation.list(this.projectId, example.id)
            return {
              exampleId: example.id,
              exampleText: example.text,
              annotations: annotations.items || annotations
            }
          } catch (error) {
            console.error(`Erro ao carregar anotações do exemplo ${example.id}:`, error)
            return {
              exampleId: example.id,
              exampleText: example.text,
              annotations: []
            }
          }
        })

        const annotationsByExample = await Promise.all(annotationsPromises)

        // Flatten todas as anotações
        this.annotations = annotationsByExample.flatMap(item =>
          item.annotations.map(annotation => ({
            ...annotation,
            exampleId: item.exampleId,
            exampleText: item.exampleText
          }))
        )

        // Aplicar filtros
        const filteredAnnotations = this.applyFilters(this.annotations)

        // Calcular estatísticas
        this.stats = this.calculateStatistics(filteredAnnotations)

        this.showSnackbar(
          `Estatísticas geradas! ${this.stats.totalAnnotations} anotações analisadas.`,
          'success'
        )
      } catch (error) {
        this.showSnackbar('Erro ao gerar estatísticas', 'error', 'mdi-alert-circle')
        console.error(error)
        this.stats = null
      } finally {
        this.loading = false
      }
    },

    applyFilters(annotations) {
      let filtered = [...annotations]

      // Filtro por anotadores
      if (this.selectedAnnotators.length > 0) {
        filtered = filtered.filter(annotation =>
          this.selectedAnnotators.includes(annotation.user || annotation.annotator_id)
        )
      }

      // Filtro por labels
      if (this.selectedLabels.length > 0) {
        filtered = filtered.filter(annotation => {
          const annotationLabel = annotation.label || annotation.category || annotation.text
          return this.selectedLabels.includes(annotationLabel)
        })
      }

      return filtered
    },

    calculateStatistics(filteredAnnotations) {
      const annotatorStats = new Map()
      const labelStats = new Map()
      const documentStats = new Map()
      const periodStats = new Map()

      const totalAnnotations = filteredAnnotations.length

      // Processar cada anotação
      filteredAnnotations.forEach(annotation => {
        const annotatorId = annotation.user || annotation.annotator_id || 'unknown'
        const annotatorName = this.getUserName(annotatorId)
        const label = annotation.label || annotation.category || annotation.text || 'Unknown'
        const exampleId = annotation.exampleId
        const createdAt = annotation.created_at || annotation.createdAt || new Date().toISOString()

        // Stats por anotador
        if (!annotatorStats.has(annotatorId)) {
          annotatorStats.set(annotatorId, {
            id: annotatorId,
            name: annotatorName,
            totalAnnotations: 0,
            documentsAnnotated: new Set(),
            labelCounts: new Map()
          })
        }

        const annotatorData = annotatorStats.get(annotatorId)
        annotatorData.totalAnnotations++
        annotatorData.documentsAnnotated.add(exampleId)

        if (!annotatorData.labelCounts.has(label)) {
          annotatorData.labelCounts.set(label, 0)
        }
        annotatorData.labelCounts.set(label, annotatorData.labelCounts.get(label) + 1)

        // Stats por label
        if (!labelStats.has(label)) {
          labelStats.set(label, {
            label,
            count: 0,
            annotators: new Set()
          })
        }

        const labelData = labelStats.get(label)
        labelData.count++
        labelData.annotators.add(annotatorId)

        // Stats por documento
        if (!documentStats.has(exampleId)) {
          const example = this.examples.find(ex => ex.id === exampleId)
          documentStats.set(exampleId, {
            id: exampleId,
            text: example ? example.text : 'Unknown',
            annotationCount: 0,
            annotators: new Set()
          })
        }

        const docData = documentStats.get(exampleId)
        docData.annotationCount++
        docData.annotators.add(annotatorId)

        // Stats por período (mês)
        const period = new Date(createdAt).toLocaleDateString('pt-BR', {
          year: 'numeric',
          month: 'long'
        })

        if (!periodStats.has(period)) {
          periodStats.set(period, 0)
        }
        periodStats.set(period, periodStats.get(period) + 1)
      })

      // Finalizar stats dos anotadores
      const finalAnnotatorStats = Array.from(annotatorStats.values()).map(annotator => {
        const documentsCount = annotator.documentsAnnotated.size
        const topLabels = Array.from(annotator.labelCounts.entries())
          .map(([label, count]) => ({ label, count }))
          .sort((a, b) => b.count - a.count)

        return {
          id: annotator.id,
          name: annotator.name,
          totalAnnotations: annotator.totalAnnotations,
          documentsAnnotated: documentsCount,
          averageAnnotationsPerDocument: documentsCount > 0 ? annotator.totalAnnotations / documentsCount : 0,
          topLabels
        }
      })

      // Finalizar stats dos labels
      const finalLabelStats = Array.from(labelStats.values()).map(label => ({
        label: label.label,
        count: label.count,
        percentage: totalAnnotations > 0 ? (label.count / totalAnnotations) * 100 : 0,
        uniqueAnnotators: label.annotators.size
      }))

      // Finalizar stats dos documentos (top 10)
      const topDocuments = Array.from(documentStats.values())
        .map(doc => ({
          ...doc,
          annotatorCount: doc.annotators.size
        }))
        .sort((a, b) => b.annotationCount - a.annotationCount)
        .slice(0, 10)

      // Finalizar stats por período
      const finalPeriodStats = Array.from(periodStats.entries())
        .map(([period, count]) => ({
          period,
          count,
          percentage: totalAnnotations > 0 ? (count / totalAnnotations) * 100 : 0
        }))
        .sort((a, b) => b.count - a.count)

      return {
        totalAnnotations,
        activeAnnotators: annotatorStats.size,
        uniqueLabels: labelStats.size,
        documentsAnnotated: documentStats.size,
        annotatorStats: finalAnnotatorStats,
        labelStats: finalLabelStats,
        topDocuments,
        periodStats: finalPeriodStats
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

.text-truncate {
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 960px) {
  .text-h4 {
    font-size: 1.5rem !important;
  }

  .v-chip-group {
    flex-direction: column;
  }
}

/* Melhorar responsividade das tabelas */
@media (max-width: 768px) {
  .v-data-table {
    font-size: 0.8rem;
  }

  .v-chip {
    font-size: 0.7rem !important;
  }
}

/* Estilo para cards de estatísticas */
.v-card.primary {
  background: linear-gradient(45deg, #1976d2, #42a5f5) !important;
}

.v-card.success {
  background: linear-gradient(45deg, #388e3c, #66bb6a) !important;
}

.v-card.info {
  background: linear-gradient(45deg, #0288d1, #4fc3f7) !important;
}

.v-card.warning {
  background: linear-gradient(45deg, #f57c00, #ffb74d) !important;
}

/* Animações suaves */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Melhorar aparência dos chips */
.v-chip.v-size--small {
  font-weight: 500;
}

/* Estilo para progress bars */
.v-progress-linear {
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>