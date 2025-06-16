<template>
  <v-container class="form-container">
    <v-card class="form-card">
      <!-- pop-up de sucesso -->
      <v-dialog v-model="showSuccess" max-width="570">
        <v-card>
          <v-card-title class="headline">
            {{ $t('Your perspective has been created successfully') }}
          </v-card-title>

          <v-card-actions>
            <v-spacer/>
            <v-btn color="primary" text @click="onSuccessClose">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>


      <!-- header -->
      <v-card-title class="headline primary white--text d-flex align-center ">
        <v-icon left color="white">mdi-pencil</v-icon>
        Create New Perspective
      </v-card-title>

      <!-- body -->
      <v-card-text class="form-content pt-6">
        <!-- global error -->
        <v-alert
          v-if="showError"
          type="error"
          dismissible
          border="left"
          elevation="2"
          class="custom-alert error-alert"
          colored-border
          @input="showError = false"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-3">mdi-alert-circle</v-icon>
            <span>{{ errorText  }}</span>
          </div>
        </v-alert>

        <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="submitForm">
          <!-- perspective title -->
          <div class="input-group">
            <v-text-field
              v-model.trim="title"
              label="Perspective Title"
              :rules="[rules.required]"
              :error-messages="fieldErrors.title"
              outlined dense prepend-inner-icon="mdi-format-title"
              hint="Enter a descriptive title for your perspective"
              persistent-hint
            />
          </div>

          <!-- description -->
          <div class="input-group">
            <v-textarea
              v-model.trim="description"
              label="Description"
              :rules="[rules.required]"
              :error-messages="fieldErrors.description"
              outlined
              auto-grow
              hint="Briefly describe what this perspective is about"
              persistent-hint
            />
          </div>

          <!-- labels builder -->
          <div class="labels-container">
            <v-card
              v-for="(label, index) in labels"
              :key="index"
              class="mb-4 pa-4"
              outlined
            >
              <div class="d-flex justify-space-between align-center mb-3">
                <span class="subtitle-2 font-weight-bold">Label {{ index + 1 }}</span>
                <v-btn icon small @click="removeLabel(index)" v-if="labels.length > 1">
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </div>

              <!-- name -->
              <v-text-field
                v-model.trim="label.name"
                label="Label name"
                :error-messages="getLabelError(index, 'name')"
                :rules="[rules.required]"
                outlined dense prepend-inner-icon="mdi-label"
              />

              <!-- type selector -->
              <v-select
                v-model="label.data_type"
                :items="dataTypes"
                label="Data type"
                item-text="text"
                item-value="value"
                :error-messages="getLabelError(index, 'data_type')"
                :rules="[rules.required]"
                outlined dense prepend-inner-icon="mdi-database"
                @change="onTypeChange(index)"
              />

              <!-- int rules -->
              <div v-if="label.data_type === 'int'" class="d-flex flex-wrap">
                <v-text-field
                  v-model.number="label.int_min"
                  type="number"
                  label="Min"
                  class="mr-2 flex-grow-1"
                  :error-messages="getLabelError(index, 'int_min')"
                  :rules="[rules.required, rules.isNumber]"
                  outlined dense
                />
                <v-text-field
                  v-model.number="label.int_max"
                  type="number"
                  label="Max"
                  class="flex-grow-1"
                  :error-messages="getLabelError(index, 'int_max')"
                  :rules="[rules.required, rules.isNumber]"
                  outlined dense
                />
              </div>

              <!-- choice options -->
              <div v-if="label.data_type === 'choice'">
                <div
                  v-for="(opt, optIdx) in label.options"
                  :key="optIdx"
                  class="d-flex align-center mb-2"
                >
                  <v-text-field
                    v-model.trim="label.options[optIdx]"
                    :label="`Option ${optIdx + 1}`"
                    :error-messages="getOptionError(index, optIdx)"
                    :rules="[rules.required]"
                    outlined dense class="flex-grow-1"
                  />
                  <v-btn icon small class="ml-2" @click="removeOption(index, optIdx)" v-if="label.options.length > 1">
                    <v-icon small>mdi-close</v-icon>
                  </v-btn>
                </div>
                <v-btn small text color="primary" @click="addOption(index)" :disabled="label.options.length >= 4">
                  <v-icon left small>mdi-plus</v-icon>
                  Add option
                </v-btn>
              </div>
            </v-card>

            <!-- add label button -->
            <v-btn color="primary" outlined @click="addLabel" :disabled="labels.length >= 7">
              <v-icon left>mdi-plus</v-icon>
              Add label
            </v-btn>
          </div>
        </v-form>
      </v-card-text>

      <!-- footer actions -->
      <v-card-actions class="actions-container">
        <v-btn outlined color="secondary" @click="$router.back()">
          <v-icon left>mdi-arrow-left</v-icon>
          Back
        </v-btn>
        <v-spacer />
        <v-btn color="primary" :loading="loading" @click="submitForm">
          <v-icon left>mdi-check</v-icon>
          Create Perspective
        </v-btn>
      </v-card-actions>

      <!-- loading bar -->
      <v-progress-linear v-if="loading" indeterminate color="primary" class="mt-2" />
    </v-card>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      title: '',
      labels: [this.newLabel()],
      loading: false,
      description: '',
      valid: true,
      showError: false,
      errorMsgKey: 'errors.serverUnavailable',
      showSuccess: false,
      fieldErrors: {},
      dataTypes: [
        { text: 'Text', value: 'string' },
        { text: 'Number', value: 'int' },
        { text: 'Options', value: 'choice' }
      ],
      rules: {
        required: v => !!v || 'This field is required',
        isNumber: v => (v === null || v === undefined || v === '') || !isNaN(v) || 'Must be a number'
      }
    }
  },

  computed: {
    errorText() {
      return this.$t(this.errorMsgKey)
    }
  },

  methods: {
    // factory
    newLabel() {
      return { name: '', data_type: 'string', int_min: null, int_max: null, options: [''] }
    },

    onSuccessClose() {
      this.showSuccess = false
      this.$router.push(`/projects/${this.$route.params.id}/perspective`)
    },

    // add / remove labels
    addLabel() {
      if (this.labels.length < 7) this.labels.push(this.newLabel())
    },
    removeLabel(idx) {
      this.labels.splice(idx, 1)
    },

    // type change resets auxiliary fields
    onTypeChange(idx) {
      const lbl = this.labels[idx]
      if (lbl.data_type === 'int') {
        lbl.options = ['']
      } else if (lbl.data_type === 'choice') {
        lbl.int_min = null
        lbl.int_max = null
        if (!lbl.options.length) lbl.options = ['']
      } else {
        lbl.int_min = null
        lbl.int_max = null
        lbl.options = ['']
      }
    },

    // options helpers
    addOption(labelIdx) {
      const opts = this.labels[labelIdx].options
      if (opts.length < 4) opts.push('')
    },
    removeOption(labelIdx, optIdx) {
      const opts = this.labels[labelIdx].options
      opts.splice(optIdx, 1)
    },

    // validation helpers
    getLabelError(labelIdx, field) {
      const key = `label_${labelIdx}_${field}`
      return this.fieldErrors[key] || ''
    },
    getOptionError(labelIdx, optIdx) {
      const key = `label_${labelIdx}_option_${optIdx}`
      return this.fieldErrors[key] || ''
    },

    validateForm() {
      this.fieldErrors = {}
      let ok = true

      // title
      if (!this.title.trim()) {
        this.fieldErrors.title = 'Title is required'
        ok = false
      }

      // labels validations
      this.labels.forEach((lbl, idx) => {
        if (!lbl.name.trim()) {
          this.fieldErrors[`label_${idx}_name`] = 'Name is required'
          ok = false
        }
        if (!lbl.data_type) {
          this.fieldErrors[`label_${idx}_data_type`] = 'Type is required'
          ok = false
        }
        if (lbl.data_type === 'int') {
          if (lbl.int_min === null || lbl.int_min === '') {
            this.fieldErrors[`label_${idx}_int_min`] = 'Min is required'
            ok = false
          }
          if (lbl.int_max === null || lbl.int_max === '') {
            this.fieldErrors[`label_${idx}_int_max`] = 'Max is required'
            ok = false
          }
          if (lbl.int_min !== null && lbl.int_max !== null && Number(lbl.int_min) >= Number(lbl.int_max)) {
            this.fieldErrors[`label_${idx}_int_max`] = 'Max must be higher than Min'
            ok = false
          }
        }
        if (lbl.data_type === 'choice') {
          const filledOpts = lbl.options.filter(o => o.trim())
          if (filledOpts.length < 2) {
            this.fieldErrors[`label_${idx}_option_0`] = 'At least 2 options'
            ok = false
          }
          lbl.options.forEach((o, oIdx) => {
            if (!o.trim()) {
              this.fieldErrors[`label_${idx}_option_${oIdx}`] = 'Required'
              ok = false
            }
          })
        }
      })

      return ok
    },

    async submitForm() {
      if (!this.validateForm()) {
        this.error = 'Please, fill the form correctly'
        this.errorMsgKey = 'errors.formInvalid'
        this.showError   = true
        return
      }


      const payload = {
        title: this.title.trim(),
        description: this.description.trim(),
        labels: this.labels.map(l => {
          const base = { name: l.name.trim(), data_type: l.data_type }
          if (l.data_type === 'int') {
            base.int_min = l.int_min
            base.int_max = l.int_max
          }
          if (l.data_type === 'choice') {
            base.options = l.options.filter(o => o.trim()).map(value => ({ value }))
          }
          return base
        })

      }
      console.log('payload que vai para o POST:', JSON.stringify(payload, null, 2))

      try {
        this.loading = true
        await this.$repositories.perspective.createPerspective(this.$route.params.id, payload)
        this.showSuccess = true
      } catch (e) {
        const { status, data } = e.response || {}
        // duplicado → mostra erro no campo Title
        if (status === 400 && data?.title?.length) {
          this.fieldErrors.title = data.title[0]
          // não mostramos o alerta global
          this.showError = false
          return
        }

        // qualquer outra falha
        console.error("DRF response:", data || e)
        this.errorMsgKey = "errors.serverUnavailable"
        this.showError   = true
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* manteve a maior parte dos estilos anteriores */
.form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  height: calc(100vh - 48px);
  animation: slideIn 0.5s ease;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.form-card {
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #ffffff;
}
.form-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-height: calc(100vh - 200px);
  background-color: #fafafa;
}
.input-group { margin-bottom: 24px; }
.labels-container { margin-top: 16px; }
.actions-container { padding: 16px 24px; background-color: #f5f5f5; }
.custom-alert { margin-bottom: 24px !important; }
</style>
