<template>
  <v-container>
    <v-alert
      v-if="error"
      type="error"
      dismissible
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-form ref="form" v-model="valid" @submit.prevent="submitForm">
      <v-text-field
        v-model="form.name"
        label="Nome da perspetiva"
        :rules="[rules.required]"
        required
      ></v-text-field>

      <v-select
        v-model="form.data_type"
        :items="dataTypes"
        label="Tipo de Dado"
        :rules="[rules.required]"
        required
      ></v-select>

      <v-btn type="submit" :disabled="!valid" color="primary">Criar Perspetiva</v-btn>
    </v-form>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      valid: false,
      error: null,
      form: {
        name: "",
        data_type: "",
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

        // Chamada ao repositório para criar a perspetiva
        await this.$repositories.perspective.createPerspective(
          this.$route.params.id,
          this.form
        );

        // Redirecionar após a criação
        this.$router.push(`/projects/${this.$route.params.id}/perspectives`);
      } catch (error) {
        console.error("Erro ao criar perspetiva:", error);
        this.error = "Erro ao criar perspetiva. Veja o console para mais detalhes.";
      }
    },
  },
};
</script>