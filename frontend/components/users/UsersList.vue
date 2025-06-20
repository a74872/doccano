<template>
  <div>
    <v-data-table
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
      class="elevation-1"
      @input="$emit('input', $event)"
      @update:options="updateQuery({ query: $route.query })"
    >
      <!-- Campo de Pesquisa -->
      <template #top>
        <v-text-field
          v-model="search"
          :prepend-inner-icon="mdiMagnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
          @input="emitSearch"
        />
      </template>

      <!-- Nome de Usuário com ícone -->
      <template #[`item.username`]="{ item }">
        <v-btn title="Ver detalhes" icon small @click="showDetails(item)" >
          <v-icon>{{ mdiChevronDown }}</v-icon>
        </v-btn>
        {{ item.username }}
      </template>

      <!-- Coluna Staff (true/false) -->
      <template #[`item.isStaff`]="{ item }">
        {{ item.isStaff }}
      </template>


      <!-- Coluna Superuser (true/false) -->
      <template #[`item.isSuperuser`]="{ item }">
        {{ item.isSuperuser }}
      </template>

      <!-- Coluna Ações -->
      <template #[`item.actions`]="{ item }">
        <v-icon color="primary" class="cursor-pointer" title="Ver detalhes" small @click="showDetails(item)">
          mdi-eye
        </v-icon>
      </template>
    </v-data-table>

    <!-- Diálogo de Detalhes -->
    <v-dialog v-model="showDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon left color="deep-purple accent-4">mdi-account-circle</v-icon>
          User Details
        </v-card-title>
        <v-card-text v-if="selectedUser">
             <p><strong>ID:</strong> {{ selectedUser.id }}</p>
            <p><strong>💗 Username:</strong> {{ selectedUser.username }}</p>
            <p><strong>🧍 Primeiro Nome:</strong> {{ selectedUser.first_name }}</p>
            <p><strong>🧍 Último Nome:</strong> {{ selectedUser.last_name }}</p>
            <p><strong>📧 Email:</strong> {{ selectedUser.email || 'Não informado' }}</p>
            <p><strong>👥 Staff:</strong> {{ selectedUser.isStaff ? '✅ Sim' : '❌ Não' }}</p>
            <p><strong>🛡️ Superuser:</strong> {{ selectedUser.isSuperuser ? '✅ Sim' : '❌ Não' }}</p>
                </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="showDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { mdiMagnify, mdiChevronDown } from '@mdi/js'
import type { PropType } from 'vue'
import Vue from 'vue'
import { DataOptions } from 'vuetify/types'
import { UserItem } from '~/domain/models/user'

export default Vue.extend({
  props: {
    isLoading: {
      type: Boolean,
      default: false,
      required: true
    },
    items: {
      type: Array as PropType<UserItem[]>,
      default: () => [],
      required: true
    },
    value: {
      type: Array as PropType<UserItem[]>,
      default: () => [],
      required: true
    },
    total: {
      type: Number,
      default: 0,
      required: true
    }
  },
  data() {
  return {
    search: this.$route.query.search || '',
    options: {} as DataOptions,
    mdiMagnify,
    mdiChevronDown,
    showDialog: false,
    selectedUser: null as UserItem | null
  }
},

  computed: {
    headers(): { text: any; value: string; sortable?: boolean }[] {
      return [
        { text: 'Username', value: 'username', sortable: true },
        { text: 'First Name', value: 'first_name' },
        { text: 'Last Name', value: 'last_name' },
        { text: 'Joined in', value: 'date_joined' },
        { text: 'Last Login', value: 'last_login' },
      ]
    }
  },

  watch: {
    options: {
      handler() {
        this.updateQuery({
          query: {
            limit: this.options.itemsPerPage.toString(),
            offset: ((this.options.page - 1) * this.options.itemsPerPage).toString(),
            q: this.search
          }
        })
      },
      deep: true
    },
    search() {
      this.updateQuery({
        query: {
          limit: this.options.itemsPerPage.toString(),
          offset: '0',
          q: this.search
        }
      })
      this.options.page = 1
    }
  },

  methods: {
  emitSearch() {
    this.$emit('search', this.search)
  },
  updateQuery(payload: any) {
    const { sortBy, sortDesc } = this.options
    const ordering = sortBy?.[0] ? (sortDesc?.[0] ? '-' + sortBy[0] : sortBy[0]) : ''
    const query = {
      ...payload.query,
      q: this.search, // utiliza "search"
      ordering
    }
    console.log("Atualizando query:", query);
    this.$emit('update:query', { query })
  },
  onSearch(search: string) {
    // Cria uma query com a chave "search"
    const query = { ...this.$route.query, q: search }
    this.updateQuery({ query })
  },
  showDetails(user: UserItem) {
    this.selectedUser = user
    this.showDialog = true
  }
}

})
</script>