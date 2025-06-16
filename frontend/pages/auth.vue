<template>
  <v-app id="inspire">
    <!-- o fundo está aplicado nesta div -->
    <v-main class="bg-login">               <!-- ① -->
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <form-login :login="authenticateUser" />
            <social-login :fetch-social-link="fetchSocialLink" />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapActions } from 'vuex'
import FormLogin   from '@/components/auth/FormLogin.vue'
import SocialLogin from '@/components/auth/SocialLogin.vue'

export default Vue.extend({
  components: { FormLogin, SocialLogin },

  methods: {
    ...mapActions('auth', ['authenticateUser', 'fetchSocialLink'])
  }
})
</script>

<style scoped>
.bg-login {
  background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(~@/assets/galaxy.jpg) center / cover no-repeat fixed;
  min-height: 100vh;
}
</style>
