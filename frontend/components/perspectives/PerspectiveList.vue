<template>
  <v-container>
    <v-btn color="primary" @click="$router.push(`/projects/${projectId}/perspective/add`)">
      Adicionar Perspetiva
    </v-btn>

    <v-data-table
      :headers="headers"
      :items="perspectives"
      item-value="id"
      class="mt-4"
    >
      <!-- Corrigido para usar a abreviação `#top` ao invés de `v-slot:top` -->
      <template #top>
        <v-toolbar flat>
          <v-toolbar-title>Perspetivas</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
      </template>

      <!-- Corrigido para usar um nome de slot válido: `#item-actions` -->
      <template #item-actions="{ item }">
        <v-btn icon @click="deletePerspective(item.id)">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </template>
    </v-data-table>

    <v-alert
      v-if="error"
      type="error"
      dismissible
      class="mt-4"
    >
      {{ error }}
    </v-alert>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      projectId: null,
      perspectives: [],
      headers: [
        { text: "Nome", value: "name" },
        { text: "Tipo de Dado", value: "data_type" },
        { text: "Ações", value: "actions", sortable: false },
      ],
      error: null,
    };
  },
  async mounted() {
    this.projectId = this.$route.params.id;
    if (!this.projectId) {
      this.error = "ID do projeto não encontrado.";
      return;
    }
    await this.fetchPerspectives();
  },
  methods: {
      async fetchPerspectives() {
        console.log(">>> Chamando getPerspectives com projectId:", this.projectId);
        try {
          this.error = null;
          const data = await this.$repositories.perspective.getPerspectives(this.projectId);
          console.log(">>> Dados recebidos:", data);
          this.perspectives = data;
        } catch (error) {
          console.error("Erro ao carregar perspetivas:", error);
          this.error = "Erro ao carregar perspetivas. Veja o console para mais detalhes.";
        }
      },
      // Certifique-se de definir também o método deletePerspective, se necessário.
},

};
</script>