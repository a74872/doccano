<template>
  <base-card
    :disabled="!valid"
    :title="$t('user.login')"
    :agree-text="$t('user.login')"
    @agree="tryLogin"
  >
    <template #content>
      <v-form v-model="valid">
        <v-alert
          v-show="showError"
          type="error"
          dense
          dismissible
        >
          {{ errorText }}
        </v-alert>

        <v-text-field
          v-model="username"
          :rules="userNameRules($t('rules.userNameRules'))"
          :label="$t('user.username')"
          name="username"
          :prepend-icon="mdiAccount"
          autofocus
          @keyup.enter="tryLogin"
        />

        <v-text-field
          v-model="password"
          :rules="passwordRules($t('rules.passwordRules'))"
          :label="$t('user.password')"
          name="password"
          :prepend-icon="mdiLock"
          type="password"
          @keyup.enter="tryLogin"
        />
      </v-form>
    </template>
  </base-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiAccount, mdiLock } from '@mdi/js'
import { userNameRules, passwordRules } from '@/rules/index'
import BaseCard from '@/components/utils/BaseCard.vue'

export default Vue.extend({
  components: { BaseCard },

  props: {
    login: {
      type: Function,
      default: () => Promise
    }
  },

  data () {
    return {
      valid       : false,
      username    : '',
      password    : '',
      userNameRules,
      passwordRules,
      showError   : false,
      errorMsgKey : 'errors.invalidUserOrPass',
      mdiAccount,
      mdiLock
    }
  },

  computed: {
    errorText (): string {
      return this.$t(this.errorMsgKey) as string
    }
  },

  methods: {
  async tryLogin () {
      try {
        await this.login({
          username: this.username,
          password: this.password
        })
        this.$router.push(this.localePath('/projects'))
      } catch (err: any) {
        console.error('Login error ▶', err)
        console.log('err.message:', err.message)
        console.log('err.request:', err.request)
        console.log('err.response:', err.response)
        console.log('  status:', err.response?.status)
        console.log('  headers:', err.response?.headers)
        console.log('  data:', err.response?.data)

        const status = err.response?.status
        if (status === 401) {
          this.errorMsgKey = 'errors.invalidUserOrPass'
        } else {
          this.errorMsgKey = 'errors.serverUnavailable'
        }

        this.showError = true
      }
    }
}
})
</script>


