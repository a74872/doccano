<template>
  <v-container class="form-container">
    <v-card class="form-card">
      <!-- header -->
      <v-card-title class="headline primary white--text d-flex align-center">
        <v-icon left color="white">mdi-pencil</v-icon>
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
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="submitForm">
          <!-- title -->
          <v-text-field
            v-model.trim="form.title"
            label="Perspective Title"
            :rules="[rules.required]"
            outlined
            dense
            prepend-inner-icon="mdi-format-title"
          />

          <v-divider class="my-4" />

          <!-- labels list -->
          <div>
            <v-card
              v-for="(lbl, idx) in form.labels"
              :key="idx"
              class="mb-4 pa-4"
              outlined
            >
              <div class="d-flex justify-space-between align-center mb-3">
                <span class="subtitle-2 font-weight-bold">Label {{ idx + 1 }}</span>
                <v-btn
                  icon
                  small
                  v-if="form.labels.length > 1"
                  @click="removeLabel(idx)"
                >
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </div>

              <v-text-field
                v-model.trim="lbl.name"
                label="Label name"
                :rules="[rules.required]"
                outlined
                dense
              />

              <v-select
                v-model="lbl.data_type"
                :items="dataTypes"
                label="Data type"
                item-text="text"
                item-value="value"
                outlined
                dense
                @change="onTypeChange(idx)"
              />

              <!-- integer rules -->
              <div v-if="lbl.data_type==='int'" class="d-flex">
                <v-text-field
                  v-model.number="lbl.int_min"
                  label="Min"
                  type="number"
                  class="mr-2"
                  outlined
                  dense
                />
                <v-text-field
                  v-model.number="lbl.int_max"
                  label="Max"
                  type="number"
                  outlined
                  dense
                />
              </div>

              <!-- choice options -->
              <div v-if="lbl.data_type==='choice'">
                <div
                  v-for="(opt,optIdx) in lbl.options"
                  :key="optIdx"
                  class="d-flex align-center mb-2"
                >
                  <v-text-field
                    v-model.trim="lbl.options[optIdx]"
                    :label="`Option ${optIdx+1}`"
                    outlined
                    dense
                  />
                  <v-btn
                    icon
                    small
                    class="ml-2"
                    v-if="lbl.options.length>1"
                    @click="removeOption(idx,optIdx)"
                  >
                    <v-icon small>mdi-close</v-icon>
                  </v-btn>
                </div>
                <v-btn
                  small
                  text
                  color="primary"
                  :disabled="lbl.options.length>=4"
                  @click="addOption(idx)"
                >
                  <v-icon left small>mdi-plus</v-icon>
                  Add option
                </v-btn>
              </div>
            </v-card>
            <v-btn
              color="primary"
              outlined
              :disabled="form.labels.length>=7"
              @click="addLabel"
            >
              <v-icon left>mdi-plus</v-icon>
              Add label
            </v-btn>
          </div>
        </v-form>
      </v-card-text>

      <!-- footer -->
      <v-card-actions class="actions-container">
        <v-btn
          outlined
          color="secondary"
          @click="$router.back()"
        >
          <v-icon left>mdi-arrow-left</v-icon>
          Back
        </v-btn>
        <v-spacer />
        <v-btn color="success" :loading="loading" @click="submitForm">
          <v-icon left>mdi-content-save</v-icon>
          Save Changes
        </v-btn>
      </v-card-actions>
      <v-progress-linear v-if="loading" indeterminate color="primary" />
    </v-card>
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
        this.error = 'Failed to load perspective'
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
      if (this.form.labels.length < 7) this.form.labels.push(this.newLabel())
    },
    removeLabel(i) {
      this.form.labels.splice(i, 1)
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
      if (o.length < 4) o.push('')
    },
    removeOption(i, oi) {
      this.form.labels[i].options.splice(oi, 1)
    },
    async submitForm() {
      if (!this.$refs.form.validate()) return
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
        this.$router.back()
      } catch (e) {
        console.error(e)
        this.error = 'Save failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.form-container { max-width: 800px; margin: 0 auto; padding: 24px; }
.form-card { border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }
.form-content { max-height: 70vh; overflow-y: auto; }
.actions-container { padding: 16px 24px; background: #f5f5f5; }
</style>
