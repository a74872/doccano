<template>
  <div>
    <v-dialog
      v-model="dialog"
      max-width="500"
    >
      <v-card>
        <v-card-title class="headline">
          {{ title }} {{ qty }} discussion(s)?
        </v-card-title>
        <v-card-actions>
          <v-spacer/>
          <v-btn
            text
            @click="onCancel"
          >
            Cancel
          </v-btn>
          <v-btn
            :color="color"
            text
            @click="onConfirm"
            :loading="loading"
            :disabled="loading"
          >
            Archive
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar para erros de base de dados -->
    <v-snackbar
      v-model="showErrorSnackbar"
      color="error"
      timeout="6000"
      top
    >
      Erro de base de dados
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="showErrorSnackbar = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    show: {
      type: Boolean,
      default: false
    },
    qty: {
      type: Number,
      default: 0
    },
    title: {
      type: String,
      default: ''
    },
    color: {
      type: String,
      default: 'grey'
    }
  },

  data() {
    return {
      loading: false,
      showErrorSnackbar: false
    }
  },

  computed: {
    // em vez de usar v-model sobre o prop, usamos este computed
    dialog: {
      get(): boolean {
        return this.show
      },
      set(val: boolean) {
        // emite um evento para o pai atualizar o `show`
        this.$emit('update:show', val)
      }
    }
  },

  methods: {
    onCancel() {
      // fechar o diálogo
      this.dialog = false
      this.$emit('cancel')
    },

    async onConfirm() {
      try {
        this.loading = true

        // Emite o evento de confirmação e aguarda a resposta
        this.$emit('confirm')

        // Se chegou aqui, a operação foi bem-sucedida
        this.dialog = false

      } catch (error) {
        // Mostra o snackbar de erro
        this.showErrorSnackbar = true
        console.error('Erro na operação:', error)
      } finally {
        this.loading = false
      }
    },

    // Método para mostrar o erro externamente (caso o pai queira controlar)
    showDatabaseError() {
      this.showErrorSnackbar = true
    }
  }
})
</script>

<style scoped>
/* ... o teu CSS ... */
</style>