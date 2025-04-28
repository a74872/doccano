<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="600">
    <v-card height="550" class="d-flex flex-column">
      <v-card-title class="headline">
        Discussion
        <v-spacer/>
        <v-btn icon @click="$emit('input', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- mensagem list -->
      <v-card-text class="flex-grow-1 pb-0 overflow-y-auto">
        <v-list dense>
          <template v-if="loading">
            <v-skeleton-loader type="list-item"/>
          </template>
          <v-list-item
            v-else
            v-for="msg in messages"
            :key="msg.id"
            two-line
          >
            <v-list-item-content>
              <v-list-item-title class="font-weight-medium">
                {{ msg.user }}
                <span class="grey--text text--caption">
                  {{ human(msg.created_at) }}
                </span>
              </v-list-item-title>
              <v-list-item-subtitle
                style="white-space: pre-wrap"
              >{{ msg.text }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>

      <!-- caixa de escrita -->
      <v-divider/>
      <v-card-actions>
        <v-text-field
          v-model="draft"
          class="flex-grow-1"
          dense
          outlined
          hide-details
          placeholder="Write a message …"
          @keyup.enter="send"
        />
        <v-btn
          color="primary"
          text
          class="text-capitalize"
          :disabled="!draft.trim()"
          @click="send"
        >
          Send
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

export default Vue.extend({
  props: {
    value:      { type: Boolean, required: true },      // v-model
    projectId:  { type: String,  required: true },
    example:    { type: Object,  required: true }       // ExampleDTO
  },
  data () {
    return {
      messages: [] as any[],
      loading : false,
      draft   : ''
    }
  },
  watch: {
    value (val: boolean) { if (val) this.fetch() }
  },
  methods: {
    human (ts: string) { return dayjs(ts).fromNow() },

    async fetch () {
      this.loading = true
      try {
        const url =
          `/projects/${this.projectId}/discussion?example=${this.example.id}`
        this.messages = (await this.$axios.$get(url)).reverse()
      } finally { this.loading = false }
    },

    async send () {
      const text = this.draft.trim()
      if (!text) return
      const url = `/projects/${this.projectId}/discussion`
      await this.$axios.$post(url, { example: this.example.id, text })
      this.draft = ''
      await this.fetch()
    }
  }
})
</script>
