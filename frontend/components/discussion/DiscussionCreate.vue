<template>
  <v-dialog
    v-model="dialog"
    max-width="600"
  >
    <v-card>
      <!-- Cabeçalho -->
      <v-card-title class="headline">
        {{ localEdited.id ? 'Edit discussion' : 'Create discussion' }}
      </v-card-title>

      <!-- Corpo do formulário -->
      <v-card-text>
        <!-- Título -->
        <v-text-field
          v-model="localEdited.title"
          label="Title"
          required
          outlined
          dense
        />

        <!-- Descrição -->
        <v-textarea
          v-model="localEdited.description"
          label="Description"
          rows="4"
          outlined
          dense
        />
      </v-card-text>

      <!-- Ações -->
      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="onCancel">
          Cancel
        </v-btn>
        <v-btn color="primary" text @click="onSave">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'DiscussionCreate',

  props: {
    show: {
      type: Boolean,
      default: false
    },
    // O objeto `edited` poderá conter id (em edição), title e description
    edited: {
      type: Object as () => {
        id?: string
        title: string
        description?: string
      },
      required: true
    }
  },

  data() {
    return {
      // Clonar o prop para não mutar diretamente
      localEdited: {
        id: this.edited.id || null,
        title: this.edited.title || '',
        description: this.edited.description || ''
      }
    }
  },

  watch: {
    // Sempre que `edited` mudar por fora, atualiza a cópia interna
    edited: {
      handler(newVal) {
        this.localEdited = {
          id: newVal.id || null,
          title: newVal.title || '',
          description: newVal.description || ''
        }
      },
      deep: true
    }
  },

  computed: {
    // Para ligar o v-model ao prop `show`
    dialog: {
      get(): boolean {
        return this.show
      },
      set(val: boolean) {
        this.$emit('update:show', val)
      }
    }
  },

  methods: {
    onCancel() {
      // Fecha o diálogo
      this.dialog = false
      this.$emit('cancel')
    },
    onSave() {
      // Emite os dados para o pai
      this.$emit('save', {
        id: this.localEdited.id,
        title: this.localEdited.title,
        description: this.localEdited.description
      })
    }
  }
})
</script>
