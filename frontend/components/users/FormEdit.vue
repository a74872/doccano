<template>
  <v-card elevation="2" class="rounded-lg">
    <!-- Header -->
    <v-toolbar flat color="primary" dark>
      <v-toolbar-title>
        <v-icon left>mdi-pencil</v-icon>
        {{ $t('generic.edit') }}
      </v-toolbar-title>
      <v-spacer />
      <v-btn icon @click="$emit('cancel')">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <!-- Form -->
    <v-card-text class="pa-4">
      <v-form v-model="valid" ref="form" @submit.prevent="saveUser">
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="first_name"
              :label="$t('First Name')"
              :rules="[(v) => !!v || $t('First name is required')]"
              prepend-inner-icon="mdi-account"
              outlined dense clearable
              required
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="last_name"
              :label="$t('Last Name')"
              :rules="[(v) => !!v || $t('Last name is required')]"
              prepend-inner-icon="mdi-account"
              outlined dense clearable
              required
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="username"
              :label="$t('Username')"
              :rules="usernameRules"
              prepend-inner-icon="mdi-account-box"
              outlined dense clearable
              required
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="email"
              :label="$t('Email')"
              :rules="emailRules"
              prepend-inner-icon="mdi-email"
              type="email"
              outlined dense clearable
              required
            />
          </v-col>
          <v-col cols="6">
            <v-switch
              v-model="isSuperuser"
              :label="$t('Superuser')"
              color="primary"
              inset
            />
          </v-col>
          <v-col cols="6">
            <v-switch
              v-model="isStaff"
              :label="$t('Staff')"
              color="primary"
              inset
            />
          </v-col>
        </v-row>

        <v-alert v-if="errorMessage" type="error" dense class="mt-3">
          {{ errorMessage }}
        </v-alert>
      </v-form>
    </v-card-text>

    <!-- Actions -->
    <v-divider />
    <v-card-actions class="pa-4">
      <v-spacer />
      <v-btn text @click="$emit('cancel')">
        {{ $t('generic.cancel') }}
      </v-btn>
      <v-btn
        color="primary"
        :disabled="!valid"
        :loading="loading"
        @click="saveUser"
      >
        {{ $t('update') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { User } from '~/domain/models/user'

export default Vue.extend({
  name: 'EditUserCard',
  props: {
    user: {
      type: Object as () => User,
      required: true
    }
  },
  data() {
    return {
      valid: false,
      loading: false,
      first_name: '',
      last_name: '',
      username: '',
      email: '',
      isSuperuser: false,
      isStaff: false,
      errorMessage: ''
    }
  },
  computed: {
    usernameRules() {
      return [
        (v: string) => !!v || this.$t('User name is required'),
        (v: string) => v.length <= 30 || this.$t('User name is too long')
      ]
    },
    emailRules() {
      return [
        (v: string) => !!v || this.$t('User email is required'),
        (v: string) => /.+@.+\..+/.test(v) || this.$t('User email must be valid'),
        (v: string) => v.length <= 254 || this.$t('User email is too long')
      ]
    }
  },
  watch: {
    user: {
      handler(user) {
        if (user) {
          this.first_name = user.first_name || ''
          this.last_name = user.last_name || ''
          this.username = user.username || ''
          this.email = user.email || ''
          this.isSuperuser = user.isSuperuser || false
          this.isStaff = user.isStaff || false
        }
      },
      immediate: true
    }
  },
  methods: {
    async saveUser() {
      const form = this.$refs.form as Vue & { validate: () => boolean }
      if (!form.validate()) return

      this.loading = true
      this.errorMessage = ''

      try {
        const updatedUser = {
          ...this.user,
          first_name: this.first_name,
          last_name: this.last_name,
          username: this.username,
          email: this.email,
          isSuperuser: this.isSuperuser,
          isStaff: this.isStaff
        }

        await this.$emit('save', updatedUser)
      } catch (e: any) {
        this.errorMessage = e.response?.data?.detail || this.$t('generic.error')
      } finally {
        this.loading = false
      }
    }
  }
})
</script>

<style scoped>
/* Garante alinhamento correto do texto nos campos */
.v-text-field >>> .v-input__control .v-input__slot {
  text-align: left;
}

.v-text-field >>> input {
  text-align: left !important;
}
</style>