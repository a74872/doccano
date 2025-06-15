<template>
  <div>
    <v-dialog :value="value" max-width="600" scrollable persistent
              @input="$emit('input', $event)">
      <v-card class="vote-dialog" elevation="12">
        <!-- Header com gradiente sutil -->
        <v-card-title class="vote-dialog-header pa-6">
          <div class="header-content">
            <v-icon class="mr-3" color="primary" size="28">mdi-vote</v-icon>
            <div>
              <h2 class="headline mb-1">Vote on a rule</h2>
              <p class="subtitle-2 mb-0 text--secondary">Select a rule to cast your vote</p>
            </div>
          </div>
          <v-btn icon large @click="$emit('input', false)" class="close-btn">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider class="mx-6"/>

        <!-- Loading state melhorado -->
        <v-card-text v-if="loading" class="loading-container">
          <div class="text-center py-8">
            <v-progress-circular
              indeterminate
              color="primary"
              size="48"
              class="mb-4"
            />
            <p class="subtitle-1 text--secondary">Loading rules...</p>
          </div>
        </v-card-text>

        <!-- Rules section -->
        <v-card-text v-else class="rules-container pa-6">
          <div v-if="rules.length === 0" class="empty-state text-center py-8">
            <v-icon size="64" color="grey lighten-1" class="mb-4">mdi-clipboard-text-outline</v-icon>
            <h3 class="subtitle-1 text--secondary">No rules available</h3>
            <p class="body-2 text--disabled">There are no rules to vote on at this time.</p>
          </div>

          <div v-else>
            <h3 class="subtitle-1 mb-4 text--primary">Available Rules</h3>
            <v-radio-group v-model="selectedRuleId" class="custom-radio-group">
              <v-card
                v-for="r in rules"
                :key="r.id"
                class="rule-card mb-3"
                :class="{ 'rule-card--selected': selectedRuleId === r.id }"
                @click="selectedRuleId = r.id"
              >
                <v-card-text class="py-3 px-4">
                  <div class="d-flex align-center">
                    <v-radio
                      :value="r.id"
                      class="mr-3"
                      color="primary"
                      @click.stop
                    />
                    <div class="flex-grow-1">
                      <h4 class="body-1 font-weight-medium mb-1">{{ r.title }}</h4>
                      <p v-if="r.description" class="body-2 text--secondary mb-0">
                        {{ r.description }}
                      </p>
                    </div>
                    <v-chip
                      v-if="isMyCurrentVote(r.id)"
                      small
                      color="success"
                      text-color="white"
                      class="ml-2"
                    >
                      <v-icon small left>mdi-check</v-icon>
                      Your vote
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-radio-group>
          </div>
        </v-card-text>

        <v-divider class="mx-6"/>

        <!-- Actions com melhor spacing -->
        <v-card-actions class="pa-6">
          <v-spacer/>
          <v-btn
            text
            large
            @click="$emit('input', false)"
            class="mr-3"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            large
            depressed
            :disabled="!selectedRuleId"
            :loading="submitting"
            @click="submit"
          >
            <v-icon left>mdi-check</v-icon>
            Submit Vote
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbars -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="4000"
      bottom
    >
      {{ snackbar.message }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    value:      { type: Boolean, required: true },
    projectId:  { type: String,  required: true },
    exampleId:  { type: Number,  required: true },
    discussion: { type: Object,  required: true }
  },

  data () {
    return {
      rules: [] as any[],
      loading: false,
      submitting: false,
      selectedRuleId: '',
      myVoteId: '',
      snackbar: {
        show: false,
        message: '',
        color: 'success'
      }
    }
  },

  watch: {
    value (v)     { v && this.fetch() },
    discussion () { this.value && this.fetch() }
  },

  methods: {
    showSnackbar(message: string, color: string = 'success') {
      this.snackbar.message = message
      this.snackbar.color = color
      this.snackbar.show = true
    },

    /* ───────────── lista regras ───────────── */
    async fetch () {
      this.loading = true
      const url =
        `/v1/projects/${this.projectId}` +
        `/discussion/examples/${this.exampleId}` +
        `/${this.discussion.id}/rules/`

      try {
        console.log('[GET]', url)
        const { data } = await this.$axios.get(url)
        this.rules = Array.isArray(data) ? data : data.results
        const username = this.$auth?.user?.username || null
        const mine = this.rules
          .flatMap((r:any) => r.votes || [])
          .find((v:any) => v.username === username)

        this.selectedRuleId = mine ? mine.rule : ''
        this.myVoteId       = mine ? mine.id   : ''
      } catch (err:any) {
        console.error('fetch rules error:', err.response?.data || err)
      } finally {
        this.loading = false
      }
    },

    async submit () {
      this.submitting = true
      // rota: …/rules/<rule_id>/votes/
      const url =
        `/v1/projects/${this.projectId}` +
        `/discussion/examples/${this.exampleId}` +
        `/${this.discussion.id}/rules/${this.selectedRuleId}/votes/`

      const body = { vote: true }      // não envie "rule" nem "user"

      try {
        if (this.myVoteId) {
          console.log('[PATCH]', `${url}${this.myVoteId}/`, body)
          await this.$axios.patch(`${url}${this.myVoteId}/`, body)
          this.showSnackbar('Vote updated successfully!', 'success')
        } else {
          console.log('[POST]', url, body)
          await this.$axios.post(url, body)
          this.showSnackbar('Vote submitted successfully!', 'success')
        }

        this.$emit('input', false)   // fecha pop-up
        this.$emit('voted')          // refresca a tabela
      } catch (error:any) {
        // mostra exactamente o que o DRF devolveu
        console.error('vote error:', error.response?.data || error)
        this.showSnackbar('Error submitting vote. Please try again.', 'error')
      } finally {
        this.submitting = false
      }
    },

    isMyCurrentVote(ruleId: string) {
      return this.myVoteId && this.selectedRuleId === ruleId
    }
  }
})
</script>

<style scoped>
.vote-dialog {
  border-radius: 12px !important;
}

.vote-dialog-header {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px 12px 0 0 !important;
}

.header-content {
  display: flex;
  align-items: center;
  flex-grow: 1;
}

.close-btn {
  transition: transform 0.2s ease;
}

.close-btn:hover {
  transform: rotate(90deg);
}

.loading-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rules-container {
  min-height: 250px;
}

.empty-state {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.custom-radio-group {
  margin-top: 0;
}

.rule-card {
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
  border-radius: 8px !important;
}

.rule-card:hover {
  border-color: #e0e0e0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
  transform: translateY(-1px);
}

.rule-card--selected {
  border-color: var(--v-primary-base) !important;
  background-color: rgba(var(--v-primary-base), 0.05);
}

.rule-card--selected:hover {
  border-color: var(--v-primary-darken1) !important;
}

/* Remove default radio group spacing */
.custom-radio-group >>> .v-input--radio-group__input {
  margin: 0;
}

.custom-radio-group >>> .v-radio {
  margin: 0;
}

/* Smooth transitions */
.v-btn {
  transition: all 0.2s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
}

.v-btn[disabled] {
  transform: none;
}
</style>