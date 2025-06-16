<template>
  <v-dialog :value="value" max-width="420" @input="$emit('input', $event)">
    <v-card>
      <v-card-title class="headline">Export report</v-card-title>

      <v-card-text>
        <p class="mb-4">Choose the format you want to download the current table:</p>
        <v-radio-group v-model="format" column>
          <v-radio label="CSV" value="csv" />
          <v-radio label="PDF" value="pdf" />
        </v-radio-group>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="$emit('input', false)">Cancel</v-btn>
        <v-btn color="primary" :disabled="!format" @click="exportFile">
          Download
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import { saveAs } from 'file-saver'
// ✅ usa export nomeado e alias PascalCase → evita import/no-named-as-default
import { jsPDF as JsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

export default Vue.extend({
  name: 'ExportReportDialog',

  props: {
    // v‑model
    value:   { type: Boolean, required: true },
    // nome base do ficheiro a exportar
    title:   { type: String,  default: 'report' },
    // cabeçalhos da tabela [{ text, value }]
    headers: { type: Array,   required: true },
    // linhas visíveis na tabela
    items:   { type: Array,   required: true }
  },

  data () {
    return { format: '' as 'csv' | 'pdf' | '' }
  },

  methods: {
    exportFile () {
      if (!this.format) return

      /* ======================= CSV ======================= */
      if (this.format === 'csv') {
      const DELIM = ';'                     // ① novo delimitador
      const quote = (v: any) => {
        // Converte undefined/null para '', escapa aspas duplas
        return `"${String(v ?? '').replace(/"/g, '""')}"`
      }

      const headerRow = (this.headers as any[])
        .map(h => quote(h.text))
        .join(DELIM)

      const bodyRows = (this.items as any[]).map(row =>
        (this.headers as any[]).map(h => quote(row[h.value])).join(DELIM)
      )

      // ② BOM à frente da string
      const csv = '\uFEFF' + [headerRow, ...bodyRows].join('\r\n')

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
      saveAs(blob, `${this.title}.csv`)

      } else {
        const doc = new JsPDF({ orientation: 'landscape', unit: 'pt' })
        const head = [(this.headers as any[]).map(h => h.text)]
        const body = (this.items as any[]).map(row =>
          (this.headers as any[]).map(h => row[h.value])
        )

        autoTable(doc, { head, body, styles: { fontSize: 8 } })
        doc.save(`${this.title}.pdf`)
      }

      this.$emit('input', false)
      this.format = ''
    }
  }
})
</script>

<style scoped>
/* sem estilos específicos por agora */
</style>
