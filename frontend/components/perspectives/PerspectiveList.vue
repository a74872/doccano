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
  font-weight
