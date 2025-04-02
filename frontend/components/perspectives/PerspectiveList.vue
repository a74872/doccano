<template>
  <v-container>
    <v-btn color="primary" @click="$router.push(`/projects/${projectId}/perspective/add`)">
      Create new Perspective
    </v-btn>

    <!-- Botão para excluir as perspectivas selecionadas -->
    <v-btn color="error" class="ml-2" @click="openConfirmDialog" :disabled="!selected.length">
      Delete Perspective
    </v-btn>

    <v-data-table
      v-if="perspectives && perspectives.length"
      :headers="headers"
      :items="perspectives"
      item-value="id"
      show-select
      v-model="selected"
      class="mt-4"
    >
      <template #top>
        <v-toolbar flat>
          <v-toolbar-title>Perspetivas</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
      </template>
    </v-data-table>

    <div v-else class="mt-4">
      <p>No perspective has been found.</p>
    </div>

    <v-alert v-if="error" type="error" dismissible class="mt-4">
      {{ error }}
    </v-alert>

    <!-- Diálogo de confirmação -->
    <v-dialog v-model="confirmDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Confirmação</v-card-title>
        <v-card-text>
          Are you sure you want to delete the selected perspective?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="confirmDialog = false">
            Cancel
          </v-btn>
          <v-btn text color="error" @click="deleteSelectedConfirmed">
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      projectId: null,
      perspectives: [],
      selected: [], // Perspectivas selecionadas
      confirmDialog: false, // Controla a visibilidade do diálogo
      headers: [
        { text: "Name", value: "name" },
        { text: "Created By", value: "created_by" },
        { text: "Description", value: "description", sortable: false },
      ],
      error: null,
    };
  },
  async mounted() {
    this.projectId = this.$route.params.id;
    if (!this.projectId) {
      this.error = "Project ID not found";
      return;
    }
    await this.fetchPerspectives();
  },
  methods: {
    async fetchPerspectives() {
      console.log(">>> Chamando getPerspectives com projectId:", this.projectId);
      try {
        this.error = null;
        const response = await this.$repositories.perspective.getPerspectives(this.projectId);
        console.log(">>> Dados recebidos:", response);
        this.perspectives = response.results;
      } catch (error) {
        console.error("Erro ao carregar perspetivas:", error);
        this.error = "Erro ao carregar perspetivas. Veja o console para mais detalhes.";
      }
    },
    openConfirmDialog() {
      this.confirmDialog = true;
    },
    async deleteSelectedConfirmed() {
      try {
        // Chama a função de deleção para cada perspectiva selecionada
        for (const item of this.selected) {
          await this.$repositories.perspective.deletePerspective(this.projectId, item.id);
        }
        // Atualiza a lista removendo os itens deletados
        this.perspectives = this.perspectives.filter(
          (item) => !this.selected.some((sel) => sel.id === item.id)
        );
        // Limpa a seleção e fecha o diálogo
        this.selected = [];
        this.confirmDialog = false;
      } catch (error) {
        console.error("Erro ao excluir perspetiva(s):", error);
        this.error = "Erro ao excluir perspetiva(s). Veja o console para mais detalhes.";
        this.confirmDialog = false;
      }
    },
  },
};
</script>
