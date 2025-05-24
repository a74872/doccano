<template>
  <v-dialog
    :value="show"
    max-width="600"
    scrollable
    @input="$emit('update:show', $event)"
  >
    <v-card>
      <v-card-title class="headline">
        Votes overview
        <v-spacer/>
        <v-btn icon @click="$emit('update:show', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider/>

      <!-- Loading -->
      <v-card-text v-if="loading" class="text-center py-6">
        <v-progress-circular indeterminate/>
      </v-card-text>

      <!-- Tabela principal -->
      <v-card-text v-else>
        <v-simple-table dense>
          <thead>
            <tr><th>Member</th><th class="text-right">Chosen rule</th></tr>
          </thead>
          <tbody>
            <tr v-for="m in members" :key="m.id">
              <td>{{ m.username }}</td>
              <td class="text-right">
                {{ ruleByUser[m.username] || '—' }}
              </td>
            </tr>
          </tbody>
        </v-simple-table>

        <!-- Resumo percentagens -->
        <v-divider class="my-4"/>

        <div v-for="row in summary"
             :key="row.title"
             class="d-flex justify-space-between px-2 py-1">
          <span>{{ row.title }}</span>
          <span>{{ row.count }} ({{ row.percent }}%)</span>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

interface Member { id:number; username:string }

export default Vue.extend({
  props:{
    show       : { type:Boolean, required:true },
    projectId  : { type:String,  required:true },
    exampleId  : { type:Number,  required:true },
    discussion : { type:Object,  required:true }   // contém id
  },

  data(){
    return {
      loading : false,
      members : [] as Member[],
      ruleByUser : {} as Record<number, string>,      // userId → rule.title
      summary  : [] as Array<{title:string,count:number,percent:string}>
    }
  },

  watch:{
    show(v){ v && this.fetch() },
    discussion(){ this.show && this.fetch() }
  },

  methods:{
    /* ── carrega membros + votos ── */
    async fetch () {
      this.loading = true
      try {
        /* 1) membros do projecto */
        const { data: mem } = await this.$axios.get(
          `/v1/projects/${this.projectId}/members`
        )
        this.members = mem                                  // [{id, username}]

        /* 2) regras + votos */
        const url =
          `/v1/projects/${this.projectId}` +
          `/discussion/examples/${this.exampleId}` +
          `/${this.discussion.id}/rules/`
        const { data } = await this.$axios.get(url)
        const rules = Array.isArray(data) ? data : data.results

        /* -------------- ALTERAÇÃO AQUI -------------- */
        const map: Record<string, string> = {}              // username → rule.title
        rules.forEach((r: any) =>
          (r.votes || []).forEach((v: any) => { map[v.username] = r.title })
        )
        this.ruleByUser = map
        /* -------------------------------------------- */

        /* resumo */
        const counts: Record<string, number> = {}
        Object.values(map).forEach(t => { counts[t] = (counts[t] || 0) + 1 })
        const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1
        this.summary = Object.entries(counts)
          .map(([title, count]) => ({
            title, count,
            percent: ((count / total) * 100).toFixed(1)
          }))
          .sort((a, b) => b.count - a.count)
      } finally { this.loading = false }
    }
  }
})
</script>
