<template>
  <v-container>
    <!-- Page title -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Reports</h1>
      </v-col>
    </v-row>

    <!-- Filters Section -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-filter</v-icon>
        Filters
      </v-card-title>
      <v-card-text>
        <v-row>
          <!-- Date Filter -->
          <v-col cols="12" md="4">
            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              offset-y
              max-width="290px"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  :value="dateRangeText"
                  label="Filter by Date"
                  prepend-icon="mdi-calendar"
                  readonly
                  outlined
                  dense
                  v-bind="attrs"
                  v-on="on"
                />
              </template>
              <v-date-picker
                v-model="selectedDates"
                range
                @input="dateMenu = false"
              />
            </v-menu>
          </v-col>

          <!-- User Filter -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedUser"
              :items="userOptions"
              label="Filter by User"
              prepend-icon="mdi-account"
              outlined
              dense
              clearable
              :loading="loadingUsers"
            />
          </v-col>

          <!-- Label Filter -->
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedLabel"
              :items="labelOptions"
              label="Filter by Label"
              prepend-icon="mdi-tag"
              outlined
              dense
              clearable
              :loading="loadingLabels"
            />
          </v-col>
        </v-row>

        <!-- Action Buttons -->
        <v-row>
          <v-col cols="12" class="text-right">
            <v-btn
              color="grey"
              text
              class="mr-2"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
            <v-btn
              color="primary"
              :loading="loading"
              @click="generateReport"
            >
              <v-icon left>mdi-chart-line</v-icon>
              Generate Report
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Results Section -->
    <v-card v-if="reportData">
      <v-card-title>
        Report Results
        <v-spacer />
        <v-btn
          color="success"
          small
          :disabled="!reportData || !reportData.length"
          :loading="exportLoading"
          @click="exportReport"
        >
          <v-icon left small>mdi-download</v-icon>
          Export
        </v-btn>
      </v-card-title>
      <v-card-text>
        <!-- Summary Cards -->
        <v-row class="mb-4">
          <v-col cols="12" sm="6" md="3">
            <v-card color="primary" dark>
              <v-card-text>
                <div class="text-h6">{{ totalAnnotations }}</div>
                <div>Total Annotations</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="success" dark>
              <v-card-text>
                <div class="text-h6">{{ uniqueUsers }}</div>
                <div>Active Users</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="info" dark>
              <v-card-text>
                <div class="text-h6">{{ uniqueLabels }}</div>
                <div>Different Labels</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="warning" dark>
              <v-card-text>
                <div class="text-h6">{{ dateRange }}</div>
                <div>Period</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Data Table -->
        <v-data-table
          :headers="headers"
          :items="reportData"
          :loading="loading"
          :items-per-page="10"
          class="elevation-1"
        >
          <template #[`item.date`]="{ item }">
            {{ formatDate(item.date) }}
          </template>
          <template #[`item.label`]="{ item }">
            <v-chip
              small
              :color="getLabelColor(item.label)"
              :text-color="getLabelTextColor(item.label)"
            >
              {{ item.label }}
            </v-chip>
          </template>
          <template #[`item.user`]="{ item }">
            {{ getUserDisplayName(item.user) }}
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- No Data Message -->
    <v-card v-else-if="!loading && hasSearched">
      <v-card-text class="text-center py-8">
        <v-icon size="64" color="grey lighten-1">mdi-database-search</v-icon>
        <div class="text-h6 grey--text mt-4">No data found</div>
        <div class="grey--text">Try adjusting the filters and generate again</div>
      </v-card-text>
    </v-card>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      bottom
      right
    >
      <v-icon left dark>{{ snackbar.icon }}</v-icon>
      {{ snackbar.message }}
      <template #action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'ProjectReports',
  
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      // Filters
      dateMenu: false,
      selectedDates: [],
      selectedUser: null,
      selectedLabel: null,
      
      // Loading states
      loading: false,
      loadingUsers: false,
      loadingLabels: false,
      exportLoading: false,
      
      // Data
      reportData: null,
      userOptions: [],
      labelOptions: [],
      members: [],
      labels: [],
      
      // State
      hasSearched: false,
      
      // Snackbar
      snackbar: {
        show: false,
        message: '',
        color: 'success',
        icon: 'mdi-check-circle',
        timeout: 5000
      },
      
      // Table headers
      headers: [
        { text: 'Date', value: 'date', sortable: true },
        { text: 'User', value: 'user', sortable: true },
        { text: 'Label', value: 'label', sortable: true },
        { text: 'Dataset', value: 'dataset', sortable: true },
        { text: 'Document', value: 'document', sortable: true }
      ]
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),

    projectId() {
      return this.$route.params.id
    },

    dateRangeText() {
      if (!this.selectedDates || this.selectedDates.length === 0) {
        return 'Select period'
      }
      if (this.selectedDates.length === 1) {
        return this.selectedDates[0]
      }
      return `${this.selectedDates[0]} to ${this.selectedDates[1]}`
    },

    totalAnnotations() {
      return this.reportData ? this.reportData.length : 0
    },

    uniqueUsers() {
      if (!this.reportData) return 0
      return new Set(this.reportData.map(item => item.user)).size
    },

    uniqueLabels() {
      if (!this.reportData) return 0
      return new Set(this.reportData.map(item => item.label)).size
    },

    dateRange() {
      if (!this.reportData || this.reportData.length === 0) return '-'
      const dates = this.reportData.map(item => new Date(item.date)).sort()
      const firstDate = dates[0]
      const lastDate = dates[dates.length - 1]
      
      if (firstDate.toDateString() === lastDate.toDateString()) {
        return this.formatDate(firstDate)
      }
      return `${this.formatDate(firstDate)} - ${this.formatDate(lastDate)}`
    }
  },

  async mounted() {
    await this.loadFiltersData()
  },

  methods: {
    showSnackbar(message, color = 'success', icon = 'mdi-check-circle', timeout = 5000) {
      this.snackbar = {
        show: true,
        message,
        color,
        icon,
        timeout
      }
    },

    async loadFiltersData() {
      try {
        // Load users and labels in parallel
        await Promise.all([
          this.loadUsers(),
          this.loadLabels()
        ])
      } catch (error) {
        this.showSnackbar('Error loading filter data', 'error', 'mdi-alert-circle')
        console.error(error)
      }
    },

    async loadUsers() {
      try {
        this.loadingUsers = true
        
        // Use the same API call as in the other component
        this.members = await this.$repositories.member.list(this.projectId)
        
        // Transform to select options
        this.userOptions = this.members.map(member => ({
          text: member.username || member.email || `User ${member.id}`,
          value: String(member.id)          // <- garante string
        }))
      } catch (error) {
        console.error('Error loading users:', error)
        // Fallback to empty array if API fails
        this.userOptions = []
      } finally {
        this.loadingUsers = false
      }
    },

    async loadLabels() {
      try {
        this.loadingLabels = true
        
        // Use the same API call as in the other component
        this.labels = await this.$services.categoryType.list(this.projectId)
        
        // Transform to select options
        this.labelOptions = this.labels.map(label => ({
          text: label.text,
          value: label.text
        }))
        
      } catch (error) {
        console.error('Error loading labels:', error)
        // Fallback to empty array if API fails
        this.labelOptions = []
      } finally {
        this.loadingLabels = false
      }
    },

    async generateReport() {
      this.loading = true
      this.hasSearched = true

      try {
        // Build query parameters - mantemos apenas filtros que a API suporta
        const query = {}
        
        if (this.selectedLabel) {
          query.label = this.selectedLabel
        }

        // Get examples with filters
        const exampleList = await this.$services.example.list(this.projectId, query)
        
        // Transform the data for the report (aplicamos todos os filtros localmente)
        this.reportData = await this.transformExampleData(exampleList.items)

        if (this.reportData.length === 0) {
          this.showSnackbar(
            'No annotations found with the applied filters. Try adjusting the search criteria.',
            'warning',
            'mdi-alert',
            6000
          )
        } else {
          this.showSnackbar(
            `Report generated successfully! Found ${this.reportData.length} annotations.`,
            'success',
            'mdi-check-circle'
          )
        }

      } catch (error) {
        this.showSnackbar(
          'Database error while generating report. Check connection and try again.',
          'error',
          'mdi-database-alert',
          8000
        )
        console.error(error)
        this.reportData = []
      } finally {
        this.loading = false
      }
    },

    /* -------- transformExampleData -------- */
    async transformExampleData(examples) {
      const reportData = [];

      for (const example of examples) {
        try {
          const distribution =
            await this.$repositories.metrics.fetchCategoryDistribution(
              this.projectId,
              { example: example.id }
            );

          // Percorre cada utilizador
          for (const uidStr in distribution) {
            // Converte se for numérico; caso contrário fica string
            const uidNum = Number(uidStr);
            const uid = Number.isNaN(uidNum) ? uidStr : uidNum;

            // Filtro de utilizador (só compara se o uid for numérico)
            if (
              this.selectedUser !== null &&
              !Number.isNaN(uidNum) &&
              uid !== this.selectedUser
            ) {
              continue;
            }

            const userLabels = distribution[uidStr];

            // Entradas por label
            for (const [labelName, count] of Object.entries(userLabels)) {
              if (this.selectedLabel && labelName !== this.selectedLabel) {
                continue;
              }

              for (let i = 0; i < count; i++) {
                const annotationDate =
                  example.createdAt ||
                  new Date().toISOString().split("T")[0];

                // ----- filtro de datas -----
                if (this.selectedDates && this.selectedDates.length > 0) {
                  const exampleDate = new Date(annotationDate);
                  const startDate = new Date(this.selectedDates[0]);

                  if (this.selectedDates.length === 1) {
                    const selDate = new Date(this.selectedDates[0]);
                    if (
                      exampleDate.toDateString() !== selDate.toDateString()
                    ) {
                      continue;
                    }
                  } else if (this.selectedDates.length === 2) {
                    const endDate = new Date(this.selectedDates[1]);
                    if (exampleDate < startDate || exampleDate > endDate) {
                      continue;
                    }
                  }
                }
                // ----- fim filtro de datas -----

                reportData.push({
                  id: `${example.id}-${uid}-${labelName}-${i}`,
                  date: annotationDate,
                  user: uid,                // pode ser number OU string
                  label: labelName,
                  dataset: this.project.name || "Dataset",
                  document: example.text
                    ? example.text.length > 50
                      ? example.text.substring(0, 50) + "..."
                      : example.text
                    : example.filename || `Doc_${example.id}`,
                });
              }
            }
          }
        } catch (err) {
          console.error(`Error processing example ${example.id}:`, err);
        }
      }

      return reportData;
    },

    /* -------- getUserDisplayName -------- */
    getUserDisplayName(userId) {
      // Tenta procurar pelo ID numérico
      const numericId = Number(userId);
      const member = Number.isNaN(numericId)
        ? null
        : this.members.find((m) => m.id === numericId);

      if (member) {
        return member.username || member.email || `User ${numericId}`;
      }

      // Se não encontrar e for string (ex.: "aggregated", "global" …)
      if (Number.isNaN(numericId)) {
        return userId;            // devolve a string original
      }

      // Último recurso
      return `User ${numericId}`;
    },

    clearFilters() {
      this.selectedDates = []
      this.selectedUser = null
      this.selectedLabel = null
      this.reportData = null
      this.hasSearched = false
      this.showSnackbar('Filters cleared successfully', 'info', 'mdi-filter-remove')
    },

    exportReport() {
      if (!this.reportData || this.reportData.length === 0) return

      try {
        this.exportLoading = true

        // Generate timestamp for filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0]
        const timeString = new Date().toLocaleTimeString('pt-PT', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }).replace(':', 'h')

        // Enhanced CSV formatting
        const headers = [
          'Date',
          'User', 
          'Label',
          'Dataset',
          'Document',
          'Annotation ID'
        ]
        
        // Add BOM for proper UTF-8 encoding in Excel
        const BOM = '\uFEFF'
        
        const csvRows = this.reportData.map(row => [
          this.formatDateForExport(row.date),
          this.getUserDisplayName(row.user),
          row.label,
          row.dataset,
          this.cleanTextForCSV(row.document),
          row.id
        ])

        // Create CSV content with proper formatting
        const csvContent = BOM + [
          headers.join(';'), // Use semicolon for better Excel compatibility
          ...csvRows.map(row => 
            row.map((cell, index) => {
              // Special handling for date column (index 0)
              if (index === 0) {
                return cell // Don't wrap date in quotes for better Excel recognition
              }
              return `"${String(cell).replace(/"/g, '""')}"`
            }).join(';')
          )
        ].join('\n')

        // Enhanced filename
        const projectName = this.project.name ? 
          this.project.name.replace(/[^a-zA-Z0-9]/g, '_') : 'Dataset'
        const filename = `Report_${projectName}_${timestamp}_${timeString}.csv`

        // Create and download file
        const blob = new Blob([csvContent], { 
          type: 'text/csv;charset=utf-8;' 
        })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        
        link.setAttribute('href', url)
        link.setAttribute('download', filename)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up
        URL.revokeObjectURL(url)

        this.showSnackbar(
          `Report exported successfully! File: ${filename}`,
          'success',
          'mdi-download'
        )

      } catch (error) {
        console.error('Export error:', error)
        this.showSnackbar(
          'Error exporting report. Please try again.',
          'error',
          'mdi-export-off',
          6000
        )
      } finally {
        this.exportLoading = false
      }
    },

    formatDate(date) {
      if (typeof date === 'string') {
        date = new Date(date)
      }
      return date.toLocaleDateString('pt-PT')
    },

    formatDateForExport(date) {
      if (typeof date === 'string') {
        date = new Date(date)
      }
      // Format as DD/MM/YYYY HH:MM for better CSV compatibility
      const day = date.getDate().toString().padStart(2, '0')
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const year = date.getFullYear()
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      
      return `${day}/${month}/${year} ${hours}:${minutes}`
    },

    cleanTextForCSV(text) {
      if (!text) return ''
      return text
        .replace(/[\r\n]+/g, ' ') // Replace line breaks with spaces
        .replace(/\s+/g, ' ')     // Replace multiple spaces with single space
        .trim()
    },

    getLabelColor(labelText) {
      const label = this.labels.find(l => l.text === labelText)
      return label ? label.backgroundColor : 'primary'
    },

    getLabelTextColor(labelText) {
      const label = this.labels.find(l => l.text === labelText)
      return label ? label.textColor : 'white'
    },
  }
}
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.text-h6 {
  font-size: 1.25rem !important;
  font-weight: 500;
}
</style>