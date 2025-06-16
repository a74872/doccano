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

      <div class="d-flex align-center">
        <v-btn
          :disabled="!exampleId"
          color="primary"
          class="text-capitalize me-2"
          @click="openCreate"
        >
          Create
        </v-btn>
        <v-btn
          v-if="isProjectAdmin"
          :disabled="!exampleId"
          color="error"
          class="text-capitalize me-2"
          @click="deleteSelected"
        >
          Delete
        </v-btn>
        <v-btn
          v-if="isProjectAdmin"
          :disabled="!canArchive"
          color="secondary"
          class="text-capitalize"
          @click="archiveSelected"
        >
          Archive
        </v-btn>
      </div>
      
      <v-spacer />
      <v-progress-circular v-if="isLoading" indeterminate size="20" />
    </v-card-title>

    <!-- Tabela principal -->
   <div style="max-height: 600px; overflow-y:auto">
    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="unresolvedList"
      item-key="id"
      dense
      show-select
      class="elevation-1"

      :items-per-page="-1"
      hide-default-footer
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
      Chat 💬
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

<!-- Coluna RULES: mostra chips com o título de cada regra -->
<template v-slot:[`item.rules`]="{ item }">
  <div class="d-flex flex-wrap">
    <v-chip
      v-for="rule in item.rules"
      :key="rule.id"
      small
      class="ma-1"
      color="primary"
      text-color="white"
    >
      {{ rule.title }}
    </v-chip>
    <!-- se preferir só quantidade, use: {{ item.rules.length }} -->
  </div>
</template>


    </v-data-table>
    </div>

    <!-- Diálogo de criação/edição -->
    <discussion-create
      :show.sync="dialogCreate"
      :edited="edited"
      @cancel="dialogCreate = false"
      @save="saveDiscussion"
    />

    <discussion-vote-dialog
      v-if="current"
      v-model="dialogVote"
      :project-id="projectId"
      :example-id="exampleId"
      :discussion="current"
      @voted="$fetch()"
    />

    <discussion-rules-dialog
      v-if="chatDiscussion"
      v-model="dialogChat"
      :project-id="projectId"
      :example-id="exampleId"
      :discussion="chatDiscussion"
    />

    <discussion-rule-form
      :show.sync="dialogRule"
      @save="createRules"
    />

    <discussion-votes-summary-dialog
      v-if="current"
      :show.sync="dialogCheck"
      :project-id="projectId"
      :example-id="exampleId"
      :discussion="current"
      @votes-error="onVotesError"
    />

    <!-- ——— CONFIRMAR eliminação ——— -->
    <v-dialog v-model="confirmDelete" max-width="420">
      <v-card>
        <v-card-title class="headline">
          Delete {{ selected.length }} discussion<span v-if="selected.length>1">s</span>?
        </v-card-title>
        <v-card-text>
          This action is irreversible.
        </v-card-text>

        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="confirmDelete=false">Cancel</v-btn>
          <v-btn color="error" text @click="doDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

         <!-- Archived (expansível) -->
    <v-expansion-panels v-model="archivedOpen" accordion class="mt-4">
      <v-expansion-panel>
        <v-expansion-panel-header>
          Archived Discussions ({{ archivedList.length }})
        </v-expansion-panel-header>

        <v-expansion-panel-content>
          <div style="max-height: 600px; overflow-y:auto">
            <v-data-table
              :headers="headers"
              :items="archivedList"
              item-key="id"
              dense
              class="elevation-1"
              :items-per-page="-1"
              hide-default-footer
            >

              <!-- SLOT RULES -->
              <template #[`item.rules`]="{ item }">
                <div class="d-flex flex-wrap">
                  <v-chip
                    v-for="r in item.rules"
                    :key="r.id"
                    small
                    class="ma-1"
                    color="primary"
                    text-color="white"
                  >
                    {{ r.title }}
                  </v-chip>
                </div>
              </template>

              <!-- SLOT ACTIONS -->
              <template #[`item.actions`]="{ item }">
                <div class="d-flex flex-column align-center">
                  <v-btn
                    small dark color="primary" class="my-1"
                    :style="{ minWidth: '160px' }"
                    @click="openCheckVotes(item)"
                  >
                    Check Votes
                  </v-btn>
                </div>
              </template>

            </v-data-table>
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Snackbar para erros -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      top
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

  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import DiscussionCreate from '~/components/discussion/DiscussionCreate.vue'
import DiscussionRulesDialog   from '~/components/discussion/DiscussionRulesDialog.vue'
import DiscussionRuleForm from '~/components/discussion/DiscussionRuleForm.vue'
import DiscussionVoteDialog from '~/components/discussion/DiscussionVoteDialog.vue'
import DiscussionVotesSummaryDialog from '~/components/discussion/DiscussionVotesSummaryDialog.vue'

/** devolve 'Resolved' (≥70 % num único voto) ou 'Unresolved' */
function computeStatus (disc: any): 'Resolved' | 'Unresolved' {
  /* se ainda não existem regras, continua por resolver */
  if (!Array.isArray(disc.rules) || disc.rules.length === 0) {
    return 'Unresolved'
  }

  /* junta todos os títulos de regra votados */
  const votos = disc.rules.flatMap((r: any) =>
    (r.votes || []).map(() => r.title)
  )

  if (votos.length === 0) return 'Unresolved'   // ninguém votou ainda

  /* contagens por regra */
  const cont: Record<string, number> = {}
  votos.forEach(t => { cont[t] = (cont[t] || 0) + 1 })

  const top   = Math.max(...Object.values(cont))
  const ratio = top / votos.length               // maioria dominante

  return ratio >= 0.7 ? 'Resolved' : 'Unresolved'
}


export default Vue.extend({
  components: {
  DiscussionCreate,
  DiscussionRulesDialog,
  DiscussionRuleForm,
  DiscussionVoteDialog,
  DiscussionVotesSummaryDialog
  },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data () {
    return {
      isLoading:    false,
      examples:     [] as Array<{ id: number; text: string }>,
      discussions:  [] as any[],
      selected:     [] as any[],
      dialogCreate: false,
      isProjectAdmin: false,
      edited:       { id: null, title: '', description: '' } as any,
      /* Pop-ups */
      dialogVote:   false,
      dialogCheck:  false,
      confirmDelete: false,
      dialogChat : false,
      chatDiscussion: null as any|null,
      dialogRule: false,
      current:      null as any | null,
      unresolved: [] as any[],
      archived  : [] as any[],
      archivedOpen: null as number|null,
      snackbar: {
        show: false,
        message: '',
        color: 'error',
        timeout: 6000
      }
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

        const data = this.exampleId
          ? await this.$repositories.discussion.list(this.projectId, this.exampleId)
          : []

        // acrescenta status
        this.discussions = data.map((d:any) => ({
          ...d,
          status: computeStatus(d)       // ← «Resolved» | «Unresolved»
        }))
      } catch (err: any) {
        this.showError('Erro de base de dados. Tenta novamente mais tarde')
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

    unresolvedList () {
      return this.discussions.filter((d:any) => !d.archived)
    },
    archivedList () {
      return this.discussions.filter((d:any) => d.archived)
    },
    canArchive () {
      return this.selected.length > 0 &&
             this.selected.every((d:any) => d.status === 'Resolved')
    },

    headers (): Array<any> {
      return [
        { text: 'Title',  value: 'title' },
        { text: 'Rules',  value: 'rules' },
        { text: 'Status',  value: 'status' },
        { text: 'Description',  value: 'description' },
        { text: 'Actions', value: 'actions',sortable:false, width: 170}
      ]
    }
  },

    async created() {
    try {
      const member = await this.$repositories.member.fetchMyRole(
        this.projectId
      )
      this.isProjectAdmin = member.isProjectAdmin
    } catch (err: any) {
      this.showError('Erro de base de dados. Tenta novamente mais tarde')
    }
  },

  watch: {
    '$route.query.example' () { this.$fetch() }
  },

  methods: {
    showError(message: string) {
      this.snackbar.message = message
      this.snackbar.color = 'error'
      this.snackbar.show = true
    },

    openCreate () {
      this.edited = { id: null, title: '', description: '' }
      this.dialogCreate = true
    },

    async saveDiscussion (
      { title, description }: { title: string; description: string }
    ) {
      try {
        await this.$repositories.discussion.create(
          this.projectId,
          this.exampleId,
          { title, description }
        )

        await this.$fetch()          // ← em vez de this.fetch()

        this.dialogCreate = false
      } catch (err: any) {
        this.showError('Erro de base de dados. Tenta novamente mais tarde')
      }
    },

    openVote (discussion:any){
      this.current   = discussion
      this.dialogVote = true
    },

    openChat (discussion: any) {
        this.chatDiscussion = discussion
        this.$nextTick(() => { this.dialogChat = true })
      },

    /* ————————————————— abrir o diálogo ————————————————— */
    openCreateRule (discussion: any) {
      this.current    = discussion
      this.dialogRule = true
    },

    /* ————————————————— gravar regras ————————————————— */
    async createRules (titles: string[]) {
      if (!this.current) return

      // Verificar se já existem regras com os mesmos nomes
      const existingRuleNames = this.current.rules?.map((r: any) => r.title.toLowerCase()) || []
      
      for (const title of titles) {
        if (existingRuleNames.includes(title.toLowerCase())) {
          this.showError(`Já existe uma regra definida com o nome "${title}"`)
          return
        }
      }

      try {
        await Promise.all(
          titles.map(t =>
            this.$repositories.rule.create(
              this.projectId,                       // ① projectId
              this.exampleId,                       // ② exampleId (da query)
              this.current.id,                      // ③ discussionId
              { title: t }
            )
          )
        )

        await this.$fetch()
      } catch (err: any) {
        this.showError('Erro de base de dados. Tenta novamente mais tarde')
      }
    },

    openCheckVotes (discussion:any){
      this.current    = discussion
      this.dialogCheck = true
    },

    /* ────────────────────────────── DELETE ────────────────────────────── */
    deleteSelected () {
      if (this.selected.length === 0) return
      this.confirmDelete = true
    },

    async doDelete () {
      this.confirmDelete = false
      if (!this.selected.length) return

      this.isLoading = true
      try {
        await Promise.all(
          this.selected.map((d:any) =>
            this.$repositories.discussion.remove(
              this.projectId,        // project
              this.exampleId,        // dataset escolhido
              d.id                   // discussion UUID
            )
          )
        )

        this.selected = []
        await this.$fetch()
      } catch (err:any) {
        this.showError('Erro de base de dados. Tenta novamente mais tarde')
      } finally {
        this.isLoading = false
      }
    },

    async archiveSelected () {
      if (!this.canArchive) return

      this.isLoading = true
      try {
        await Promise.all(
          this.selected.map((d:any) =>
            this.$repositories.discussion.patch(
              this.projectId,
              this.exampleId,
              d.id,
              { archived: true }
            )
          )
        )
        this.selected = []
        await this.$fetch()
      } catch (err:any) {
        this.showError('Erro de base de dados. Tenta novamente mais tarde')
      } finally {
        this.isLoading = false
      }
    },

    onVotesError() {
      this.snackbar = {
        show: true,
        message: 'Connection error to the server. Please, try again later.',
        color: 'error',
        timeout: 6000
      }
    },
  }
})
</script>

<style>
.me-4 { margin-right: 1rem; }
.me-2 { margin-right: 0.5rem; }

</style>