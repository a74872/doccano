<template>
  <v-container>
    <!-- Page title -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4"></h1>
      </v-col>
    </v-row>

    <!-- Selector buttons just under the title -->
    <v-row class="mb-4">
      <v-col cols="12" class="d-flex">
        <v-btn
          :color="activeSection === 'annotations' ? 'primary' : 'grey lighten-1'"
          class="mr-3"
          depressed
          @click="toggleSection('annotations')"
        >
          Annotations
        </v-btn>

        <v-btn
          :color="activeSection === 'annotators' ? 'primary' : 'grey lighten-1'"
          depressed
          @click="toggleSection('annotators')"
        >
          Annotators
        </v-btn>
      </v-col>
    </v-row>

    <!-- ============================  ANNOTATIONS SECTION  ============================ -->
    <v-expand-transition>
      <div v-if="activeSection === 'annotations'">
        <!-- Sub-report type (Desacordos | Perspetivas)  -->
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedReport"
              :items="annotationReportTypes"
              label="Tipo de Relatório"
              outlined
              dense
              @change="onReportTypeChange"
            />
          </v-col>
        </v-row>

        <!-- Annotation-specific filters -->
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-if="showDatasetFilter && selectedReport !== 'annotationHistory'"
              v-model="selectedDataset"
              :items="datasets"
              item-text="name"
              item-value="id"
              label="Dataset"
              outlined
              dense
              :loading="loadingDatasets"
            />

            <v-select
              v-else-if="selectedReport === 'annotationHistory' && examples.length > 0"
              v-model="selectedExample"
              :items="examples"
              item-text="name"
              item-value="name"
              label="Dataset Name"
              outlined
              dense
            />

            <v-select
              v-if="selectedReport === 'annotationHistory'"
              v-model="selectedMember"
              :items="memberItems"
              label="Annotator"
              outlined
              dense
              :loading="loadingMembers"
            />

            <v-select
              v-if="selectedReport === 'annotationHistory'"
              v-model="selectedLabel"
              :items="labelItems"
              label="Label"
              outlined
              dense
              :loading="loadingLabels"
            />

            <v-select
              v-else-if="showPerspectiveFilter"
              v-model="selectedPerspective"
              :items="perspectives"
              item-text="name"
              item-value="id"
              label="Perspetiva"
              outlined
              dense
              :loading="loadingPerspectives"
            />
          </v-col>

          <v-col cols="12" md="4">
            <v-select
              v-if="showDiscussionFilter"
              v-model="selectedDiscussion"
              :items="discussions"
              item-text="title"
              item-value="id"
              label="Título da Discussão"
              outlined
              dense
              :loading="loadingDiscussions"
            />
          </v-col>
        </v-row>

        <!-- Action buttons -->
        <v-row>
          <v-col cols="12">
            <v-btn
              color="primary"
              class="mr-2"
              :loading="loading"
              :disabled="!canGenerateReport"
              @click="generateReport"
            >
              Gerar Relatório
            </v-btn>

            <v-btn
              color="secondary"
              :disabled="!reportData"
              @click="exportReport"
            >
              Export Report
            </v-btn>
          </v-col>
        </v-row>

        <!-- Report table(s) for annotations -->
        <v-row v-if="reportData && (selectedReport === 'disagreements' || selectedReport === 'perspectives')">
          <v-col cols="12">
            <v-card>
              <v-card-title>{{ reportTitle }}</v-card-title>
              <v-card-text>
                <div v-if="selectedReport === 'disagreements'">
                  <v-data-table
                    :headers="disagreementHeaders"
                    :items="reportData.items"
                    :loading="loading"
                  />
                </div>
                <div v-else-if="selectedReport === 'perspectives'">
                  <v-data-table
                    :headers="perspectiveHeaders"
                    :items="reportData.items"
                    :loading="loading"
                  />
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="reportData && selectedReport === 'annotationHistory'">
          <v-col cols="12">
            <v-card>
              <v-card-title>
                {{ reportTitle }}
                <v-spacer />

                <!-- Menu de datas para histórico de anotações -->
                <v-menu
                  v-if="selectedReport === 'annotationHistory'"
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  offset-y
                  transition="scale-transition"
                  max-width="320"
                >
                  <template #activator="{ on, attrs }">
                    <v-btn
                      v-bind="attrs"
                      v-on="on"
                      color="primary"
                      class="d-flex align-center px-3 py-2"
                      elevation="0"
                    >
                      <span class="mr-2 subtitle-2 font-weight-medium">
                        {{ dateFilterLabel }}
                      </span>
                      <v-icon small>{{ icons.calendar }}</v-icon>
                    </v-btn>
                  </template>

                  <v-card>
                    <v-card-text style="width:340px">
                      <div class="subtitle-2 mb-1">Start date</div>
                      <v-date-picker
                        v-model="startDate"
                        :max="endDate || undefined"
                        label="Start date"
                        scrollable
                        class="mb-2"
                      />

                      <div class="subtitle-2 mb-1">End date</div>
                      <v-date-picker
                        v-model="endDate"
                        :min="startDate || undefined"
                        label="End date"
                        scrollable
                      />
                    </v-card-text>
                    <v-card-actions class="justify-end pr-20" style="margin-right:10px">
                      <v-btn text @click="clearDates">Clean </v-btn>
                      <v-btn color="primary" @click="dateMenu=false">OK </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-menu>
              </v-card-title>

              <v-card-text>
                <v-data-table
                  :headers="annotationHistoryHeaders"
                  :items="filteredItems"
                  :loading="loading"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-expand-transition>

    <!-- =======================  ANNOTATORS SECTION  ======================= -->
    <v-expand-transition>
      <div v-if="activeSection === 'annotators'">
        <!-- ---------- card único com título + botão-calendário -------- -->

        <!-- ---------- select de membro + botões ----------------------- -->
        <!-- ❶ LINHA dos filtros + botões  -->
        <v-row class="mb-4" align="center">
          <!-- SELECT ocupa 4 colunas em md+  -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedMember"
              :items="memberItems"
              label="Annotator"
              outlined
              dense
              :loading="loadingMembers"
            />
          </v-col>

          <!-- BOTÕES: col "auto" e alinhados à direita -->
          <v-col
            cols="12"
            md="8"
            class="d-flex justify-mid align-center mt-n7"
          >
            <v-btn
              color="primary"
              large
              class="mr-2"
              :loading="loading"
              :disabled="!canGenerateReport"
              @click="generateReport"
            >
              Generate&nbsp;Report
            </v-btn>

            <v-btn
              color="secondary"
              large
              :disabled="!reportData"
              @click="showExportDialog = true"
            >
              Export&nbsp;Report
            </v-btn>

            <export-report-dialog
              v-model="showExportDialog"
              :title="reportTitle.replace(/\\s+/g,'_').toLowerCase()"
              :headers="activeSection==='annotators' ? annotatorHeaders
                       : selectedReport==='disagreements' ? disagreementHeaders
                       : selectedReport==='perspectives'   ? perspectiveHeaders
                       : annotationHistoryHeaders"
              :items="filteredItems"
            />

          </v-col>
        </v-row>

        <v-card>
          <v-card-title>
            {{ reportTitle }}
            <v-spacer />

            <!-- activator do menu de datas -->
            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              offset-y
              transition="scale-transition"
              max-width="320"
            >
              <template #activator="{ on, attrs }">
                <!-- botão que abre o menu -->
                <v-btn
                  v-bind="attrs"
                  v-on="on"
                  color="primary"
                  class="d-flex align-center px-3 py-2"
                  elevation="0"
                >
                  <!-- título / legenda -->
                  <span class="mr-2 subtitle-2 font-weight-medium">
                    Data filter
                  </span>

                  <!-- ícone do calendário -->
                  <v-icon small>{{ icons.calendar }}</v-icon>
                </v-btn>
              </template>

              <!-- ---- pickers dentro do menu ---- -->
              <v-card>
                <v-card-text style="width:340px">
                  <div class="subtitle-2 mb-1">Start date</div>
                  <v-date-picker
                    v-model="startDate"
                    :max="endDate || undefined"
                    label="Start date"
                    scrollable
                    class="mb-2"
                  />

                  <div class="subtitle-2 mb-1">End date</div>
                  <v-date-picker
                    v-model="endDate"
                    :min="startDate || undefined"
                    label="End date"
                    scrollable
                  />
                </v-card-text>
                <v-card-actions class="justify-end pr-20" style="margin-right:10px">
                  <v-btn text  @click="clearDates">Clean </v-btn>
                  <v-btn color="primary" @click="dateMenu=false">OK </v-btn>
                </v-card-actions>
              </v-card>
            </v-menu>
          </v-card-title>

          <!-- ---------- tabela filtrada ------------------------------- -->
          <v-card-text>
            <v-data-table
              :headers="annotatorHeaders"
              :items="filteredItems"
              :loading="loading"
            />
          </v-card-text>
        </v-card>
      </div>
    </v-expand-transition>

    <!-- ============================  ERROR ============================ -->
    <v-row v-if="errorKey || error">
      <v-col cols="12">
        <!-- erro traduzido a partir da key -->
        <v-alert
          v-if="errorKey"
          type="error"
          border="left"
          colored-border
          elevation="2"
        >
          {{ $t(errorKey) }}
        </v-alert>

        <!-- fallback para mensagens literais -->
        <v-alert
          v-else
          type="error"
          border="left"
          colored-border
          elevation="2"
        >
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

  </v-container>
</template>

<script lang="ts">
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

import Vue from 'vue'
import { mdiCalendarRange } from '@mdi/js'
import ExportReportDialog from '~/components/statistics/ExportReportDialog.vue'
import { Perspective } from '~/domain/models/perspective/perspective'
import { APIStatisticsRepository } from '~/repositories/statistics/apiStatisticsRepository'

interface ReportData {
  items: Array<{
    document?: number
    annotator1?: number
    annotator2?: number
    disagreementRate?: number
    disagreementCategories?: string[]
    perspective?: string
    total?: number
    categories?: string
    datasets?: Array<{
      document: number
      categories: Array<{
        name: string
        count: number
        percentage: string
      }>
    }>
  }>
}

interface Dataset {
  id: number
  name: string
}

interface Discussion {
  id: number
  title: string
}

interface LabelItem {
  text: string
  backgroundColor: string
  textColor: string
}

export default Vue.extend({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  components: { ExportReportDialog },

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      icons: {calendar: mdiCalendarRange,},
      showExportDialog: false,
      error:    null as string | null,
      errorKey: ''   as string,
      dateMenu  : false,
      startDate : null as string | null,
      endDate   : null as string | null,
      activeSection: null as 'annotations' | 'annotators' | null,
      selectedReport : 'annotators',
      selectedLabel: null as string | null,
      loadingLabels: false,
      annotationReportTypes: [
        { text: 'Relatório de Desacordos', value: 'disagreements' },
        { text: 'Relatório de Perspetivas', value: 'perspectives' },
        { text: 'Histórico de Anotações', value: 'annotationHistory' }
      ],
      selectedDataset: null as string | null,
      selectedPerspective: null as number | null,
      selectedMember : 'ALL' as string,
      selectedDiscussion: null as number | null,
      selectedExample: null as string | null,
      loading: false,
      loadingDatasets: false,
      loadingPerspectives: false,
      loadingMembers: false,
      loadingDiscussions: false,
      reportData: null as ReportData | null,
      reportTypes: [
        { text: 'Relatório de Desacordos', value: 'disagreements' },
        { text: 'Relatório de Perspetivas', value: 'perspectives' },
        { text: 'Annotators Report', value: 'annotators' },
        { text: 'Histórico de Anotações', value: 'annotationHistory' }
      ],
      datasets: [] as Dataset[],
      perspectives: [] as Perspective[],
      members: [] as { username:string }[],
      discussions: [] as Discussion[],
      disagreementHeaders: [
        { text: 'Documento', value: 'document' },
        { text: 'Annotator 1', value: 'annotator1' },
        { text: 'Annotator 2', value: 'annotator2' },
        { text: 'Taxa de Desacordo', value: 'disagreementRate' },
        { text: 'Categorias em Desacordo', value: 'disagreementCategories' }
      ],
      perspectiveHeaders: [
        { text: 'Documento', value: 'document' },
        { text: 'Annotator', value: 'annotator' },
        { text: 'Categoria', value: 'category' },
        { text: 'Frequência', value: 'frequency' },
        { text: 'Percentagem', value: 'percentage' }
      ],
      annotatorHeaders: [
        { text: 'Annotator', value: 'annotator' },
        { text: 'Dataset Name', value: 'example' },
        { text: 'Last Modification', value: 'date'      },
        { text: 'Total Labels', value: 'total' },
        { text: 'Labels Used', value: 'categories' }
      ],
      headers: [
        { text: 'Annotator', value: 'annotator' },
        { text: 'Total Annotations', value: 'total' },
        { text: 'Categories', value: 'categories' },
        { text: 'Datasets', value: 'datasets' }
      ],
      labels: [] as LabelItem[],
      projectId: 0,
      annotationHistoryHeaders: [
        { text: 'Annotator', value: 'annotator' },
        { text: 'Dataset Name', value: 'example' },
        { text: 'Label', value: 'label' },
        { text: 'Date', value: 'date' }
      ],
      examples: [] as { name: string }[],
    }
  },

  computed: {
    showDatasetFilter(): boolean {
      return (
        this.selectedReport === 'disagreements' ||
        this.selectedReport === 'annotationHistory'
      )
    },
    showPerspectiveFilter(): boolean {
      return this.selectedReport === 'perspectives'
    },
    showMemberFilter(): boolean {
      return this.selectedReport === 'annotators'
    },
    showDiscussionFilter(): boolean {
      return this.selectedReport === 'disagreements' && this.selectedDataset !== null
    },

    memberItems (): { text:string, value:string }[] {
      return [
        { text:'All', value:'ALL' },
        ...this.members.map(m => ({ text:m.username, value:m.username }))
      ]
    },

    labelItems(): { text: string; value: string }[] {
      return [
        { text: 'All', value: 'ALL' },
        ...this.labels.map(l => ({ text: l.text, value: l.text }))
      ]
    },

    exampleItems(): { text: string; value: string }[] {
      return [
        { text: 'All', value: 'ALL' },
        ...this.examples.map(ex => ({ text: ex.name, value: ex.name }))
      ]
    },

    canGenerateReport(): boolean {
      switch (this.selectedReport) {
        case 'disagreements':
          return this.selectedDataset !== null && this.selectedDiscussion !== null
        case 'perspectives':
          return this.selectedPerspective !== null
        case 'annotators':
          return true
        case 'annotationHistory':
          // Permite gerar o relatório se pelo menos um filtro estiver selecionado
          return this.selectedExample !== null || 
                 this.selectedMember !== 'ALL' || 
                 this.selectedLabel !== null
        default:
          return false
      }
    },
    reportTitle(): string {
      const map: Record<string, string> = {
        disagreements: 'Relatório de Desacordos',
        perspectives: 'Relatório de Perspetivas',
        annotators: 'Annotators Report',
        annotationHistory: 'Histórico de Anotações'
      }
      return map[this.selectedReport] || ''
    },

    /* label resumido no botão */
    dateFilterLabel (): string {
      if (!this.startDate && !this.endDate) return 'Filtrar por data'
      if (this.startDate && this.endDate)   return `${this.startDate} → ${this.endDate}`
      return this.startDate || this.endDate || ''
    },

    /* linhas aplicando o intervalo de datas */
    filteredItems (): any[] {
      if (!this.reportData) return []
      let items = this.reportData.items

      // Aplica filtro de exemplo se selecionado
      if (this.selectedReport === 'annotationHistory' && this.selectedExample) {
        items = items.filter((row: any) => row.example === this.selectedExample)
      }

      // Aplica filtro de anotador se selecionado
      if (this.selectedReport === 'annotationHistory' && this.selectedMember !== 'ALL') {
        items = items.filter((row: any) => row.annotator === this.selectedMember)
      }

      // Aplica filtro de label se selecionado
      if (this.selectedReport === 'annotationHistory' && this.selectedLabel && this.selectedLabel !== 'ALL') {
        items = items.filter((row: any) => row.label === this.selectedLabel)
      }

      // Aplica filtro de datas
      const { startDate, endDate } = this
      if (!startDate && !endDate) return items
      const t0 = startDate ? new Date(startDate) : null
      const t1 = endDate   ? new Date(endDate)   : null
      return items.filter(row => {
        if (!row.date) return false
        const ts = new Date(row.date)
        if (t0 && ts < t0) return false
        if (t1 && ts > new Date(t1.getTime()+86400000-1)) return false
        return true
      })
    }

  },

  async fetch() {
    await this.loadInitialData()
  },

  methods: {
    /* Toggle the two main sections */
    toggleSection(section: 'annotations' | 'annotators') {
      // If the user clicks the already‑open section, collapse it
      if (this.activeSection === section) {
        this.activeSection = null
        return
      }

      // Open the requested section and set an appropriate default reportType
      this.activeSection = section
      this.selectedReport = section === 'annotators' ? 'annotators' : 'disagreements'
      this.onReportTypeChange()
    },

    async loadInitialData() {
      const projectId = parseInt(this.$route.params.id)
      await Promise.all([
        this.loadDatasets(projectId),
        this.loadPerspectives(projectId),
        this.loadMembers(projectId),
        this.loadExamples(projectId),
        this.loadLabels()
      ])
    },

    async loadDatasets(projectId: number) {
      this.loadingDatasets = true
      try {
        // Buscar datasets reais do projeto
        const datasets = await this.$repositories.catalog.list(projectId.toString())
        this.datasets = datasets.map((d: any) => ({ id: d.taskId, name: d.displayName || d.display_name || d.name }))
      } catch (error) {
        console.error('Erro ao carregar datasets:', error)
      } finally {
        this.loadingDatasets = false
      }
    },

    async loadPerspectives(projectId: number) {
      this.loadingPerspectives = true
      try {
        this.perspectives = await this.$repositories.perspective.getPerspectives(projectId)
      } catch (error) {
        console.error('Erro ao carregar perspetivas:', error)
      } finally {
        this.loadingPerspectives = false
      }
    },

    async loadMembers (projectId: number) {
      this.loadingMembers = true
      try {
        const dist = await this.$repositories.metrics
                            .fetchCategoryDistribution(projectId.toString(), {})
        this.members = Object.keys(dist).map(username => ({ username }))
      } finally {
        this.loadingMembers = false
      }
    },

    async loadExamples(projectId: number) {
      try {
        const response = await this.$repositories.example.list(projectId.toString(), {});
        const items = response.items || [];
        const uniqueExamples = Array.from(new Set(items.map((ex: any) => ex.upload_name || ex.filename?.split('/').pop() || `#${ex.id}`)));
        this.examples = uniqueExamples.map((name: string) => ({ name }));
      } catch (error) {
        console.error('Erro ao carregar exemplos:', error);
        this.examples = [];
      }
    },

    async loadDiscussions(_projectId: number, _datasetId: number) {
      this.loadingDiscussions = true
      try {
        // TODO: Implementar chamada à API para obter discussões
        const response = await new Promise<{ results: Discussion[] }>(resolve => {
          setTimeout(() => {
            resolve({
              results: [
                { id: 1, title: 'Discussão 1' },
                { id: 2, title: 'Discussão 2' }
              ]
            })
          }, 1000)
        })
        this.discussions = response.results
      } catch (error) {
        console.error('Erro ao carregar discussões:', error)
      } finally {
        this.loadingDiscussions = false
      }
    },

    onReportTypeChange() {
      // Resetar seleções quando o tipo de relatório muda
      this.selectedDataset = null
      this.selectedPerspective = null
      this.selectedMember = 'ALL'
      this.selectedDiscussion = null
      this.selectedExample = null
      this.selectedLabel = null
      this.reportData = null
    },

    async generateReport () {
      this.startDate = this.endDate = null
      this.loading = true
      this.error   = null

      const projectId = Number(this.$route.params.id)
      const statisticsRepository = this.$repositories.statistics as APIStatisticsRepository

      /* ------------ filtros visíveis em todo o método ------------ */
      const filters = {
        dataset    : this.selectedDataset    || undefined,
        discussion : this.selectedDiscussion || undefined,
        perspective: this.selectedPerspective|| undefined,
        member     : this.selectedMember === 'ALL' ? undefined : this.selectedMember,
        example    : this.selectedExample    || undefined
      }

      try {
        if (this.selectedReport === 'annotators') {
          // "ALL" → undefined → devolve todos os membros
          this.reportData = await statisticsRepository.generateAnnotatorReport(
            projectId.toString(),
            { member: filters.member }
          )
        } else if (this.selectedReport === 'disagreements') {
          this.reportData = await statisticsRepository.generateDisagreementReport(projectId, filters)
        } else if (this.selectedReport === 'perspectives') {
          this.reportData = await statisticsRepository.generatePerspectiveReport(projectId, filters)
        } else { /* annotationHistory */
          this.reportData = await statisticsRepository.generateAnnotationHistoryReport(
            projectId.toString(),
            filters.example,
            { member: filters.member }
          )
        }

        if (!this.reportData?.items?.length) {
          this.error = 'Nenhum dado encontrado para os filtros selecionados.'
          this.reportData = null
        }

      } catch (err: any) {
      console.error('API-error:', err)

      /* ------------ indisponível / timeout ------------ */
      const status = err.response?.status
      if (!err.response || [0, 502, 503, 504].includes(status)) {
        this.errorKey = 'errors.serverUnavailable'   // usar a chave i18n
        this.error    = null                         // limpa texto literal
      }

      /* ------------ 500 ------------ */
      else if (status === 500) {
        this.error    = 'O servidor encontrou um erro. Tente mais tarde.'
        this.errorKey = ''
      }

      /* ------------ 404 ------------ */
      else if (status === 404) {
        this.error    = 'Dados não encontrados para estes filtros.'
        this.errorKey = ''
      }

      /* ------------ outros ------------ */
      else {
        this.error    = err.response.data?.detail || err.message || 'Erro ao gerar relatório'
        this.errorKey = ''
      }

      this.reportData = null


    } finally {
        this.loading = false
      }
    },

    exportReport() {
      if (!this.reportData || !this.reportData.items) return;

      // 1. Prepara os dados para exportar
      const data = this.reportData.items.map(item => ({
        Annotator: item.annotator,
        'Dataset Name': item.example,
        Label: item.label,
        Date: item.date,
      }));

      // 2. Cria a worksheet e o workbook
      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Histórico de Anotações');

      // 3. Gera o ficheiro Excel
      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });

      // 4. Faz download
      const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
      saveAs(blob, 'historico_anotacoes.xlsx');
    },

    getLabelColor(labelName: string): string {
      const label = this.labels.find(l => l.text === labelName)
      return label?.backgroundColor || '#ccc'
    },
    getLabelTextColor(labelName: string): string {
      const label = this.labels.find(l => l.text === labelName)
      return label?.textColor || '#000'
    },
    async loadLabels() {
      try {
        const response = await this.$services.categoryType.list(this.$route.params.id)
        this.labels = response.map((item: any) => ({
          text: item.text,
          backgroundColor: item.backgroundColor,
          textColor: item.textColor
        }))
      } catch (error) {
        console.error('Error loading labels:', error)
        this.error = 'Failed to load labels'
      }
    },

    clearDates () {
      this.startDate = this.endDate = null
    }
  },

  async created() {
    await this.loadLabels()
    await this.loadInitialData()
  }
})
</script>