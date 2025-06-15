<template>
  <base-card
    title="Delete Settings"
    :agree-text="$t('generic.yes')"
    :cancel-text="$t('generic.cancel')"
    @agree="onAgree"
    @cancel="onCancel"
  >
    <template #content>
      Are you sure you want to delete the following settings?
      <v-list dense>
        <v-list-item v-for="(item, i) in selected" :key="i">
          <v-list-item-content>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </template>
  </base-card>
</template>

<script>
import Vue from 'vue'
import BaseCard from '@/components/utils/BaseCard.vue'

export default Vue.extend({
  components: {
    BaseCard
  },

  props: {
    selected: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        timeout: 3000
      }
    }
  },
  methods: {
    onAgree() {
      this.$emit('remove')
      this.showSnack('Configuração deletada com sucesso!', 'success')
    },
    onCancel() {
      this.$emit('cancel')
      this.showSnack('Exclusão cancelada.', 'error')
    },
    showSnack(text, color = 'success') {
      this.snackbar.text = text
      this.snackbar.color = color
      this.snackbar.show = true
    }
  },
  <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout" top right>
    {{ snackbar.text }}
  </v-snackbar>
</script>