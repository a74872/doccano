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

      <!-- Edit (moved next to Create) -->
      <v-btn
        color="success"
        class="ml-4 custom-btn edit-btn"
        min-width="180"
        height="40"
        :disabled="selected.length !== 1"
        @click="openEditDialog"
      >
        <v-icon left class="mr-2">mdi-pencil</v-icon>
        Edit
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
      <template v-slot:[`item.labelsCol`]="{ item }">
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

    <!-- IMPROVED confirm delete dialog -->
    <v-dialog v-model="confirmDialog" max-width="520" persistent>
      <v-card class="delete-dialog-card">
        <!-- Enhanced Header -->
        <v-card-title class="delete-dialog-header pa-0">
          <div class="delete-header-content">
            <div class="delete-icon-container">
              <v-icon size="28" color="white">mdi-delete-alert</v-icon>
            </div>
            <div class="delete-title-section">
              <h3 class="delete-title">Confirm Deletion</h3>
              <div class="delete-subtitle">
                {{ selected.length }} {{ selected.length === 1 ? 'perspective' : 'perspectives' }} selected
              </div>
            </div>
          </div>
        </v-card-title>

        <!-- Enhanced Content -->
        <v-card-text class="delete-dialog-content">
          <div class="delete-message">
            <p class="mb-3">You are about to permanently delete the following {{ selected.length === 1 ? 'perspective' : 'perspectives' }}:</p>

            <!-- Enhanced list with better styling -->
            <div class="perspectives-list">
              <div
                v-for="(item, index) in selected"
                :key="item.id"
                class="perspective-item"
                :class="{ 'mb-2': index < selected.length - 1 }"
              >
                <div class="perspective-item-content">
                  <v-icon small color="error" class="mr-2">mdi-file-document</v-icon>
                  <span class="perspective-name">{{ item.title }}</span>
                  <v-chip x-small color="grey lighten-2" class="ml-2">
                    {{ item.labels?.length || 0 }} {{ item.labels?.length === 1 ? 'label' : 'labels' }}
                  </v-chip>
                </div>
              </div>
            </div>

            <!-- Enhanced warning -->
            <v-alert
              type="error"
              dense
              class="mt-4 delete-warning"
              border="left"
              colored-border
              icon="mdi-alert-circle"
            >
              <div class="warning-content">
                <strong>This action cannot be undone!</strong>
                <br>
                <small>All associated data will be permanently removed.</small>
              </div>
            </v-alert>
          </div>
        </v-card-text>

        <!-- Enhanced Actions -->
        <v-card-actions class="delete-dialog-actions">
          <v-spacer></v-spacer>
          <v-btn
            text
            color="grey darken-1"
            class="cancel-btn"
            @click="cancelDelete"
          >
            <v-icon left small>mdi-close</v-icon>
            Cancel
          </v-btn>
          <v-btn
            color="error"
            class="confirm-delete-btn"
            @click="deleteSelectedConfirmed"
          >
            <v-icon left small>mdi-delete</v-icon>
            Delete {{ selected.length === 1 ? 'Perspective' : 'Perspectives' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- details dialog -->
    <v-dialog v-model="detailsDialog" max-width="640">
      <v-card>
        <v-card-title class="headline primary white--text">Perspective details</v-card-title>
        <v-card-text v-if="selectedPerspective" class="details-content">
          <div class="detail-item">
            <span class="detail-label">Title:</span>
            <span class="detail-value title-value">{{ selectedPerspective.title }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Created by:</span>
            <span class="detail-value">{{ selectedPerspective.created_by || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Created at:</span>
            <span class="detail-value">{{ formatDate(selectedPerspective.created_at) }}</span>
          </div>
          <div class="detail-item" v-for="lbl in selectedPerspective.labels" :key="lbl.id">
            <span class="detail-label">{{ lbl.name }} ({{ lbl.data_type }})</span>
            <span class="detail-value">
              <template v-if="lbl.data_type==='int'">
                {{ lbl.int_min }} – {{ lbl.int_max }}
              </template>
              <template v-else-if="lbl.data_type==='choice'">
                <v-chip
                  v-for="opt in lbl.options"
                  :key="opt.value"
                  small
                  class="ma-1"
                  color="grey lighten-3"
                >
                  {{ opt.value }}
                </v-chip>
              </template>
            </span>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- snackbar para mensagens de sucesso/erro -->
    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      top
      timeout="4000"
    >
      {{ snackbar.text }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.visible = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
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
      ],
      snackbar: {
        visible: false,
        text: '',
        color: 'success'
      }
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id
    await this.fetchPerspectives()
  },
  methods: {
    showSnack(text, color = 'success') {
      this.snackbar.text = text
      this.snackbar.color = color
      this.snackbar.visible = true
    },
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
        this.showSnack(`Perspective${this.selected.length > 1 ? 's' : ''} deleted successfully`)
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
    },
    cancelDelete() {
      this.confirmDialog = false
      this.showSnack('Perspective deletion cancelled', 'error')
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

/* Enhanced styling for the Edit button */
.edit-btn {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%) !important;
  border: none;
  position: relative;
  overflow: hidden;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.edit-btn:before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.edit-btn:hover:before {
  left: 100%;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%) !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
}

.edit-btn:disabled {
  background: #e0e0e0 !important;
  color: #9e9e9e !important;
  transform: none !important;
  box-shadow: none !important;
}

.empty-state {
  color: rgba(0, 0, 0, 0.38);
  font-style: italic;
  text-align: center;
  padding: 24px;
}

.details-content {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
}

.detail-label {
  min-width: 140px;
  font-weight: 600;
  color: #555;
}

.detail-value {
  flex: 1;
}

.title-value {
  font-weight: 700;
  margin-left: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}
.detail-label {
  font-weight: 600;
  color: #555;
}

/* NEW ENHANCED DELETE DIALOG STYLES */
.delete-dialog-card {
  border-radius: 12px !important;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
}

.delete-dialog-header {
  background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
  color: white;
}

.delete-header-content {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  width: 100%;
}

.delete-icon-container {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  backdrop-filter: blur(10px);
}

.delete-title-section {
  flex: 1;
}

.delete-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  line-height: 1.2;
}

.delete-subtitle {
  font-size: 0.875rem;
  opacity: 0.9;
  margin-top: 4px;
  font-weight: 400;
}

.delete-dialog-content {
  padding: 24px !important;
  background: #fafafa;
}

.delete-message {
  color: #424242;
  line-height: 1.5;
}

.perspectives-list {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  max-height: 200px;
  overflow-y: auto;
}

.perspective-item {
  transition: all 0.2s ease;
}

.perspective-item:hover {
  transform: translateX(4px);
}

.perspective-item-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.perspective-item:last-child .perspective-item-content {
  border-bottom: none;
}

.perspective-name {
  font-weight: 500;
  color: #424242;
  flex: 1;
}

.delete-warning {
  border-radius: 8px !important;
  background: #ffebee !important;
}

.warning-content {
  line-height: 1.4;
}

.delete-dialog-actions {
  padding: 16px 24px 24px 24px !important;
  background: white;
}

.cancel-btn {
  text-transform: none;
  font-weight: 500;
  padding: 8px 20px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.confirm-delete-btn {
  text-transform: none;
  font-weight: 600;
  padding: 8px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
  transition: all 0.2s ease;
}

.confirm-delete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(211, 47, 47, 0.4);
}
</style>