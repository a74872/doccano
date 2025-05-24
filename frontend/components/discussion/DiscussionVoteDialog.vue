<template>
  <v-dialog :value="value" max-width="500" scrollable
            @input="$emit('input', $event)">
    <v-card>
      <v-card-title class="headline">
        Vote on a rule
        <v-spacer/>
        <v-btn icon @click="$emit('input', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider/>

      <!-- carregamento -->
      <v-card-text v-if="loading" class="text-center py-6">
        <v-skeleton-loader type="paragraph"/>
      </v-card-text>

      <!-- regras -->
      <v-card-text v-else>
        <v-radio-group v-model="selectedRuleId" column>
          <v-radio v-for="r in rules"
                   :key="r.id"
                   :label="r.title"
                   :value="r.id"/>
        </v-radio-group>
      </v-card-text>

      <v-divider/>

      <!-- acções -->
      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="$emit('input', false)">Cancel</v-btn>
        <v-btn color="primary" text
               :disabled="!selectedRuleId"
               @click="submit">
          Submit
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
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
      selectedRuleId: '',
      myVoteId: ''
    }
  },

  watch: {
    value (v)     { v && this.fetch() },
    discussion () { this.value && this.fetch() }
  },

  methods: {
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
      // rota: …/rules/<rule_id>/votes/
      const url =
        `/v1/projects/${this.projectId}` +
        `/discussion/examples/${this.exampleId}` +
        `/${this.discussion.id}/rules/${this.selectedRuleId}/votes/`

      const body = { vote: true }      // não envie “rule” nem “user”

      try {
        if (this.myVoteId) {
          console.log('[PATCH]', `${url}${this.myVoteId}/`, body)
          await this.$axios.patch(`${url}${this.myVoteId}/`, body)
        } else {
          console.log('[POST]', url, body)
          await this.$axios.post(url, body)
        }

        this.$emit('input', false)   // fecha pop-up
        this.$emit('voted')          // refresca a tabela
      } catch (error:any) {
        // mostra exactamente o que o DRF devolveu
        console.error('vote error:', error.response?.data || error)
      }
    }


  }
})
</script>
