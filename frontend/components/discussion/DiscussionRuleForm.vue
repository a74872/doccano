<template>
  <v-dialog
    :value="show"
    max-width="600"
    scrollable
    persistent
    @input="$emit('update:show', $event)"
  >
    <v-card class="elevation-8">
      <v-card-title class="primary white--text pa-6">
        <v-icon left color="white" class="mr-3">mdi-rule</v-icon>
        <span class="text-h5 font-weight-light">Create New Rules</span>
        <v-spacer/>
        <v-btn
          icon
          color="white"
          @click="$emit('update:show', false)"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- Content -->
      <v-card-text class="pa-6">
        <div class="mb-4">
          <p class="text-body-1 grey--text text--darken-1 mb-3">
            Define the rules that will be used for voting on this discussion. Each rule should be clear and concise.
          </p>
        </div>

        <!-- Rules list -->
        <v-slide-y-transition group appear>
          <v-card
            v-for="(rule, idx) in rules"
            :key="idx"
            outlined
            class="mb-3 rule-card"
            :class="{ 'error-border': hasError(idx) }"
          >
            <v-card-text class="pa-4">
              <div class="d-flex align-center">
                <div class="rule-number mr-3">
                  <v-avatar size="28" color="primary" class="white--text">
                    <span class="caption font-weight-bold">{{ idx + 1 }}</span>
                  </v-avatar>
                </div>
                
                <v-text-field
                  v-model="rules[idx]"
                  outlined
                  dense
                  hide-details="auto"
                  :counter="60"
                  label="Rule title"
                  placeholder="Enter a clear and concise rule..."
                  class="flex-grow-1"
                  :rules="getRuleValidation(idx)"
                  :error="hasError(idx)"
                  clearable
                />
                
                <v-btn
                  v-if="rules.length > 1"
                  icon
                  color="error"
                  class="ml-3"
                  @click="remove(idx)"
                >
                  <v-icon>mdi-delete-outline</v-icon>
                </v-btn>
              </div>

              <!-- Error message -->
              <v-expand-transition>
                <div v-if="hasError(idx)" class="mt-2">
                  <v-alert
                    dense
                    text
                    type="error"
                    class="mb-0"
                  >
                    {{ getErrorMessage(idx) }}
                  </v-alert>
                </div>
              </v-expand-transition>
            </v-card-text>
          </v-card>
        </v-slide-y-transition>

        <!-- Add rule button -->
        <div class="text-center mt-4">
          <v-btn
            outlined
            color="primary"
            class="px-6"
            :disabled="rules.length >= 5"
            @click="addField"
          >
            <v-icon left>mdi-plus</v-icon>
            Add Another Rule
          </v-btn>
        </div>

        <!-- Info section -->
        <v-card
          flat
          color="blue-grey lighten-5"
          class="mt-4 pa-4"
        >
          <div class="d-flex align-center">
            <v-icon color="blue-grey" class="mr-2">mdi-information-outline</v-icon>
            <div>
              <p class="mb-1 caption font-weight-medium blue-grey--text text--darken-2">
                Guidelines:
              </p>
              <ul class="caption blue-grey--text text--darken-1 mb-0 ml-4">
                <li>You can create up to 5 rules maximum</li>
                <li>Each rule must be unique and non-empty</li>
                <li>Rules should be clear and actionable</li>
              </ul>
            </div>
          </div>
        </v-card>
      </v-card-text>

      <!-- Actions -->
      <v-divider/>
      <v-card-actions class="pa-6">
        <v-spacer/>
        <v-btn
          text
          color="grey darken-1"
          class="px-6"
          @click="cancel"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          depressed
          class="px-8"
          :disabled="!canSave"
          @click="save"
        >
          <v-icon left small>mdi-content-save</v-icon>
          Save Rules
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'DiscussionRuleForm',
  props: {
    show:       { type: Boolean, default: false },
    ruleTitle:  { type: String,  default: '' }
  },
  data () {
    return {
      rules: this.ruleTitle ? [this.ruleTitle] : ['']
    }
  },
  computed: {
    canSave (): boolean {
      return (
        this.rules.length > 0 &&
        this.rules.every(r => r.trim().length > 0) &&
        !this.hasDuplicates() &&
        this.rules.every(r => r.trim().length <= 60)
      )
    }
  },
  watch: {
    show (v: boolean) {
      if (v && this.rules.length === 0) {
        this.rules = ['']
      }
    }
  },
  methods: {
    addField () {
      if (this.rules.length < 5) {
        this.rules.push('')
      }
    },
    
    remove (idx: number) {
      this.rules.splice(idx, 1)
    },

    cancel () {
      this.rules = ['']
      this.$emit('update:show', false)
    },
    
    save () {
      const titles = this.rules.map(r => r.trim()).filter(Boolean)
      this.$emit('save', titles)
      this.$emit('update:show', false)
      this.rules = ['']
    },

    hasDuplicates (): boolean {
      const trimmedRules = this.rules.map(r => r.trim().toLowerCase()).filter(Boolean)
      return trimmedRules.length !== new Set(trimmedRules).size
    },

    hasError (idx: number): boolean {
      const rule = this.rules[idx].trim()
      
      // Empty rule
      if (!rule) return false // Don't show error for empty until user tries to save
      
      // Rule too long
      if (rule.length > 60) return true
      
      // Duplicate rule
      const duplicateCount = this.rules
        .map(r => r.trim().toLowerCase())
        .filter(r => r === rule.toLowerCase() && r !== '')
        .length
      
      return duplicateCount > 1
    },

    getErrorMessage (idx: number): string {
      const rule = this.rules[idx].trim()
      
      if (rule.length > 60) {
        return 'Rule title must be 60 characters or less'
      }
      
      const duplicateCount = this.rules
        .map(r => r.trim().toLowerCase())
        .filter(r => r === rule.toLowerCase() && r !== '')
        .length
      
      if (duplicateCount > 1) {
        return 'This rule already exists. Please use a different title.'
      }
      
      return ''
    },

    getRuleValidation (_idx: number) {
      return [
        (v: string) => !!v.trim() || 'Rule title is required',
        (v: string) => v.trim().length <= 60 || 'Rule title must be 60 characters or less',
        (v: string) => {
          if (!v.trim()) return true
          const duplicateCount = this.rules
            .map(r => r.trim().toLowerCase())
            .filter(r => r === v.trim().toLowerCase() && r !== '')
            .length
          return duplicateCount <= 1 || 'This rule already exists'
        }
      ]
    }
  }
})
</script>

<style scoped>
.rule-card {
  transition: all 0.3s ease;
}

.rule-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important;
}

.error-border {
  border-color: #f44336 !important;
  border-width: 2px !important;
}

.rule-number {
  min-width: 28px;
}
</style>