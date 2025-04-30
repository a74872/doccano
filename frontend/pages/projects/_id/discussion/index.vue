<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-select
        v-model="exampleId"
        :items="examples"
        item-text="text"
        item-value="id"
        label="Choose dataset"
        outlined dense
        class="me-4"
      />
      <v-btn
        :disabled="!exampleId"
        color="primary"
        class="text-capitalize me-2"
        @click="openCreate"
      >
        {{ $t('generic.add') }}
      </v-btn>
      <v-spacer/>
      <v-progress-circular v-if="isLoading" indeterminate size="20"/>
    </v-card-title>

    <discussion-list
      v-model="selected"
      :items="discussions"
      :loading="isLoading"
    />

    <discussion-create
      :show.sync="dialogCreate"
      :edited="edited"
      @cancel="dialogCreate = false"
      @save="saveDiscussion"
    />
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import DiscussionList   from '~/components/discussion/DiscussionList.vue'
import DiscussionCreate from '~/components/discussion/DiscussionCreate.vue'

export default Vue.extend({
  components: { DiscussionList, DiscussionCreate },
  layout: 'project',
  middleware: ['check-auth','auth','setCurrentProject','isProjectAdmin'],

  data() {
    return {
      isLoading:    false,
      examples:     [] as Array<{ id:number; text:string }>,
      discussions:  [] as any[],
      selected:     [] as any[],
      dialogCreate: false,
      edited:       { id: null, title: '', description: '' } as any
    }
  },

  // Nuxt hook
  async fetch() {
    this.isLoading = true
    try {
      const { items } = await this.$services.example.list(this.projectId, {})
      this.examples = items.map(e => ({
        id: e.id,
        text: e.upload_name || e.filename || `${e.id}`
      }))

      if (this.exampleId) {
        this.discussions = await this.$repositories.discussion.list(this.projectId, this.exampleId)
      } else {
        this.discussions = []
      }
    } finally {
      this.isLoading = false
    }
  },

  computed: {
    projectId(): string { return this.$route.params.id },
    exampleId: {
      get(): number { return Number(this.$route.query.example) || 0 },
      set(v: number) { this.$router.push({ query: { example: v } }) }
    }
  },

  watch: {
    '$route.query.example'() {
      this.$fetch()
    }
  },

  methods: {
    openCreate() {
      this.edited = { id: null, title: '', description: '' }
      this.dialogCreate = true
    },

    async saveDiscussion(payload: { id: string|null; title: string }) {
      try {
        await this.$repositories.discussion.create(
          this.projectId,
          this.exampleId,
          { title: payload.title }   // <— retirado description
        )
        await this.fetch()
        this.dialogCreate = false
      } catch (e) {
        // Para ver o erro retornado:
        console.error('[Discussion] saveDiscussion error:', e.response?.data || e)
      }
    }
  }
})
</script>

<style scoped>
.me-4 { margin-right: 1rem }
.me-2 { margin-right: 0.5rem }
</style>
