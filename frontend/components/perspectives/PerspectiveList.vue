<template>
  <v-container>
    <!-- action buttons -->
    <div class="d-flex align-center mb-4">
      <v-btn color="primary" class="custom-btn" min-width="180" height="40"
             @click="$router.push(`/projects/${projectId}/perspective/add`)">
        <v-icon left class="mr-2">mdi-plus</v-icon>
        Create new Perspective
      </v-btn>

      <v-btn color="error" class="ml-4 custom-btn" min-width="180" height="40"
             :disabled="!selected.length" @click="confirmDialog = true">
        <v-icon left class="mr-2">mdi-delete</v-icon>
        Delete Perspective
      </v-btn>

      <v-btn color="info" class="ml-4 custom-btn" min-width="180" height="40"
             :disabled="selected.length !== 1" @click="openDetailsDialog">
        <v-icon left class="mr-2">mdi-eye</v-icon>
        View Details
      </v-btn>
    </div>

    <!-- perspectives table -->
    <v-data-table v-if="perspectives.length"
                  v-model="selected" :headers="headers" :items="perspectives"
                  item-value="id" show-select class="elevation-1"
                  :items-per-page="10"
                  :footer-props="{
                    'items-per-page-options':[5,10,15,20],
                    'items-per-page-text':'Items per page:'
                  }">
      <template #top>
        <v-toolbar flat>
          <v-toolbar-title>Perspectives</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
      </template>
    </v-data-table>

    <div v-else class="mt-4 empty-state">No perspective has been found.</div>

    <!-- error alert -->
    <v-alert v-if="error" type="error" dismissible border="left" elevation="2"
             colored-border class="custom-alert error-alert">
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
            <li v-for="item in selected" :key="item.id">{{ item.title }}</li>
          </ul>
          <v-alert type="warning" dense class="mt-4" border="left" colored-border>
            This action cannot be undone.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey" @click="confirmDialog=false">Cancel</v-btn>
          <v-btn text color="primary" @click="deleteSelectedConfirmed">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- details dialog -->
    <v-dialog v-model="detailsDialog" max-width="640">
      <v-card>
        <v-card-title class="headline primary white--text">Perspective details</v-card-title>
        <v-card-text v-if="selectedPerspective" class="details-content">
          <div class="detail-item"><span class="detail-label">Title:</span>{{ selectedPerspective.title }}</div>
          <div class="detail-item"><span class="detail-label">Created by:</span>{{ selectedPerspective.created_by || '—' }}</div>
          <div class="detail-item"><span class="detail-label">Created at:</span>{{ formatDate(selectedPerspective.created_at) }}</div>
          <div class="detail-item" v-for="lbl in selectedPerspective.labels" :key="lbl.id">
            <span class="detail-label">{{ lbl.name }} ({{ lbl.data_type }})</span>
            <span>
              <template v-if="lbl.data_type==='int'">{{ lbl.int_min }} – {{ lbl.int_max }}</template>
              <template v-else-if="lbl.data_type==='choice'">{{ lbl.options.map(o=>o.value).join(', ') }}</template>
            </span>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="detailsDialog=false">Close</v-btn>
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
        { text: 'Labels', value: 'labelsStr', sortable: false },
        { text: 'Created By', value: 'created_by' },
        { text: 'Created At', value: 'created_at' }
      ]
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id
    await this.fetchPerspectives()
  },
  methods: {
    async fetchPerspectives() {
      try {
        const response = await this.$repositories.perspective.getPerspectives(this.projectId)
        const items = Array.isArray(response.results) ? response.results : response
        this.perspectives = items.map(p => ({
          ...p,
          labelsStr: p.labels.map(l => l.name).join(', ')
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
      return date ? new Date(date).toLocaleString() : '—'
    }
  }
}
</script>

<style scoped>
.custom-btn { text-transform:none;font-weight:500;letter-spacing:.5px;padding:0 20px;box-shadow:0 3px 5px rgba(0,0,0,.1);transition:all .3s ease; }
.custom-btn:hover { transform:translateY(-1px);box-shadow:0 4px 6px rgba(0,0,0,.15); }
.empty-state { color:rgba(0,0,0,.38);font-style:italic;text-align:center;padding:24px; }
.details-content { padding:20px;background:#f8f9fa;border-radius:4px; }
.detail-item { display:flex;justify-content:space-between;margin-bottom:12px; }
.detail-label { font-weight:500;margin-right:8px; }
.custom-alert { margin:16px 0 !important;border-radius:8px !important; }
</style>
