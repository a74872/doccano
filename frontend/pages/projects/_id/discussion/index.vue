<template>
  <v-card>
    <!-- Toolbar -->
    <v-card-title class="d-flex align-center">
      <v-select
        v-model="exampleId"
        :items="examples"
        item-text="text"
        item-value="id"
        label="Choose dataset"
        outlined
        dense
        class="me-4"
      />

      <v-btn
        :disabled="!exampleId"
        color="primary"
        class="text-capitalize me-2"
        @click="openCreate"
      >
        Create
      </v-btn>
      <v-btn
        :disabled="!exampleId"
        color="error"
        class="text-capitalize me-2"
        @click="deleteSelected"
      >
        Delete
      </v-btn>
      <v-btn
        :disabled="!exampleId"
        color="secondary"
        class="text-capitalize"
        @click="archiveSelected"
      >
        Archive
      </v-btn>

      <v-spacer />
      <v-progress-circular v-if="isLoading" indeterminate size="20" />
    </v-card-title>

    <!-- Tabela principal -->
    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="discussions"
      item-key="id"
      dense
      show-select
      class="elevation-1"
    >

      <!-- Coluna ACTIONS -->
<template v-slot:[`item.actions`]="{ item }">
  <div class="d-flex flex-column align-center ">
    <v-btn
      color="primary"
      dark
      small
      class="mt-2 mb-2"
      :style="{ minWidth: '160px' }"
      @click="openVote(item)"
    >
      Vote
    </v-btn>

    <v-btn
      color="primary"
      dark
      small
      class="mb-2"
      :style="{ minWidth: '160px' }"
      @click="openChat(item)"
    >
      Chat
    </v-btn>

    <v-btn
      color="primary"
      dark
      small
      class="mb-2"
      :style="{ minWidth: '160px' }"
      @click="openCreateRule(item)"
    >
      Create New Rule
    </v-btn>

    <v-btn
      color="primary"
      dark
      small
      class="mb-2"
      :style="{ minWidth: '160px' }"
      @click="openCheckVotes(item)"
    >
      Check Votes
    </v-btn>
  </div>
</template>






    </v-data-table>

    <!-- Diálogo de criação/edição -->
    <discussion-create
      :show.sync="dialogCreate"
      :edited="edited"
      @cancel="dialogCreate = false"
      @save="saveDiscussion"
    />

    <!-- Pop-ups vazios -->
    <v-dialog v-model="dialogVote"   max-width="400"><v-card /></v-dialog>
    <v-dialog v-model="dialogChat"   max-width="400"><v-card /></v-dialog>
    <v-dialog v-model="dialogRule"   max-width="400"><v-card /></v-dialog>
    <v-dialog v-model="dialogCheck"  max-width="400"><v-card /></v-dialog>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import DiscussionCreate from '~/components/discussion/DiscussionCreate.vue'

export default Vue.extend({
  components: { DiscussionCreate },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  data () {
    return {
      isLoading:    false,
      examples:     [] as Array<{ id: number; text: string }>,
      discussions:  [] as any[],
      selected:     [] as any[],
      dialogCreate: false,
      edited:       { id: null, title: '', description: '' } as any,
      /* Pop-ups */
      dialogVote:   false,
      dialogChat:   false,
      dialogRule:   false,
      dialogCheck:  false,
      current:      null as any | null
    }
  },

  async fetch () {
    this.isLoading = true
    try {
      const { items } = await this.$services.example.list(this.projectId, {})
      this.examples = items.map(e => ({
        id: e.id,
        text: e.upload_name || e.filename || `${e.id}`
      }))

      this.discussions = this.exampleId
        ? await this.$repositories.discussion.list(this.projectId, this.exampleId)
        : []
    } finally {
      this.isLoading = false
    }
  },

  computed: {
    projectId (): string { return this.$route.params.id },
    exampleId: {
      get (): number { return Number(this.$route.query.example) || 0 },
      set (v: number) { this.$router.push({ query: { example: v } }) }
    },
    headers (): Array<any> {
      return [
        { text: 'Title',  value: 'title' },
        { text: 'Rules',  value: 'rules' },
        { text: 'Status',  value: 'status' },
        { text: 'Actions', value: 'actions', width: 170}
      ]
    }
  },

  watch: {
    '$route.query.example' () { this.$fetch() }
  },

  methods: {
    /* Toolbar */
    openCreate () {
      this.edited = { id: null, title: '', description: '' }
      this.dialogCreate = true
    },
    async saveDiscussion ({ title }: { title: string }) {
      await this.$repositories.discussion.create(
        this.projectId,
        this.exampleId,
        { title }
      )
      await this.fetch()
      this.dialogCreate = false
    },

    /* Ações */
    openVote       (item: any) { this.current = item; this.dialogVote  = true },
    openChat       (item: any) { this.current = item; this.dialogChat  = true },
    openCreateRule (item: any) { this.current = item; this.dialogRule  = true },
    openCheckVotes (item: any) { this.current = item; this.dialogCheck = true },

    /* Ainda por implementar */
    deleteSelected () { /* TODO */ },
    archiveSelected () { /* TODO */ }
  }
})
</script>

<style>
.me-4 { margin-right: 1rem; }
.me-2 { margin-right: 0.5rem; }

</style>
