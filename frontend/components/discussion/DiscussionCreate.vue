<!-- frontend/components/discussion/DiscussionCreate.vue -->
<template>
  <v-dialog v-model="dialog" max-width="600">
    <v-card>
      <v-card-title class="headline">
        {{ localEdited.id ? 'Edit discussion' : 'Create discussion' }}
      </v-card-title>

      <v-card-text>
        <v-text-field
          v-model="localEdited.title"
          label="Title"
          required
          outlined
          dense
        />
      </v-card-text>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="onCancel">Cancel</v-btn>
        <v-btn color="primary" text @click="onSave">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    show:    { type: Boolean, default: false },
    edited:  { type: Object as () => { id?: string; title: string }, required: true }
  },

  data() {
    return {
      localEdited: { id: this.edited.id||null, title: this.edited.title||'' }
    }
  },

  watch: {
    edited(newVal: any) {
      this.localEdited = { id: newVal.id||null, title: newVal.title||'' }
    }
  },

  computed: {
    dialog: {
      get() { return this.show },
      set(v: boolean) { this.$emit('update:show', v) }
    }
  },

  methods: {
    onCancel() {
      this.dialog = false
      this.$emit('cancel')
    },
    onSave() {
      this.$emit('save', { id: this.localEdited.id, title: this.localEdited.title })
    }
  }
})
</script>
