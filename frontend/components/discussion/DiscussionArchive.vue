<template>
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
        >
          Archive
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
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
    onConfirm() {
      this.$emit('confirm')
    }
  }
})
</script>

<style scoped>
/* ... o teu CSS ... */
</style>
