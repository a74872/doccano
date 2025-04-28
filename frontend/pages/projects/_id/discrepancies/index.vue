<template>
  <v-card>
    <!-- Admin controls -->
    <v-card-title v-if="isProjectAdmin">
      <v-btn
        class="text-capitalize ms-2"
        :disabled="!canDelete"
        outlined
        @click.stop="dialogDelete = true"
      >
        {{ $t('generic.delete') }}
      </v-btn>
      <v-spacer />
      <v-btn
        :disabled="!item.count"
        class="text-capitalize"
        color="error"
        @click="dialogDeleteAll = true"
      >
        {{ $t('generic.deleteAll') }}
      </v-btn>

      <!-- Single-delete dialog -->
      <v-dialog v-model="dialogDelete">
        <form-delete
          :selected="selected"
          :item-key="itemKey"
          @cancel="dialogDelete = false"
          @remove="remove"
        />
      </v-dialog>

      <!-- Bulk-delete dialog -->
      <v-dialog v-model="dialogDeleteAll">
        <form-delete-bulk
          @cancel="dialogDeleteAll = false"
          @remove="removeAll"
        />
      </v-dialog>

      <!-- Assignment dialog -->
      <v-dialog v-model="dialogAssignment">
        <form-assignment
          @assigned="assigned"
          @cancel="dialogAssignment = false"
        />
      </v-dialog>

      <!-- Reset assignment dialog -->
      <v-dialog v-model="dialogReset">
        <form-reset-assignment
          @cancel="dialogReset = false"
          @reset="resetAssignment"
        />
      </v-dialog>
    </v-card-title>

    <!-- Image list for image projects -->
    <image-list
      v-if="project.isImageProject"
      v-model="selected"
      :items="item.items"
      :is-admin="user.isProjectAdmin"
      :is-loading="isLoading"
      :members="members"
      :total="item.count"
      @update:query="updateQuery"
      @click:labeling="movePage"
      @assign="assign"
      @unassign="unassign"
    />

    <!-- Audio list for audio projects -->
    <audio-list
      v-else-if="project.isAudioProject"
      v-model="selected"
      :items="item.items"
      :is-admin="user.isProjectAdmin"
      :is-loading="isLoading"
      :members="members"
      :total="item.count"
      @update:query="updateQuery"
      @click:labeling="movePage"
      @assign="assign"
      @unassign="unassign"
    />

    <!-- Document list for text projects -->
    <document-list
      v-else
      v-model="selected"
      :items="item.items"
      :is-admin="user.isProjectAdmin"
      :is-loading="isLoading"
      :members="members"
      :total="item.count"
      :labels="labels"
      @update:query="updateQuery"
      @click:labeling="movePage"
      @show-used-labels="openStats"
      @edit="editItem"
      @assign="assign"
      @unassign="unassign"
      @verify-discrepancies="openVerify"
    />

    <!-- ═══════════════ Used-Labels dialog ═══════════════ -->
    <v-dialog v-model="dialogStats" max-width="500">
      <v-card>
        <v-card-title class="headline">Label usage</v-card-title>
        <v-simple-table dense>
          <thead>
            <tr>
              <th>Label</th>
              <th class="text-right">Count</th>
              <th class="text-right">%</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in stats" :key="row.id">
              <td>
                <v-chip
                  :color="row.backgroundColor"
                  :text-color="row.textColor"
                  small
                  class="me-1"
                >
                  {{ row.text }}
                </v-chip>
              </td>
              <td class="text-right">{{ row.count }}</td>
              <td class="text-right">{{ row.percent }}%</td>
            </tr>
          </tbody>
        </v-simple-table>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="dialogStats = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogVerify" max-width="500">
      <v-card>
        <v-card-title class="headline">Verify discrepancies</v-card-title>
        <v-simple-table dense>
          <thead>
            <tr><th>Member</th><th>Label</th></tr>
          </thead>
          <tbody>
              <tr v-for="row in verifyRows" :key="row.user"
                  :class="row.mismatch ? 'red--text text--darken-2' : ''">
                <td>{{ row.user }}</td>
                <td>
                  <v-chip
                    v-for="lab in row.labels"
                    :key="lab.text"
                    :color="lab.color"
                    :text-color="$contrastColor(lab.color)"
                    small
                    class="me-1"
                  >
                    {{ lab.text }}
                  </v-chip>
                </td>
              </tr>
            </tbody>

        </v-simple-table>

        <v-divider />

        <v-card-text class="font-italic">{{ verifyMsg }}</v-card-text>

        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="dialogVerify=false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import { mapGetters } from 'vuex'
import Vue from 'vue'
import { Distribution } from '~/domain/models/metrics/metrics'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'
import DocumentList from '@/components/discrepancies/DocumentList.vue'
import FormAssignment from '~/components/example/FormAssignment.vue'
import FormDelete from '@/components/example/FormDelete.vue'
import FormDeleteBulk from '@/components/example/FormDeleteBulk.vue'
import FormResetAssignment from '~/components/example/FormResetAssignment.vue'
import AudioList from '~/components/example/AudioList.vue'
import ImageList from '~/components/example/ImageList.vue'
import { ExampleDTO, ExampleListDTO } from '~/services/application/example/exampleData'
import { MemberItem } from '~/domain/models/member/member'
import { LabelItem } from '~/domain/models/label/label'

export default Vue.extend({
  components: {
    AudioList,
    DocumentList,
    ImageList,
    FormAssignment,
    FormDelete,
    FormDeleteBulk,
    FormResetAssignment
  },

  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      dialogDelete: false,
      dialogDeleteAll: false,
      dialogAssignment: false,
      dialogReset: false,
      item: {} as ExampleListDTO,
      selected: [] as ExampleDTO[],
      members: [] as MemberItem[],
      user: {} as MemberItem,
      labels: [] as LabelItem[],
      isLoading: false,
      isProjectAdmin: false,
      dialogStats: false,
      distribution: {} as Distribution,
      stats: [] as Array<LabelItem & { count:number; percent:number }>,
      dialogVerify : false,
      verifyRows   : [] as Array<{user:string,label:string,color:string}>,
      verifyMsg    : ''
    }
  },

  async fetch() {
    this.isLoading = true
    this.item = await this.$services.example.list
    (
      this.projectId,
      this.$route.query
    )
    this.user = await this.$repositories.member.fetchMyRole(this.projectId)
    if (this.user.isProjectAdmin) {
      this.members = await this.$repositories.member.list(this.projectId)
    }
    // Fetch project labels
    this.labels = await this.$services.categoryType.list(this.projectId)

    await Promise.all(
      this.item.items.map(async (example: ExampleDTO) => {
        const dist = await this.$repositories.metrics.fetchCategoryDistribution(
          this.projectId,
          { example: example.id }           // só este example
        )

        const usedLabels = new Set<string>()

        for (const user in dist) {
          Object.entries(dist[user])        // ⇐ [label, count]
            .filter(([, count]) => count > 0)
            .forEach(([label]) => usedLabels.add(label))
        }

        // só há discrepância se mais de UMA label realmente usada
        this.$set(example, 'has_discrepancy', usedLabels.size > 1)
      })
    )

    this.isLoading = false
  },

  computed: {
    ...mapGetters('projects', ['project']),

    canDelete(): boolean {
      return this.selected.length > 0
    },

    projectId(): string {
      return this.$route.params.id
    },

    itemKey(): string {
      return this.project.isImageProject || this.project.isAudioProject
        ? 'filename'
        : 'text'
    }
  },

  watch: {
    '$route.query': _.debounce(function () {
      this.$fetch()
    }, 1000)
  },

  async created() {
    const member = await this.$repositories.member.fetchMyRole(
      this.projectId
    )
    this.isProjectAdmin = member.isProjectAdmin
  },

  methods: {
    async remove() {
      await this.$services.example.bulkDelete(
        this.projectId,
        this.selected
      )
      this.$fetch()
      this.dialogDelete = false
      this.selected = []
    },

    async removeAll() {
      await this.$services.example.bulkDelete(this.projectId, [])
      this.$fetch()
      this.dialogDeleteAll = false
      this.selected = []
    },

    updateQuery(query: object) {
      this.$router.push(query)
    },

    movePage(query: object) {
      const link = getLinkToAnnotationPage(
        this.projectId,
        this.project.projectType
      )
      this.updateQuery({ path: this.localePath(link), query })
    },

    editItem(item: ExampleDTO) {
      this.$router.push(`dataset/${item.id}/edit`)
    },

    async assign(exampleId: number, userId: number) {
      await this.$repositories.assignment.assign(
        this.projectId,
        exampleId,
        userId
      )
      this.item = await this.$services.example.list(
        this.projectId,
        this.$route.query
      )
    },

    async unassign(assignmentId: string) {
      await this.$repositories.assignment.unassign(
        this.projectId,
        assignmentId
      )
      this.item = await this.$services.example.list(
        this.projectId,
        this.$route.query
      )
    },

    async assigned() {
      this.dialogAssignment = false
      this.item = await this.$services.example.list(
        this.projectId,
        this.$route.query
      )
    },

    async resetAssignment() {
      this.dialogReset = false
      await this.$repositories.assignment.reset(this.projectId)
      this.item = await this.$services.example.list(
        this.projectId,
        this.$route.query
      )
    },

    async openStats({ example }: { example: ExampleDTO }) {
      this.stats = []

      const dist = await this.$repositories.metrics
        .fetchCategoryDistribution(this.projectId, { example: example.id })

      const sum: Record<string, number> = {}
      for (const user in dist) {
        for (const lbl in dist[user]) {
          sum[lbl] = (sum[lbl] || 0) + dist[user][lbl]
        }
      }

      const total = Object.values(sum).reduce((a, b) => a + b, 0)

      this.stats = this.labels
        .filter(l => sum[l.text])
        .map(l => ({
          ...l,
          count: sum[l.text],
          percent: ((sum[l.text] / total) * 100).toFixed(1)
        }))
        .sort((a, b) => b.count - a.count)

      this.dialogStats = true
    },



    async openVerify({ example }: { example: ExampleDTO }) {
      const dist = await this.$repositories.metrics
        .fetchCategoryDistribution(this.projectId, { example: example.id })

      const rows: any[] = []

      for (const user in dist) {
        // entradas do tipo [['Positive', 3], ['Negative', 1]]
        const pairs = Object.entries(dist[user])

        // 1) maior contagem
        const max  = Math.max(...pairs.map(([, c]) => c))

        // 2) todas as labels que têm a contagem “max”
        const top  = pairs.filter(([, c]) => c === max)

        // 3) escolha de visual:
        //    - se empate, mostra "Positive / Negative"
        //    - senão só a label com maior voto
        const labelObjs = top.map(([txt]) => {
          const meta = this.labels.find(l => l.text === txt) || {}
          return { text: txt, color: meta.backgroundColor || '#ccc' }
        })

        rows.push({
          user,
          labels: labelObjs           // ← array, não string única
        })
      }

      const mismatch = new Set(rows.map(r => r.labels[0].text)).size > 1
      this.verifyRows = rows.map(r => ({ ...r, mismatch }))
      this.verifyMsg  = mismatch
        ? 'Discrepancies have been detected, different labels were used!'
        : 'No discrepancies have been detected, all labels used were equal.'
      this.dialogVerify = true
    }

  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}
</style>