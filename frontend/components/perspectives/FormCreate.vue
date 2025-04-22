<template>
  <v-container>
    <!-- Display any error messages -->
    <v-alert v-if="error" type="error" dismissible class="mb-4">
      {{ error }}
    </v-alert>

    <v-form ref="form" v-model="valid" @submit.prevent="submitForm">
      <!-- Perspective Title -->
      <v-text-field
        v-model="form.name"
        label="Perspective Title"
        :rules="[rules.required]"
        required
      ></v-text-field>

      <!-- Ask how many descriptions (1–7) -->
      <v-select
        v-model="numberOfDescriptions"
        :items="descriptionOptions"
        label="Select how many etiquettes would you like for this perspective?"
        :rules="[rules.required]"
        required
      ></v-select>

      <!-- Always show the first description field (main description) -->
      <v-textarea
        v-model="form.description"
        label="Etiquette number: 1"
        rows="2"
        :rules="[rules.required]"
        required
        class="mt-2"
      ></v-textarea>

      <!-- If the user wants more than one, render additional fields -->
      <div v-if="numberOfDescriptions > 1">
        <v-textarea
          v-for="n in (numberOfDescriptions - 1)"
          :key="n"
          v-model="form['description_' + n]"
          :label="`Etiquette number: ${1+n}`"
          rows="2"
          :rules="[rules.required]"
          required
          class="mb-2"
        ></v-textarea>
      </div>

      <!-- Back to Projects button -->
      <v-btn color="secondary" @click="$router.push('/projects')" class="mr-2 mt-4">
        Back to Projects
      </v-btn>

      <!-- Submit button -->
      <v-btn type="submit" :disabled="!valid || loading" color="primary" class="mt-4">
        Create
      </v-btn>

      <!-- Loading indicator -->
      <v-progress-linear
        v-if="loading"
        indeterminate
        color="primary"
        class="mt-2"
      ></v-progress-linear>
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
      numberOfDescriptions: 1, // Default to 1 description
      descriptionOptions: [1, 2, 3, 4, 5, 6, 7],
      form: {
        name: "",
        description: "",
        // If you previously had data_type, remove or keep as needed
      },
      rules: {
        required: (value) => !!value || "This field is required.",
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        this.error = null;
        this.loading = true;

        // Build the payload. The first description is always "description"
        const payload = {
          name: this.form.name,
          description: this.form.description,
        };

        // If the user wants more than 1 description, add description_1, description_2, etc.
        if (this.numberOfDescriptions > 1) {
          for (let i = 1; i < this.numberOfDescriptions; i++) {
            payload[`description_${i}`] = this.form[`description_${i}`];
          }
        }

        // Call your repository or API with the payload
        await this.$repositories.perspective.createPerspective(
          this.$route.params.id,
          payload
        );

        // Redirect after creation
        this.$router.push(`/projects/${this.$route.params.id}/perspective`);
      } catch (error) {
        console.error("Error creating perspective:", error);
        this.error = "Failed to create perspective. Check console for details.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
