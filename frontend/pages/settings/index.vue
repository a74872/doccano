<template>
  <v-app id="inspire">
  <!-- o fundo está aplicado nesta div -->
    <v-main class="bg-login">
    <v-card>
      <v-card-title v-if="isStaff">
        <v-btn class="text-capitalize" color="primary" @click.stop="dialogCreate = true">
          {{ $t('generic.create') }}
        </v-btn>
        <v-dialog v-model="dialogCreate" max-width="900">
          <form-create
          @cancel="dialogCreate = false"
          @save="onSave"
          @created="onCreateSuccess"
          @failed="onCreateError"/>
        </v-dialog>

        <v-btn
          class="text-capitalize ms-2"
          :disabled="!canEdit"
          outlined
          @click.stop="dialogEdit = true"
        >
          {{ $t('generic.edit') }}
        </v-btn>
        <v-dialog v-model="dialogEdit">
          <form-edit
            :user="selected[0]"
            @cancel="dialogEdit = false"
            @save="onEditSave"
          />
        </v-dialog>

        <v-btn
          class="text-capitalize ms-2"
          :disabled="!canDelete"
          outlined
          @click.stop="dialogDelete = true"
        >
          {{ $t('generic.delete') }}
        </v-btn>
        <v-dialog v-model="dialogDelete" max-width="400">
          <form-delete :selected="selected" @cancel="onDeleteCancel" @remove="remove" />
        </v-dialog>
      </v-card-title>

      <users-list
        v-model="selected"
        :items="users.items"
        :is-loading="isLoading"
        :total="users.count"
        @update:query="updateQuery"
        @search="onSearch"
    />
    </v-card>
    <!-- ───────────── SNACKBAR GLOBAL ───────────── -->
    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      top mid
      timeout="4000"
    >
      {{ snackbar.text }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.visible = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
   </v-main>
  </v-app>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue from 'vue'
import { mapGetters } from 'vuex'
import UsersList from '@/components/users/UsersList.vue'
import FormDelete from '@/components/users/FormDelete.vue'
import FormCreate from '@/components/settings/FormCreate.vue'
import FormEdit from '@/components/users/FormEdit.vue'
import { Page } from '~/domain/models/page'
import { User } from '~/domain/models/user'
import { SearchQueryData } from '~/services/application/user/userApplicationService'

export default Vue.extend({
  components: {
    UsersList,
    FormDelete,
    FormCreate,
    FormEdit
  },
  layout: 'projects',
  middleware: ['check-auth', 'auth'],

  data() {
    return {
      dialogCreate: false,
      dialogDelete: false,
      dialogEdit: false,
      users: new Page<User>(0, null, null, []),
      selected: [] as User[],
      isLoading: false,
      snackbar: {
        visible: false,
        text   : '',
        color  : 'success'   // success | error
      }
    }
  },

  async fetch() {
    await this.fetchUsers()
  },

  computed: {
    ...mapGetters('auth', ['isStaff']),
    canDelete(): boolean {
      return this.selected.length > 0
    },
    canEdit(): boolean {
      return this.selected.length === 1 // Edit is only available when exactly one user is selected
    }
  },

  watch: {
    '$route.query': _.debounce(function () {
      this.$fetch()
    }, 500)
  },

  methods: {
    onCreateSuccess() {
      this.dialogCreate = false
      this.fetchUsers()
      this.showSnack('New user created successfully', 'success')
    },
    onCreateError(msg:string) {
      this.showSnack(msg, 'error')
    },

    showSnack(text:string, color:'success'|'error') {
      this.snackbar.text   = text
      this.snackbar.color  = color
      this.snackbar.visible = true
    },

    async fetchUsers() {
      this.isLoading = true
      try {
        this.users = await this.$repositories.user.list(this.$route.query as SearchQueryData)
      } catch (error) {
        console.error('Erro ao buscar usuários:', error)
      }
      this.isLoading = false
    },

    updateQuery({ query }: { query: any }) {
    this.$router.push({ query })
  },
  onSearch(search: string) {
    const query = { ...this.$route.query, search }
    this.updateQuery({ query })
  },

    onSave() {
      this.dialogCreate = false
      this.$fetch()
    },

async onEditSave(updatedUser: User) {
  try {
    await this.$repositories.user.update(updatedUser.id, updatedUser)
    this.dialogEdit = false
    this.$fetch()
    this.showSnack('Utilizador editado com sucesso!', 'success')
  } catch (error) {
    console.error('Erro ao atualizar utilizador:', error)
    
    let errorMessage = 'Erro ao atualizar utilizador'
    
    // Username já existe
    if (error.response?.status === 400 || 
        error.response?.status === 409 || 
        error.response?.data?.message?.includes('username')) {
      errorMessage = 'Nome de utilizador já existe. Por favor, escolha outro.'
    }
    // Erro geral de BD/servidor
    else if (error.response?.status >= 500) {
      errorMessage = 'Erro do servidor de base de dados. Tente novamente mais tarde.'
    }
    
    this.showSnack(errorMessage, 'error')
  }
}
,

    async remove() {
      try {
        console.log("Iniciando remoção de utilizadores. Selecionados:", this.selected);
        const ids = this.selected.map(user => user.id);
        console.log("IDs dos usuários a serem deletados:", ids);
        await this.$repositories.user.bulkDelete(ids);
        console.log("Exclusão em lote realizada com sucesso.");
        await this.$fetch();
        this.dialogDelete = false;
        this.selected = [];
        this.showSnack('User deleted successfully', 'success');
        console.log("Dialog de deleção fechado e seleção limpa.");
      } catch (error) {
        console.error("Erro ao deletar usuários:", error);
      }
    },
    onDeleteCancel() {
      this.dialogDelete = false;
      this.showSnack('User deletion cancelled', 'error');
    }
  }
})
</script>
<style scoped>
.bg-login {
  background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(~@/assets/galaxy.jpg) center / cover no-repeat fixed;
  min-height: 100vh;
}
</style>
