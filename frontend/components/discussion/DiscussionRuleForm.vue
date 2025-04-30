<template>
  <v-dialog
    :value="localShow"
    max-width="400"
    @input="val => $emit('update:show', val)"
  >
    <v-card>
      <v-card-title class="headline">New rule</v-card-title>
      <v-card-text>
        <v-text-field
          v-model="localTitle"
          label="Rule title"
          outlined
          dense
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="cancel">Cancel</v-btn>
        <v-btn
          color="primary"
          text
          :disabled="!localTitle.trim()"
          @click="add"
        >
          Add
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'DiscussionRuleForm',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    ruleTitle: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      localShow: this.show,
      localTitle: this.ruleTitle
    }
  },
  watch: {
    show(val: boolean) {
      this.localShow = val
    },
    ruleTitle(val: string) {
      this.localTitle = val
    }
  },
  methods: {
    cancel() {
      // fecha o diálogo sem criar
      this.$emit('update:show', false)
      this.localTitle = this.ruleTitle   // opcional: reset
    },
    add() {
      // emite o texto atual da regra
      this.$emit('add', this.localTitle.trim())
      this.$emit('update:show', false)
      this.localTitle = ''
    }
  }
})
</script>
