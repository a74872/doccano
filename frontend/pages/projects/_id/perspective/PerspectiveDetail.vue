<template>
  <v-container>
    <v-card v-if="perspective">
      <v-card-title class="headline">Perspective Details</v-card-title>
      <v-card-text>
        <v-simple-table>
          <template v-slot:default>
            <tbody>
              <tr>
                <td><strong>Name</strong></td>
                <td>{{ perspective.name }}</td>
              </tr>
              <tr>
                <td><strong>Data Type</strong></td>
                <td>{{ perspective.data_type }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette</strong></td>
                <td>{{ perspective.description }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 1</strong></td>
                <td>{{ perspective.description_1 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 2</strong></td>
                <td>{{ perspective.description_2 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 3</strong></td>
                <td>{{ perspective.description_3 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 4</strong></td>
                <td>{{ perspective.description_4 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 5</strong></td>
                <td>{{ perspective.description_5 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 6</strong></td>
                <td>{{ perspective.description_6 }}</td>
              </tr>
              <tr>
                <td><strong>Etiquette 7</strong></td>
                <td>{{ perspective.description_7 }}</td>
              </tr>
              <tr>
                <td><strong>Created By</strong></td>
                <td>{{ perspective.created_by }}</td>
              </tr>
              <tr>
                <td><strong>Created At</strong></td>
                <td>{{ perspective.created_at }}</td>
              </tr>
              <tr>
                <td><strong>Project ID</strong></td>
                <td>{{ perspective.project_id }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="$router.go(-1)">Back</v-btn>
      </v-card-actions>
    </v-card>
    <v-alert v-else type="error">{{ error || "Perspective not found." }}</v-alert>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      projectId: null,
      perspectiveId: null,
      perspective: null,
      error: null,
    };
  },
  async mounted() {
    this.projectId = this.$route.params.id;
    this.perspectiveId = this.$route.params.perspectiveId;

    if (!this.projectId || !this.perspectiveId) {
      this.error = "Missing Project or Perspective ID.";
      return;
    }

    await this.fetchPerspectiveDetails();
  },
  methods: {
    async fetchPerspectiveDetails() {
      try {
        this.error = null;
        this.perspective = await this.$repositories.perspective.getPerspectiveDetails(
          this.projectId,
          this.perspectiveId
        );
      } catch (error) {
        console.error("Error fetching perspective details:", error);
        this.error = "Error fetching perspective details.";
      }
    },
  },
};
</script>
