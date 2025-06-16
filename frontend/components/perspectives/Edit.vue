<template>
  <v-container class="form-container">
    <v-card class="form-card">
      <!-- Enhanced header -->
      <v-card-title class="header">
        <v-icon left color="white" size="24">mdi-pencil</v-icon>
        Edit Perspective
      </v-card-title>

      <!-- body -->
      <v-card-text class="form-content">
        <v-alert
          v-if="error"
          type="error"
          dense
          border="left"
          colored-border
          class="mb-4 modern-alert"
        >
          {{ error }}
        </v-alert>

        <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="submitForm">
          <!-- title -->
          <div class="input-section">
            <v-text-field
              v-model.trim="form.title"
              label="Perspective Title"
              :rules="[rules.required]"
              outlined
              dense
              prepend-inner-icon="mdi-format-title"
              class="modern-input"
            />
          </div>

          <v-divider class="section-divider" />

          <!-- labels list -->
          <div class="labels-section">
            <div class="section-header">
              <h3 class="section-title">
                <v-icon left color="primary">mdi-tag-multiple</v-icon>
                Data Labels
              </h3>
              <v-chip small color="primary" outlined>
                {{ form.labels.length }}/7
              </v-chip>
            </div>

            <div class="labels-list">
              <v-card
                v-for="(lbl, idx) in form.labels"
                :key="idx"
                class="label-card"
                outlined
                elevation="2"
              >
                <div class="label-header">
                  <div class="label-number">{{ idx + 1 }}</div>
                  <span class="label-title">Label {{ idx + 1 }}</span>
                  <v-spacer />
                  <v-btn
                    icon
                    small
                    v-if="form.labels.length > 1"
                    @click="removeLabel(idx)"
                    class="delete-btn"
                  >
                    <v-icon small color="error">mdi-delete</v-icon>
                  </v-btn>
                </div>

                <v-divider class="my-3" />

                <div class="label-form">
                  <v-text-field
                    v-model.trim="lbl.name"
                    label="Label name"
                    :rules="[rules.required]"
                    outlined
                    dense
                    class="modern-input mb-3"
                  />

                  <v-select
                    v-model="lbl.data_type"
                    :items="dataTypes"
                    label="Data type"
                    item-text="text"
                    item-value="value"
                    outlined
                    dense
                    class="modern-input mb-3"
                    @change="onTypeChange(idx)"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon small :color="getTypeColor(lbl.data_type)">
                        {{ getTypeIcon(lbl.data_type) }}
                      </v-icon>
                    </template>
                  </v-select>

                  <!-- integer rules -->
                  <div v-if="lbl.data_type==='int'" class="range-section">
                    <div class="range-header">
                      <v-icon small color="info">mdi-numeric</v-icon>
                      <span class="range-label">Number Range</span>
                    </div>
                    <div class="range-inputs">
                      <v-text-field
                        v-model.number="lbl.int_min"
                        label="Min"
                        type="number"
                        class="range-field"
                        outlined
                        dense
                      />
                      <span class="range-separator">to</span>
                      <v-text-field
                        v-model.number="lbl.int_max"
                        label="Max"
                        type="number"
                        outlined
                        dense
                        class="range-field"
                      />
                    </div>
                  </div>

                  <!-- choice options -->
                  <div v-if="lbl.data_type==='choice'" class="options-section">
                    <div class="options-header">
                      <v-icon small color="success">mdi-format-list-bulleted</v-icon>
                      <span class="options-label">Options</span>
                      <v-chip x-small color="success" outlined>
                        {{ lbl.options.filter(o => o.trim()).length }}/4
                      </v-chip>
                    </div>
                    <div class="options-list">
                      <div
                        v-for="(opt,optIdx) in lbl.options"
                        :key="optIdx"
                        class="option-row"
                      >
                        <v-text-field
                          v-model.trim="lbl.options[optIdx]"
                          :label="`Option ${optIdx+1}`"
                          outlined
                          dense
                          class="option-input"
                        />
                        <v-btn
                          icon
                          small
                          class="option-delete-btn"
                          v-if="lbl.options.length>1"
                          @click="removeOption(idx,optIdx)"
                        >
                          <v-icon small color="error">mdi-close</v-icon>
                        </v-btn>
                      </div>
                    </div>
                    <v-btn
                      small
                      text
                      color="success"
                      :disabled="lbl.options.length>=4"
                      @click="addOption(idx)"
                      class="add-option-btn"
                    >
                      <v-icon left small>mdi-plus</v-icon>
                      Add option
                    </v-btn>
                  </div>
                </div>
              </v-card>
            </div>

            <v-btn
              color="primary"
              outlined
              large
              :disabled="form.labels.length>=7"
              @click="addLabel"
              class="add-label-btn"
            >
              <v-icon left>mdi-plus</v-icon>
              Add label
            </v-btn>
          </div>
        </v-form>
      </v-card-text>

      <!-- Enhanced footer -->
      <v-card-actions class="actions-container">
        <v-btn
          outlined
          color="grey darken-1"
          large
          @click="$router.back()"
          class="action-btn"
        >
          <v-icon left>mdi-arrow-left</v-icon>
          Back
        </v-btn>
        <v-spacer />
        <v-btn 
          color="success" 
          large
          :loading="loading" 
          @click="submitForm"
          class="action-btn save-btn"
        >
          <v-icon left>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </v-card-actions>
      <v-progress-linear v-if="loading" indeterminate color="primary" />
    </v-card>

    <!-- Snackbar for messages -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      top
      right
    >
      <v-icon left color="white">{{ snackbar.icon }}</v-icon>
      {{ snackbar.message }}
      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
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
export default {
  props: {
    perspective: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      projectId: this.$route.params.id,
      perspectiveId: this.$route.params.pid,
      loading: false,
      valid: true,
      error: null,
      form: {
        title: '',
        labels: []
      },
      dataTypes: [
        { text: 'Texto livre', value: 'string' },
        { text: 'Número inteiro', value: 'int' },
        { text: 'Opção de lista', value: 'choice' }
      ],
      rules: {
        required: (v) => !!v || 'Campo obrigatório'
      },
      snackbar: {
        show: false,
        message: '',
        color: 'success',
        icon: 'mdi-check-circle',
        timeout: 5000
      }
    }
  },
  created() {
    console.log('route params', this.$route.params)

    if (this.perspective) {
      this.populateForm(this.perspective)
    } else {
      this.fetchPerspective()
    }
  },
  methods: {
    populateForm(p) {
      this.form.title = p.title
      this.form.labels = p.labels.map((l) => ({
        name: l.name,
        data_type: l.data_type,
        int_min: l.int_min,
        int_max: l.int_max,
        options: l.options?.map((o) => o.value) || ['']
      }))
    },
    async fetchPerspective() {
      try {
        const p = await this.$repositories.perspective.getPerspectiveDetails(
          this.projectId,
          this.perspectiveId
        )
        this.populateForm(p)
      } catch (e) {
        this.showErrorMessage('Failed to load perspective. Please try again.')
        console.error(e)
      }
    },
    newLabel() {
      return {
        name: '',
        data_type: 'string',
        int_min: null,
        int_max: null,
        options: ['']
      }
    },
    addLabel() {
      if (this.form.labels.length < 7) {
        this.form.labels.push(this.newLabel())
        this.showSuccessMessage('New label added successfully!')
      }
    },
    removeLabel(i) {
      this.form.labels.splice(i, 1)
      this.showSuccessMessage('Label removed successfully!')
    },
    onTypeChange(i) {
      const l = this.form.labels[i]
      if (l.data_type === 'int') {
        l.options = ['']
      } else if (l.data_type === 'choice') {
        l.int_min = null
        l.int_max = null
        if (!l.options.length) l.options = ['']
      } else {
        l.int_min = null
        l.int_max = null
        l.options = ['']
      }
    },
    addOption(i) {
      const o = this.form.labels[i].options
      if (o.length < 4) {
        o.push('')
        this.showSuccessMessage('New option added successfully!')
      }
    },
    removeOption(i, oi) {
      this.form.labels[i].options.splice(oi, 1)
      this.showSuccessMessage('Option removed successfully!')
    },
    getTypeIcon(type) {
      const icons = {
        string: 'mdi-format-text',
        int: 'mdi-numeric',
        choice: 'mdi-format-list-bulleted'
      }
      return icons[type] || 'mdi-help'
    },
    getTypeColor(type) {
      const colors = {
        string: 'blue',
        int: 'orange',
        choice: 'green'
      }
      return colors[type] || 'grey'
    },
    async submitForm() {
      if (!this.$refs.form.validate()) {
        this.showErrorMessage('Please fill in all required fields correctly.')
        return
      }

      // Validate at least one label exists
      if (this.form.labels.length === 0) {
        this.showErrorMessage('Please add at least one data label.')
        return
      }

      // Validate choice options
      for (let i = 0; i < this.form.labels.length; i++) {
        const label = this.form.labels[i]
        if (label.data_type === 'choice') {
          const validOptions = label.options.filter(o => o.trim())
          if (validOptions.length < 2) {
            this.showErrorMessage(`Label "${label.name}" must have at least 2 options.`)
            return
          }
        }
        if (label.data_type === 'int') {
          if (label.int_min !== null && label.int_max !== null && label.int_min >= label.int_max) {
            this.showErrorMessage(`Label "${label.name}": minimum value must be less than maximum value.`)
            return
          }
        }
      }

      this.loading = true
      const payload = {
        title: this.form.title.trim(),
        labels: this.form.labels.map((l) => {
          const base = { name: l.name.trim(), data_type: l.data_type }
          if (l.data_type === 'int') {
            base.int_min = l.int_min
            base.int_max = l.int_max
          }
          if (l.data_type === 'choice') {
            base.options = l.options
              .filter((o) => o.trim())
              .map((value) => ({ value }))
          }
          return base
        })
      }
      
      try {
        await this.$services.perspective.updatePerspective(
          this.projectId,
          this.perspectiveId,
          payload
        )
        this.showSuccessMessage('Perspective updated successfully!')
        // Delay navigation to show success message
        setTimeout(() => {
          this.$router.back()
        }, 1500)
      } catch (e) {
        console.error(e)
        let errorMessage = 'Failed to save changes. Please try again.'
        
        // Handle specific error cases
        if (e.response) {
          switch (e.response.status) {
            case 400:
              errorMessage = 'Invalid data provided. Please check your inputs.'
              break
            case 401:
              errorMessage = 'You are not authorized to perform this action.'
              break
            case 403:
              errorMessage = 'Access denied. You do not have permission to edit this perspective.'
              break
            case 404:
              errorMessage = 'Perspective not found. It may have been deleted.'
              break
            case 422:
              errorMessage = 'Validation failed. Please check your data and try again.'
              break
            case 500:
              errorMessage = 'Server error. Please try again later.'
              break
            case 502:
              errorMessage = 'Erro de base de dados. Tente novamente mais tarde.'
              break
            case 503:
              errorMessage = 'Erro de base de dados. Tente novamente mais tarde.'
              break
            case 504:
              errorMessage = 'Erro de base de dados. Tente novamente mais tarde.'
              break
            default:
              errorMessage = `Error ${e.response.status}: ${e.response.statusText || 'Unknown error'}`
          }
        } else if (e.code === 'NETWORK_ERROR') {
          errorMessage = 'Network error. Please check your connection and try again.'
        }
        
        this.showErrorMessage(errorMessage)
      } finally {
        this.loading = false
      }
    },
    showSuccessMessage(message) {
      this.snackbar = {
        show: true,
        message,
        color: 'success',
        icon: 'mdi-check-circle',
        timeout: 3000
      }
    },
    showErrorMessage(message) {
      this.snackbar = {
        show: true,
        message,
        color: 'error',
        icon: 'mdi-alert-circle',
        timeout: 6000
      }
    },
    showInfoMessage(message) {
      this.snackbar = {
        show: true,
        message,
        color: 'info',
        icon: 'mdi-information',
        timeout: 4000
      }
    }
  }
}
</script>

<style scoped>
.form-container { 
  max-width: 800px; 
  margin: 0 auto; 
  padding: 24px; 
}

.form-card { 
  border-radius: 12px; 
  overflow: hidden; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  padding: 20px 24px;
  font-size: 1.25rem;
  font-weight: 600;
}

.form-content { 
  padding: 32px 24px;
  background: #fafafa;
}

.modern-alert {
  border-radius: 8px;
  background: rgba(244, 67, 54, 0.1);
}

.input-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section-divider {
  margin: 24px 0;
}

.labels-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
}

.labels-list {
  margin-bottom: 20px;
}

.label-card {
  margin-bottom: 16px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.label-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.label-header {
  display: flex;
  align-items: center;
  padding: 16px 16px 0;
}

.label-number {
  width: 28px;
  height: 28px;
  background: #1976d2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  margin-right: 12px;
}

.label-title {
  font-weight: 600;
  color: #2c3e50;
}

.delete-btn {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.delete-btn:hover {
  opacity: 1;
}

.label-form {
  padding: 0 16px 16px;
}

.modern-input {
  background: white;
  border-radius: 6px;
}

.range-section {
  background: rgba(33, 150, 243, 0.05);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.range-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.range-label {
  font-weight: 500;
  color: #1976d2;
  font-size: 0.875rem;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-field {
  flex: 1;
}

.range-separator {
  color: #666;
  font-weight: 500;
  padding: 0 4px;
}

.options-section {
  background: rgba(76, 175, 80, 0.05);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.options-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.options-label {
  font-weight: 500;
  color: #388e3c;
  font-size: 0.875rem;
  flex: 1;
}

.options-list {
  margin-bottom: 12px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.option-row:last-child {
  margin-bottom: 0;
}

.option-input {
  flex: 1;
}

.option-delete-btn {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.option-delete-btn:hover {
  opacity: 1;
}

.add-option-btn {
  text-transform: none;
  font-weight: 500;
}

.add-label-btn {
  width: 100%;
  height: 48px;
  text-transform: none;
  font-weight: 600;
  border: 2px dashed #1976d2;
  transition: all 0.2s ease;
}

.add-label-btn:hover {
  background: rgba(25, 118, 210, 0.05);
}

.actions-container { 
  padding: 20px 24px; 
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

.action-btn {
  height: 44px;
  text-transform: none;
  font-weight: 600;
  border-radius: 6px;
  padding: 0 24px;
}

.save-btn {
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.save-btn:hover {
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
}

/* Responsive */
@media (max-width: 600px) {
  .form-container {
    padding: 16px;
  }
  
  .form-content {
    padding: 20px 16px;
  }
  
  .input-section,
  .labels-section {
    padding: 16px;
  }
  
  .range-inputs {
    flex-direction: column;
    gap: 8px;
  }
  
  .range-separator {
    transform: rotate(90deg);
  }
}
</style>