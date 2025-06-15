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

      <!-- Give Answers -->
      <v-btn
        color="success"
        class="ml-4 custom-btn"
        min-width="180"
        height="40"
        :disabled="selected.length !== 1"
        @click="openAnswerDialog"
      >
        <v-icon left class="mr-2">mdi-comment-text</v-icon>
        Give Answers
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

      <!-- Responded -->
      <v-btn
        color="info"
        class="ml-4 custom-btn"
        min-width="180"
        height="40"
        :disabled="selected.length !== 1"
        @click="openRespondedDialog"
      >
        <v-icon left class="mr-2">mdi-account-group</v-icon>
        Responded
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

      <!-- custom cell for title with response status -->
      <template #[`item.title`]="{ item }">
        <div class="d-flex align-center">
          {{ item.title }}
          <v-tooltip v-if="item.hasResponse">
            <template #activator="{ on, attrs }">
              <v-icon
                small
                color="success"
                class="ml-2"
                v-bind="attrs"
                v-on="on"
              >
                mdi-check-circle
              </v-icon>
            </template>
            <span>You have already answered this perspective</span>
          </v-tooltip>
        </div>
      </template>

      <!-- Slot para renderizar as chips das labels -->
      <template #[`item.labelsCustom`]="{ item }">
        <div class="d-flex flex-wrap">
          <v-chip
            v-for="lbl in item.labelsCustom"
            :key="lbl.id"
            :color="chipColor(lbl.data_type)"
            small
            class="ma-1 white--text"
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
          <div v-for="lbl in selectedPerspective.labels" :key="lbl.id" class="detail-item">
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

    <!-- answer dialog -->
    <v-dialog v-model="answerDialog" max-width="800">
      <v-card>
        <v-card-title class="headline primary white--text">
          <v-icon left color="white">mdi-comment-text</v-icon>
          Answer Perspective
        </v-card-title>

        <v-card-text v-if="selectedPerspective" class="pt-4">
          <v-alert
            v-if="error"
            type="error"
            dense
            border="left"
            colored-border
            class="mb-4"
          >
            {{ error }}
          </v-alert>

          <v-form ref="answerForm" v-model="answerFormValid">
            <div v-for="(label, index) in selectedPerspective.labels" :key="index" class="mb-6">
              <v-card outlined class="pa-4">
                <div class="subtitle-1 font-weight-bold mb-2">{{ label.name }}</div>
                
                <!-- String input -->
                <v-text-field
                  v-if="label.data_type === 'string' && answers[label.id]"
                  v-model="answers[label.id].string_value"
                  label="Your answer"
                  :rules="[rules.required]"
                  outlined
                  dense
                />

                <!-- Integer input -->
                <v-text-field
                  v-else-if="label.data_type === 'int' && answers[label.id]"
                  v-model.number="answers[label.id].int_value"
                  type="number"
                  :label="`Enter a number between ${label.int_min} and ${label.int_max}`"
                  :rules="[
                    rules.required,
                    v => v >= label.int_min || `Minimum value is ${label.int_min}`,
                    v => v <= label.int_max || `Maximum value is ${label.int_max}`
                  ]"
                  outlined
                  dense
                />

                <!-- Choice input -->
                <v-radio-group
                  v-else-if="label.data_type === 'choice' && answers[label.id]"
                  v-model="answers[label.id].choice_value"
                  :rules="[rules.required]"
                >
                  <v-radio
                    v-for="option in label.options"
                    :key="option.value"
                    :label="option.value"
                    :value="option.value"
                  />
                </v-radio-group>
              </v-card>
            </div>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn text @click="answerDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="submitting"
            :disabled="!answerFormValid"
            @click="submitAnswers"
          >
            Submit Answers
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- responded dialog -->
    <v-dialog v-model="respondedDialog" max-width="800">
      <v-card>
        <v-card-title class="headline primary white--text">
          <v-icon left color="white">mdi-account-group</v-icon>
          Annotators Responses
        </v-card-title>

        <v-card-text v-if="selectedPerspective" class="pt-4">
          <v-data-table
            :headers="respondedHeaders"
            :items="annotatorsResponses"
            :loading="loadingResponses"
            class="elevation-1"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn text @click="respondedDialog = false">Close</v-btn>
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
      answerDialog: false,
      selectedPerspective: null,
      error: null,
      submitting: false,
      answerFormValid: false,
      answers: {},
      headers: [
        { text: 'Title', value: 'title' },
        { text: 'Labels', value: 'labelsCustom', sortable: false },
        { text: 'Created By', value: 'created_by' },
        { text: 'Created At', value: 'created_at_fmt' }
      ],
      rules: {
        required: v => !!v || 'This field is required'
      },
      respondedDialog: false,
      loadingResponses: false,
      annotatorsResponses: [],
      respondedHeaders: [
        { text: 'Username', value: 'username' },
        { text: 'Response Date', value: 'responseDate' }
      ],
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id
    await this.fetchPerspectives()
    await this.checkResponses()
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
          labelsCustom: p.labels, // novo campo para renderização customizada
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
    },
    async checkResponses() {
      try {
        for (const perspective of this.perspectives) {
          try {
            const resp = await this.$repositories.perspective.getMyResponse(
              this.projectId,
              perspective.id
            )
            perspective.hasResponse = !!(resp && Object.keys(resp).length > 0)
          } catch (e) {
            perspective.hasResponse = false
          }
        }
      } catch (e) {
        console.error('Error checking responses:', e)
      }
    },
    async openAnswerDialog() {
      if (this.selected.length !== 1) return
      try {
        const id = this.selected[0].id
        const perspective = this.perspectives.find(p => p.id === id)
        
        // Check if user has already responded
        try {
          await this.$repositories.perspective.getMyResponse(
            this.projectId,
            id
          )
          this.$toasted.error('You have already answered this perspective')
          return
        } catch (e) {
          // No response found, continue
        }

        this.selectedPerspective = perspective
        this.answers = {}
        this.selectedPerspective.labels.forEach(label => {
          this.answers[label.id] = {
            string_value: null,
            int_value: null,
            choice_value: null
          }
        })
        this.answerDialog = true
      } catch (e) {
        console.error(e)
        this.error = 'Unable to load perspective details.'
      }
    },
    async submitAnswers() {
      if (!this.$refs.answerForm.validate()) return
      this.submitting = true
      this.error = null
      try {
        const answers = this.selectedPerspective.labels.map(label => {
          const answer = this.answers[label.id]
          const obj = { label_id: label.id }
          if (label.data_type === 'string') {
            obj.string_value = answer.string_value
          } else if (label.data_type === 'int') {
            obj.int_value = answer.int_value
          } else if (label.data_type === 'choice') {
            obj.choice_value = answer.choice_value
          }
          return obj
        })
        const payload = {
          perspective: this.selectedPerspective.id,
          answers
        }
        await this.$repositories.perspective.createResponse(
          this.projectId,
          this.selectedPerspective.id,
          payload
        )
        // Se chegou aqui, foi sucesso!
        this.answerDialog = false
        this.answers = {}
        this.selectedPerspective = null
        await this.fetchPerspectives()
        await this.checkResponses()
        this.$toasted.success('Answers submitted successfully')
      } catch (e) {
        console.error('Error submitting answers:', e)
        this.error = 'Failed to submit answers. Please try again.'
      } finally {
        this.submitting = false
      }
    },
    async openRespondedDialog() {
      if (this.selected.length !== 1) return
      try {
        console.log('Abrindo dialog responded');
        this.respondedDialog = true
        this.loadingResponses = true
        const id = this.selected[0].id
        this.selectedPerspective = this.perspectives.find(p => p.id === id)
        console.log('Selected perspective:', this.selectedPerspective)
        const responses = await this.$repositories.perspective.listResponses(
          this.projectId,
          id
        )
        console.log('Respostas recebidas:', responses)
        let responseList = []
        if (responses && Array.isArray(responses.results)) {
          responseList = responses.results
        } else if (Array.isArray(responses)) {
          responseList = responses
        }
        // Agrupar por usuário e pegar a data mais recente
        const userLatestResponse = {}
        responseList.forEach(r => {
          if (!userLatestResponse[r.user] || new Date(r.created_at) > new Date(userLatestResponse[r.user].created_at)) {
            userLatestResponse[r.user] = r
          }
        })
        this.annotatorsResponses = Object.values(userLatestResponse).map(r => ({
          username: r.user,
          responseDate: this.formatDate(r.created_at)
        }))
        console.log('Annotators responses:', this.annotatorsResponses)
      } catch (e) {
        console.error('Erro no openRespondedDialog:', e)
        this.error = 'Unable to load annotators responses: ' + (e.message || 'Unknown error')
      } finally {
        this.loadingResponses = false
      }
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
