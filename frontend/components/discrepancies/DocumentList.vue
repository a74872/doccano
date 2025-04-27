<template>
  <v-data-table
    :value="value"
    :headers="headers"
    :items="items"
    :options.sync="options"
    :server-items-length="total"
    :search="search"
    :loading="isLoading"
    :loading-text="$t('generic.loading')"
    :no-data-text="$t('vuetify.noDataAvailable')"
    :footer-props="{
      showFirstLastPage: true,
      'items-per-page-options': [10, 50, 100],
      'items-per-page-text': $t('vuetify.itemsPerPageText'),
      'page-text': $t('dataset.pageText')
    }"
    item-key="id"
    show-select
    @input="$emit('input', $event)"
  >
    <!-- Search field -->
    <template #top>
      <v-text-field
        v-model="search"
        :prepend-inner-icon="mdiMagnify"
        :label="$t('generic.search') + ' (e.g. label:positive)'"
        single-line
        hide-details
        filled
      />
    </template>

    <!-- Status -->
    <template #[`item.isConfirmed`]="{ item }">
      <v-chip
        :color="item.isConfirmed ? 'success' : 'warning'"
        text
        small
      >
        {{ item.isConfirmed ? 'Finished' : 'In progress' }}
      </v-chip>
    </template>

    <!-- Text -->
    <template #[`item.text`]="{ item }">
      <span class="d-flex d-sm-none">
        {{ item.text | truncate(50) }}
      </span>
      <span class="d-none d-sm-flex">
        {{ item.text | truncate(200) }}
      </span>
    </template>

    <!-- Discrepancies -->
    <template #[`item.has_discrepancy`]="{ item }">
      <v-chip
        :color="item.has_discrepancy ? 'error' : 'grey'"
        text
        small
      >
        {{ item.has_discrepancy ? 'Yes' : 'No' }}
      </v-chip>
    </template>

    <!-- Labels -->
    <template #[`item.labels`]>
      <div class="d-flex flex-wrap py-2">
        <v-chip
          v-for="label in labels"
          :key="label.id"
          small
          :color="label.backgroundColor"
          :text-color="label.textColor"
          class="me-1 mb-1"
        >
          {{ label.text }}
        </v-chip>
      </div>
    </template>

    <!-- Members -->
    <template #[`item.assignee`]>
      <div class="d-flex flex-column py-2">
        <span
          v-for="member in members"
          :key="member.user"
          class="mb-1"
        >
          {{ member.username }}
        </span>
      </div>
    </template>

    <!-- Actions -->
    <template #[`item.action`]="{ item }">
      <div class="d-flex flex-column mt-2">
        <v-btn
          class="mb-2"
          small
          color="primary text-capitalize"
          @click="$emit('show-used-labels',  { example: item })"
        >
          Show Used Labels
        </v-btn>

        <v-btn
          class="mb-2"
          small
          color="primary text-capitalize"
          @click="$emit('discussion', item)"
        >
          Discussion
        </v-btn>
        <v-btn
          class="mb-2"
          small
          color="primary text-capitalize"
          @click="$emit('verify-discrepancies', item)"
        >
          Verify Discrepancies
        </v-btn>
      </div>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMagnify } from '@mdi/js'
import type { PropType } from 'vue'
import { DataOptions } from 'vuetify/types'
import { ExampleDTO } from '~/services/application/example/exampleData'
import { LabelItem } from '~/domain/models/label/label'
import { MemberItem } from '~/domain/models/member/member'

export default Vue.extend({
  props: {
    isLoading: { type: Boolean, default: false, required: true },
    items: { type: Array as PropType<ExampleDTO[]>, default: () => [], required: true },
    value: { type: Array as PropType<ExampleDTO[]>, default: () => [], required: true },
    total: { type: Number, default: 0, required: true },
    members: { type: Array as PropType<MemberItem[]>, default: () => [], required: true },
    labels: { type: Array as PropType<LabelItem[]>, default: () => [] },
    isAdmin: { type: Boolean, default: false }
  },
  data() {
    return {
      search: this.$route.query.q,
      options: {} as DataOptions,
      mdiMagnify
    }
  },
  computed: {
    headers() {
      return [
        { text: 'Status', value: 'isConfirmed', sortable: false },
        { text: this.$t('dataset.text'), value: 'text', sortable: false },
        { text: 'Discrepancies', value: 'has_discrepancy', sortable: false },
        { text: 'Labels', value: 'labels', sortable: false },
        { text: 'Members', value: 'assignee', sortable: false },
        { text: this.$t('dataset.action'), value: 'action', sortable: false }
      ]
    }
  }
})
</script>