<template>
  <div>
    <!-- search bar -->
    <v-text-field
      v-model="search"
      prepend-inner-icon="mdi-magnify"
      dense
      flat
      solo-inverted
      hide-details
      :placeholder="$t('generic.search')"
      class="mb-2"
    />

    <!-- data-table -->
    <v-data-table
      :value="model"
      :headers="headers"
      :items="filtered"
      item-key="id"
      show-select
      dense
      :loading="loading"
      :footer-props="{ itemsPerPageOptions: [10,25,50] }"
      @input="$emit('input', $event)"
    >
      <!-- slot de status -->
      <template slot="item.status" slot-scope="{ item }">
        <v-chip small :color="item.is_resolved ? 'success' : 'warning'" text>
          {{ item.is_resolved ? 'Resolved' : 'Pending' }}
        </v-chip>
      </template>

      <!-- slot de rules -->
      <template slot="item.rules" slot-scope="{ item }">
        <v-chip
          v-for="r in item.rules"
          :key="r.id"
          x-small
          class="ma-1"
          :color="r.active ? 'primary' : 'grey'"
          text
        >
          {{ r.title }}
        </v-chip>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  /* eslint-disable vue/no-mutating-props */

  props: {
    value:   { type: Array,   default: () => [] },
    items:   { type: Array,   default: () => [] },
    loading: { type: Boolean, default: false }
  },

  data() {
    return {
      search: ''
    }
  },

  computed: {
    // Emula v-model na prop `value`
    model: {
      get(): any[] {
        return this.value
      },
      set(v: any[]) {
        this.$emit('input', v)
      }
    },
    headers() {
      return [
        { text: 'ID',     value: 'id',     width: 70 },
        { text: 'Title',  value: 'title',  sortable: false },
        { text: 'Status', value: 'status', sortable: false },
        { text: 'Rules',  value: 'rules',  sortable: false }
      ]
    },
    filtered() {
      if (!this.search.trim()) return this.items
      const q = this.search.toLowerCase()
      return this.items.filter(d => d.title.toLowerCase().includes(q))
    }
  }
})
</script>
