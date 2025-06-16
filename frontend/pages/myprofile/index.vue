<template>
  <v-container class="d-flex align-center justify-center fill-height pt-10">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card class="pa-4">
          <v-card-title class="text-h5 d-flex align-center">
            <v-icon left color="deep-purple accent-4" class="mr-2">mdi-account-circle</v-icon>
            My Profile
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text v-if="user" class="mt-4">
            <v-simple-table>
              <template #default>
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Username</strong></td>
                    <td>{{ user.username }}</td>
                  </tr>
                  <tr>
                    <td><strong>First Name</strong></td>
                    <td>{{ user.first_name }}</td>
                  </tr>
                  <tr>
                    <td><strong>Last Name</strong></td>
                    <td>{{ user.last_name }}</td>
                  </tr>
                  <tr>
                    <td><strong>Email</strong></td>
                    <td>{{ user.email || 'Not provided' }}</td>
                  </tr>
                  <tr>
                    <td><strong>Staff</strong></td>
                    <td>{{ user.isStaff ? 'Yes' : 'No' }}</td>
                  </tr>
                  <tr>
                    <td><strong>Superuser</strong></td>
                    <td>{{ user.isSuperuser ? 'Yes' : 'No' }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
          <v-card-text v-else-if="loading" class="text-center mt-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-2">Loading profile...</p>
          </v-card-text>
          <v-divider class="mt-4"></v-divider>
          <v-card-actions class="justify-space-between mt-2">
            <div>
              <v-btn color="primary" text @click="goBack">Back</v-btn>
              <v-btn color="secondary" text>Edit Profile</v-btn>
            </div>
            <v-btn color="error" text @click="signout">⏻ Logout</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Snackbar para erros -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      top
    >
      {{ snackbar.text }}
      <template #action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import { mdiLogout } from '@mdi/js'
import { mapActions } from 'vuex'
import Vue from 'vue'
import { UserItem } from '~/domain/models/user'

export default Vue.extend({
  data() {
    return {
      user: null as UserItem | null,
      loading: false,
      mdiLogout,
      snackbar: {
        show: false,
        text: '',
        color: 'error',
        timeout: 5000
      }
    }
  },

  async mounted() {
    // Verificar autenticação simples
    if (!this.isAuthenticated()) {
      this.showAuthError()
      setTimeout(() => {
        this.$router.push(this.localePath('/'))
      }, 2000)
      return
    }

    // Carregar perfil do utilizador
    await this.loadProfile()
  },

  methods: {
    ...mapActions('auth', ['logout']),

    goBack() {
      this.$router.push(this.localePath('/projects'))
    },

    signout() {
      this.logout()
      this.$router.push(this.localePath('/'))
    },

    async loadProfile() {
      this.loading = true
      try {
        this.user = await this.$repositories.user.getProfile()
      } catch (error) {
        console.error('Failed to fetch user profile:', error)

        // Verificar se é erro de autenticação
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          this.showAuthError()
          setTimeout(() => {
            this.$router.push(this.localePath('/'))
          }, 2000)
          return
        }

        // Verificar se é erro de base de dados
        if (this.isDatabaseError(error)) {
          this.showDatabaseError()
          setTimeout(() => {
            this.$router.push(this.localePath('/'))
          }, 2000)
          return
        }

        // Outros erros
        this.showGenericError()
      } finally {
        this.loading = false
      }
    },

    isAuthenticated(): boolean {
      try {
        // Verificar diferentes métodos de autenticação
        return !!(
          this.$store?.getters?.['auth/isAuthenticated'] ||
          this.$auth?.loggedIn ||
          this.$cookies?.get('auth-token') ||
          (typeof window !== 'undefined' && localStorage.getItem('auth-token'))
        )
      } catch (error) {
        console.error('Error checking authentication:', error)
        return false
      }
    },

    isDatabaseError(error: any): boolean {
      // Verificar diferentes tipos de erros de base de dados
      if (error?.response?.status >= 500 && error?.response?.status < 600) {
        return true
      }

      if (error?.code === 'ECONNREFUSED' ||
          error?.code === 'ENOTFOUND' ||
          error?.code === 'ETIMEDOUT') {
        return true
      }

      const errorMessage = error?.message?.toLowerCase() || ''
      if (errorMessage.includes('database') ||
          errorMessage.includes('connection') ||
          errorMessage.includes('server') ||
          errorMessage.includes('timeout')) {
        return true
      }

      if (error?.response?.status === 503) {
        return true
      }

      return false
    },

    showDatabaseError() {
      this.snackbar = {
        show: true,
        text: 'Erro de Base de Dados. Tente novamente mais tarde',
        color: 'error',
        timeout: 5000
      }
    },

    showAuthError() {
      this.snackbar = {
        show: true,
        text: 'Acesso não autorizado. Por favor, faça login.',
        color: 'warning',
        timeout: 4000
      }
    },

    showGenericError() {
      this.snackbar = {
        show: true,
        text: 'Erro ao carregar perfil. Tente novamente.',
        color: 'error',
        timeout: 4000
      }
    }
  }
})
</script>

<style scoped>
.v-container {
  height: 100vh;
  padding-top: 20px;
}
.v-card {
  max-width: 500px;
  margin: auto;
}
</style>