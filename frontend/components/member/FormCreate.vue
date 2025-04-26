<template>
  <base-card
    :disabled="!valid"
    :title="$t('members.addMember')"
    :agree-text="$t('generic.save')"
    :cancel-text="$t('generic.cancel')"
    @agree="$emit('save')"
    @cancel="$emit('cancel')"
  >
    <template #content>
      <v-form v-model="valid">
        <v-autocomplete
          v-model="user"
          :items="users"
          :loading="isLoading"
          :search-input.sync="username"
          hide-no-data
          open-on-focus
          item-text="username"
          :label="$t('members.userSearchAPIs')"
          :placeholder="$t('members.userSearchPrompt')"
          :prepend-icon="mdiAccount"
          :rules="[rules.userRequired]"
          return-object
          @focus="fetchUsers"
          @update:search-input="onSearch"
        />

        <v-select
          v-model="role"
          :items="roles"
          item-text="name"
          item-value="id"
          :label="$t('members.role')"
          :rules="[rules.roleRequired]"
          return-object
          :prepend-icon="mdiCreditCardOutline"
        >
          <template #item="props">
            {{ $translateRole(props.item.name, $t('members.roles')) }}
          </template>
          <template #selection="props">
            {{ $translateRole(props.item.name, $t('members.roles')) }}
          </template>
        </v-select>

        <v-alert v-if="errorMessage" prominent type="error">
          <v-row align="center">
            <v-col class="grow">
              {{ errorMessage }}
            </v-col>
          </v-row>
        </v-alert>
      </v-form>
    </template>
  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiAccount, mdiCreditCardOutline } from '@mdi/js'
import BaseCard from '@/components/utils/BaseCard.vue'
import { RoleItem } from '~/domain/models/role/role'
import { UserItem } from '~/domain/models/user/user'

export default Vue.extend({
  name: 'FormCreateMember',

  components: { BaseCard },

  props: {
    value: {
      type: Object as any,
      required: true
    },
    errorMessage: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      valid: false,
      isLoading: false,
      users: [] as UserItem[],
      roles: [] as RoleItem[],
      username: '',
      rules: {
        userRequired: (v: UserItem | null) => (!!v && !!v.username) || this.$t('generic.required'),
        roleRequired: (v: RoleItem | null) => (!!v && !!v.name) || this.$t('generic.required')
      },
      mdiAccount,
      mdiCreditCardOutline
    }
  },

  computed: {
    user: {
      get(): UserItem | null {
        if (!this.value.user) return null
        return {
          id: this.value.user,
          username: this.value.username,
          isStaff: false,
          isSuperuser: false
        }
      },
      set(u: UserItem | null) {
        if (!u) {
          this.$emit('input', { ...this.value, user: null, username: '' })
        } else {
          this.$emit('input', {
            ...this.value,
            user: u.id,
            username: u.username
          })
        }
      }
    },
    role: {
      get(): RoleItem | null {
        if (!this.value.role) return null
        return { id: this.value.role, name: this.value.rolename }
      },
      set(r: RoleItem | null) {
        if (!r) {
          this.$emit('input', { ...this.value, role: null, rolename: '' })
        } else {
          this.$emit('input', {
            ...this.value,
            role: r.id,
            rolename: r.name
          })
        }
      }
    }
  },

  watch: {
    username(newVal: string) {
      // dispara busca apenas se tiver algo digitado
      if (newVal && !this.isLoading) {
        this.fetchUsers()
      }
      if (!newVal) {
        this.users = []
      }
    }
  },

  async created() {
    // Carrega as roles apenas uma vez
    this.roles = await this.$repositories.role.list()
  },

  methods: {
    async fetchUsers() {
      this.isLoading = true
      try {
        // Atenção: DRF SearchFilter usa o param "search"
        const page = await this.$repositories.user.list({ search: this.username })
        console.log('Usuários recebidos (page.items):', page.items)
        this.users = (page as any).items || []
      } catch (err) {
        console.error('Erro ao buscar usuários:', err)
        this.users = []
      } finally {
        this.isLoading = false
      }
    },

    onSearch(val: string) {
      this.username = val
      // a busca vai disparar pelo watcher
    }
  }
})
</script>
