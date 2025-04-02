<template>
  <v-container>
    <v-alert v-if="error" type="error" dismissible class="mb-4">
      {{ error }}
    </v-alert>

    <v-form ref="form" v-model="valid" @submit.prevent="submitForm">
      <!-- Campo para o título/pergunta da perspectiva -->
      <v-text-field
        v-model="form.name"
        label="Pergunta da Perspetiva"
        :rules="[rules.required]"
        required
      ></v-text-field>

      <!-- Campo para o tipo de dado -->
      <v-select
        v-model="form.data_type"
        :items="dataTypes"
        label="Tipo de Dado"
        :rules="[rules.required]"
        required
      ></v-select>

      <!-- Campo para a descrição -->
      <v-textarea
        v-model="form.description"
        label="Descrição da Perspetiva"
        rows="3"
        :rules="[rules.required]"
        required
      ></v-textarea>

      <v-btn type="submit" :disabled="!valid || loading" color="primary">
        Criar Perspetiva
      </v-btn>

      <!-- Botão para voltar diretamente para /projects -->
      <v-btn color="secondary" @click="$router.push('/projects')" class="ml-2">
        Voltar
      </v-btn>

      <v-progress-linear v-if="loading" indeterminate color="primary" class="mt-2"></v-progress-linear>
    </v-form>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      valid: false,
      loading: false,
      error: null,
      form: {
        name: "",
        data_type: "",
        description: "",
      },
      dataTypes: [
        { text: "String", value: "string" },
        { text: "Integer", value: "integer" },
        { text: "Float", value: "float" },
        { text: "Boolean", value: "boolean" },
      ],
      rules: {
        required: (value) => !!value || "Este campo é obrigatório.",
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        this.error = null;
        this.loading = true;

        await this.$repositories.perspective.createPerspective(
          this.$route.params.id,
          this.form
        );

        this.$router.push(`/projects/${this.$route.params.id}/perspective`);
      } catch (error) {
        console.error("Erro ao criar perspetiva:", error);
        this.error = "Erro ao criar perspetiva. Veja o console para mais detalhes.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
