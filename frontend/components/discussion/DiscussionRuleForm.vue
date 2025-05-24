<template>
  <v-dialog
    :value="show"
    max-width="500"
    @input="$emit('update:show', $event)"
    scrollable
  >
    <v-card>
      <v-card-title class="headline">New rule(s)</v-card-title>

      <v-divider/>

      <!-- lista dinâmica de inputs -->
      <v-card-text>
        <v-slide-y-transition group appear>
          <div v-for="(rule, idx) in rules" :key="idx" class="d-flex align-center mb-2">
            <v-text-field
              v-model="rules[idx]"
              outlined dense hide-details
              :counter="60"
              label="Rule title"
              class="flex-grow-1"
              :rules="[v => !!v.trim() || 'Required']"
            />
            <v-btn
              icon
              class="ms-2"
              @click="remove(idx)"
              v-if="rules.length > 1"
            >
              <v-icon small>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-slide-y-transition>

        <v-btn
          small text
          color="primary"
          class="mt-2"
          :disabled="rules.length >= 5"
          @click="addField"
        >
          <v-icon left small>mdi-plus</v-icon>
          Add rule
        </v-btn>
        <small class="grey--text d-block mt-1">
          You can add up to 5 rules.
        </small>
      </v-card-text>

      <v-divider/>

      <!-- acções -->
      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="$emit('update:show', false)">Cancel</v-btn>
        <v-btn
          color="primary"
          text
          :disabled="!canSave"
          @click="save"
        >Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'DiscussionRuleForm',
  props: {
    show:       { type: Boolean, default: false },
    // opcional: título inicial único (para modo “editar” no futuro)
    ruleTitle:  { type: String,  default: '' }
  },
  data () {
    return {
      rules: this.ruleTitle ? [this.ruleTitle] : ['']   // pelo menos 1 campo
    }
  },
  computed: {
    canSave (): boolean {
      return (
        this.rules.length > 0 &&
        this.rules.every(r => r.trim().length > 0)
      )
    }
  },
  watch: {
    show (v:boolean) {
      if (v && this.rules.length === 0) this.rules = ['']
    }
  },
  methods: {
    addField ()   { if (this.rules.length < 5) this.rules.push('') },
    remove (idx:number) { this.rules.splice(idx, 1) },
    save () {
      const titles = this.rules.map(r => r.trim()).filter(Boolean)
      this.$emit('save', titles)
      this.$emit('update:show', false)
      this.rules = ['']              // reset para próxima vez
    }
  }
})
</script>
