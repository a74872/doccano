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
                    <td><strong>ID</strong></td>
                    <td>{{ user.id }}</td>
                  </tr>
                  <tr>
                    <td><strong>Username</strong></td>
                    <td>{{ user.username }}</td>
                  </tr>
                  <tr>
                    <td><strong>First Name</strong></td>
                    <td>{{ user.firstName }}</td>
                  </tr>
                  <tr>
                    <td><strong>Last Name</strong></td>
                    <td>{{ user.lastName }}</td>
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
      mdiLogout
    }
  },
  async created() {
    try {
      this.user = await this.$repositories.user.getProfile()
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
    }
  },
  methods: {
    ...mapActions('auth', ['logout']),
    goBack() {
      this.$router.push(this.localePath('/projects'))
    },
    signout() {
      this.logout()
      this.$router.push(this.localePath('/'))
    }
  }
})
</script>

<style scoped>
.v-container {
  height: 100vh;
  padding-top: 20px; /* Adiciona espaçamento extra no topo */
}
.v-card {
  max-width: 500px;
  margin: auto;
}
</style>
