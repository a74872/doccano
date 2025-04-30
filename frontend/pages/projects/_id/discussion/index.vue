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
      <v-btn
        :disabled="!selected.length"
        outlined
        class="me-2"
        @click="dialogDelete = true"
      >
        {{ $t('generic.delete') }}
      </v-btn>
      <v-btn
        :disabled="!selected.length"
        outlined
        color="grey darken-1"
        @click="dialogArchive = true"
      >
        Archive
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

    <discussion-delete
      :show.sync="dialogDelete"
      :qty="selected.length"
      title="Delete"
      color="error"
      @cancel="dialogDelete = false"
      @confirm="removeSelected"
    />

    <discussion-archive
      :show.sync="dialogArchive"
      :qty="selected.length"
      title="Archive"
      color="grey darken-1"
      @cancel="dialogArchive = false"
      @confirm="archiveSelected"
    />


  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import DiscussionList    from '~/components/discussion/DiscussionList.vue'
import DiscussionCreate  from '~/components/discussion/DiscussionCreate.vue'
import DiscussionDelete  from '~/components/discussion/DiscussionDelete.vue'
import DiscussionArchive from '~/components/discussion/DiscussionArchive.vue'

export default Vue.extend({
  components: { DiscussionList, DiscussionCreate, DiscussionDelete, DiscussionArchive },
  layout: 'project',
  middleware: ['check-auth','auth','setCurrentProject','isProjectAdmin'],

  data() {
    return {
      isLoading:    false,
      examples:     [] as Array<{ id:number; text:string }>,
      discussions:  [] as any[],
      selected:     [] as any[],
      dialogCreate:  false,
      dialogDelete:  false,
      dialogArchive: false,
      edited:        { id: null, title: '', description: '' } as any
    }
  },

  async fetch() {
    this.isLoading = true
    try {
      const list = await this.$services.example.list(this.projectId, {})
      this.examples = list.items.map(e => ({
        id:   e.id,
        text: e.upload_name || e.filename || String(e.id)
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
      this.fetch()
    }
  },

  methods: {
    openCreate() {
      this.edited = { id: null, title: '', description: '' }
      this.dialogCreate = true
    },

    async saveDiscussion(payload: { id: string|null; title: string; description: string }) {
      try {
        await this.$repositories.discussion.create(
          this.projectId,
          this.exampleId,
          { title: payload.title, description: payload.description }
        )
        await this.fetch()
        this.dialogCreate = false
      } catch (e) {
        console.error('[Discussion] saveDiscussion error:', e)
      }
    },

    async removeSelected() {
      await this.$repositories.discussion.bulkDelete(
        this.projectId,
        this.selected.map(d => d.id)
      )
      this.selected = []
      await this.fetch()
    },

    async archiveSelected() {
      await this.$repositories.discussion.archive(
        this.projectId,
        this.selected.map(d => d.id)
      )
      this.selected = []
      await this.fetch()
    }
  }
})
</script>

<style scoped>
.me-4 { margin-right: 1rem }
.me-2 { margin-right: 0.5rem }
</style>
