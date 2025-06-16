<template>
  <v-container>
    <!-- action buttons -->
    <div class="d-flex align-center mb-4">
      <!-- Create -->
      <v-btn
        color="primary"
        class="custom-btn"
        min-width="180"
        height="40"
        @click="goToAdd"
      >
        <v-icon left class="mr-2">mdi-plus</v-icon>
        Create new Perspective
      </v-btn>

      <!-- Delete -->
      <v-btn
        color="error"
        class="ml-4 custom-btn"
        min-width="180"
        height="40"
        :disabled="!selected.length"
        @click="confirmDialog = true"
      >
        <v-icon left class="mr-2">mdi-delete</v-icon>
        Delete Perspective
      </v-btn>

      <!-- View -->
      <v-btn
        color="info"
        class="ml-4 custom-btn"
        min-width="180"
        height="40"
        :disabled="selected.length !== 1"
        @click="openDetailsDialog"
      >
        <v-icon left class="mr-2">mdi-eye</v-icon>
        View Details
      </v-btn>

      <!-- Edit (new) -->
      <v-btn
        color="success"
        class="ml-4 custom-btn"
        min-width="180"
        height="40"
        :disabled="selected.length !== 1"
        @click="openEditDialog"
      >
        <v-icon left class="mr-2">mdi-pencil</v-icon>
        Edit
      </v-btn>
    </div>

    <!-- perspectives table -->
    <v-data-table
      v-if="perspectives.length"
      v-model="selected"
      :headers="headers"
      :items="perspectives"
      item-value="id"
      show-select
      class="elevation-1"
      :items-per-page="10"
      :footer-props="{ 'items-per-page-options':[5,10,15,20], 'items-per-page-text':'Items per page:' }"
    >
      <template #top>
        <v-toolbar flat>
          <v-toolbar-title>Perspectives</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
      </template>

      <!-- custom cell for labels -->
      <template #[`item.labelsCol`]="{ item }">
        <div class="d-flex flex-wrap">
          <v-chip
            v-for="lbl in item.labels"
            :key="lbl.id"
            small
            class="ma-1 white--text"
            :color="chipColor(lbl.data_type)"
          >
            {{ lbl.name }}
          </v-chip>
        </div>
      </template>
    </v-data-table>

    <div v-else class="mt-4 empty-state">No perspective has been found.</div>

    <!-- error alert -->
    <v-alert v-if="error" type="error" dismissible border="left" elevation="2" colored-border class="custom-alert error-alert">
      <v-icon left class="mr-2">mdi-alert-circle</v-icon>
      {{ error }}
    </v-alert>

    <!-- confirm delete dialog -->
    <v-dialog v-model="confirmDialog" max-width="480">
      <v-card>
        <v-card-title class="headline d-flex align-center">
          <v-icon left color="error">mdi-delete</v-icon>
          Delete confirmation
          <v-chip small color="error" class="ml-2">{{ selected.length }} item(s)</v-chip>
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the following perspectives?
          <ul class="pl-4 mt-3">
            <li v-for="item in selected" :key="item.id" class="mb-1">{{ item.title }}</li>
          </ul>
          <v-alert type="warning" dense class="mt-4" border="left" colored-border>
            This action cannot be undone.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey" @click="confirmDialog = false">Cancel</v-btn>
          <v-btn text color="primary" @click="deleteSelectedConfirmed">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- details dialog - IMPROVED DESIGN -->
    <v-dialog v-model="detailsDialog" max-width="800" persistent>
      <v-card class="details-card">
        <!-- Header with gradient background -->
        <v-card-title class="details-header pa-0">
          <div class="header-content">
            <div class="d-flex align-center">
              <div>
                <h2 class="headline mb-1">Perspective Details</h2>
                <p class="subtitle-1 mb-0 opacity-90">Complete information overview</p>
              </div>
            </div>
            <v-btn icon class="close-btn" @click="detailsDialog = false">
              <v-icon color="error">mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-title>

        <v-card-text v-if="selectedPerspective" class="details-body pa-6">
          <!-- Title Section -->
          <div class="details-section">
            <div class="section-header">
              <v-icon class="section-icon" color="primary">mdi-format-title</v-icon>
              <h3 class="section-title">General Information</h3>
            </div>
            <v-card class="info-card" elevation="0">
              <v-card-text class="pa-4">
                <div class="info-grid">
                  <div class="info-item">
                    <div class="info-label">
                      <v-icon small class="mr-2" color="grey darken-1">mdi-tag</v-icon>
                      Title
                    </div>
                    <div class="info-value title-highlight">{{ selectedPerspective.title }}</div>
                  </div>
                  <div class="info-item" v-if="selectedPerspective.description">
                    <div class="info-label">
                      <v-icon small class="mr-2" color="grey darken-1">mdi-text</v-icon>
                      Description
                    </div>
                    <div class="info-value">{{ selectedPerspective.description }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">
                      <v-icon small class="mr-2" color="grey darken-1">mdi-account</v-icon>
                      Created by
                    </div>
                    <div class="info-value">{{ selectedPerspective.created_by || '—' }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">
                      <v-icon small class="mr-2" color="grey darken-1">mdi-calendar</v-icon>
                      Created at
                    </div>
                    <div class="info-value">{{ formatDate(selectedPerspective.created_at) }}</div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <!-- Labels Section -->
          <div class="details-section" v-if="selectedPerspective.labels && selectedPerspective.labels.length">
            <div class="section-header">
              <v-icon class="section-icon" color="secondary">mdi-label-multiple</v-icon>
              <h3 class="section-title">Labels Configuration</h3>
              <v-chip small class="ml-2" color="secondary" outlined>
                {{ selectedPerspective.labels.length }} label(s)
              </v-chip>
            </div>

            <div class="labels-grid">
              <v-card
                v-for="lbl in selectedPerspective.labels"
                :key="lbl.id"
                class="label-card"
                elevation="2"
              >
                <v-card-text class="pa-4">
                  <div class="label-header">
                    <div class="label-name">
                      <v-chip
                        small
                        :color="chipColor(lbl.data_type)"
                        class="white--text label-type-chip"
                      >
                        {{ lbl.data_type }}
                      </v-chip>
                      <span class="label-title">{{ lbl.name }}</span>
                    </div>
                  </div>

                  <v-divider class="my-3"></v-divider>

                  <div class="label-content">
                    <template v-if="lbl.data_type === 'int'">
                      <div class="range-display">
                        <v-icon small class="mr-2" color="deep-purple">mdi-numeric</v-icon>
                        <span class="range-text">
                          Range: <strong>{{ lbl.int_min }}</strong> to <strong>{{ lbl.int_max }}</strong>
                        </span>
                      </div>
                    </template>

                    <template v-else-if="lbl.data_type === 'choice'">
                      <div class="choice-header">
                        <v-icon small class="mr-2" color="blue">mdi-format-list-bulleted</v-icon>
                        <span class="choice-label">Available options:</span>
                      </div>
                      <div class="choice-options">
                        <v-chip
                          v-for="opt in lbl.options"
                          :key="opt.value"
                          small
                          class="choice-chip"
                          color="blue lighten-4"
                          text-color="blue darken-2"
                        >
                          {{ opt.value }}
                        </v-chip>
                      </div>
                    </template>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>

          <!-- Empty state for no labels -->
          <div v-else class="details-section">
            <div class="section-header">
              <v-icon class="section-icon" color="grey">mdi-label-off</v-icon>
              <h3 class="section-title">Labels Configuration</h3>
            </div>
            <v-card class="empty-labels-card" elevation="0">
              <v-card-text class="text-center pa-6">
                <v-icon size="48" color="grey lighten-2" class="mb-3">mdi-label-off-outline</v-icon>
                <p class="grey--text">No labels configured for this perspective</p>
              </v-card-text>
            </v-card>
          </div>
        </v-card-text>

        <v-card-actions class="details-actions pa-6">
          <v-spacer></v-spacer>
          <v-btn
            text
            color="grey darken-1"
            class="mr-2"
            @click="detailsDialog = false"
          >
            Close
          </v-btn>
          <v-btn
            color="primary"
            @click="detailsDialog = false"
            elevation="2"
            class="done-btn"
          >
            Done
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      projectId: null,
      perspectives: [],
      selected: [],
      confirmDialog: false,
      detailsDialog: false,
      selectedPerspective: null,
      error: null,
      headers: [
        { text: 'Title', value: 'title' },
        { text: 'Description', value: 'description' },
        { text: 'Labels', value: 'labelsCol', sortable: false },
        { text: 'Created By', value: 'created_by' },
        { text: 'Created At', value: 'created_at_fmt' }
      ]
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id
    await this.fetchPerspectives()
  },
  methods: {
    openEditDialog () {
      if (this.selected.length !== 1) return
      // navega para página de edição (ou abre um diálogo) – ajuste conforme tiver
      const pid = this.selected[0].id
      this.$router.push(`/projects/${this.projectId}/perspective/${pid}/edit`)
    },
    goToAdd() {
      this.$router.push(`/projects/${this.projectId}/perspective/add`)
    },
    chipColor(type) {
      switch (type) {
        case 'int':
          return 'deep-purple lighten-2'
        case 'choice':
          return 'blue lighten-2'
        default:
          return 'grey'
      }
    },
    async fetchPerspectives() {
      try {
        const response = await this.$repositories.perspective.getPerspectives(this.projectId)
        const items = Array.isArray(response.results) ? response.results : response
        this.perspectives = items.map(p => ({
          ...p,
          labelsCol: p.labels, // for slot column
          created_at_fmt: this.formatDate(p.created_at)
        }))
      } catch (e) {
        console.error(e)
        this.error = 'Unable to load perspectives. See console for details.'
      }
    },
    async deleteSelectedConfirmed() {
      try {
        for (const row of this.selected) {
          await this.$repositories.perspective.deletePerspective(this.projectId, row.id)
        }
        this.perspectives = this.perspectives.filter(row => !this.selected.includes(row))
        this.selected = []
        this.confirmDialog = false
      } catch (e) {
        console.error(e)
        this.error = 'Deletion failed.'
        this.confirmDialog = false
      }
    },
    async openDetailsDialog() {
      if (this.selected.length !== 1) return
      try {
        const id = this.selected[0].id
        this.selectedPerspective = await this.$repositories.perspective.getPerspectiveDetails(this.projectId, id)
        this.detailsDialog = true
      } catch (e) {
        console.error(e)
        this.error = 'Unable to load perspective details.'
      }
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleString('pt-PT') : '—'
    }
  }
}
</script>

<style scoped>
.custom-btn {
  text-transform: none;
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 0 20px;
  box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}
.custom-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}
.empty-state {
  color: rgba(0, 0, 0, 0.38);
  font-style: italic;
  text-align: center;
  padding: 24px;
}

/* IMPROVED DETAILS DIALOG STYLES */
.details-card {
  border-radius: 12px !important;
  overflow: hidden;
}

.details-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  position: relative;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  width: 100%;
}

.close-btn {
  background: transparent !important;
  border: none;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  transform: scale(1.05);
}

.done-btn {
  min-width: 100px;
  text-align: center;
}

.details-body {
  background: #fafafa;
  max-height: 60vh;
  overflow-y: auto;
}

.details-section {
  margin-bottom: 32px;
}

.details-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e0e0;
}

.section-icon {
  margin-right: 12px;
  font-size: 20px !important;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.info-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.title-highlight {
  font-size: 16px !important;
  font-weight: 700 !important;
  color: #1976d2 !important;
}

.labels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.label-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.label-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
}

.label-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.label-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label-type-chip {
  font-size: 10px !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.label-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.label-content {
  margin-top: 8px;
}

.range-display {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f3e5f5;
  border-radius: 8px;
  border-left: 4px solid #9c27b0;
}

.range-text {
  font-size: 14px;
  color: #4a148c;
}

.choice-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #1976d2;
}

.choice-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.choice-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.choice-chip {
  font-size: 12px !important;
  font-weight: 500 !important;
  transition: all 0.2s ease;
}

.choice-chip:hover {
  transform: scale(1.05);
}

.empty-labels-card {
  background: white;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
}

.details-actions {
  background: white;
  border-top: 1px solid #e0e0e0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-content {
    padding: 16px 20px;
  }

  .details-body {
    padding: 16px !important;
  }

  .labels-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    gap: 12px;
  }

  .details-section {
    margin-bottom: 24px;
  }
}
</style>