<template>
  <v-row>
    <v-col cols="12">
      <member-progress />
    </v-col>
    <v-col v-if="!!project.canDefineCategory" cols="12">
      <label-distribution
        title="Category Distribution"
        :distribution="categoryDistribution"
        :label-types="categoryTypes"
      />
    </v-col>
    <v-col v-if="!!project.canDefineSpan" cols="12">
      <label-distribution
        title="Span Distribution"
        :distribution="spanDistribution"
        :label-types="spanTypes"
      />
    </v-col>
    <v-col v-if="!!project.canDefineRelation" cols="12">
      <label-distribution
        title="Relation Distribution"
        :distribution="relationDistribution"
        :label-types="relationTypes"
      />
    </v-col>
    <v-col cols="12">
      <member-label-choices :member-choices="memberChoices" />
    </v-col>
  </v-row>
</template>

<script>
import { mapGetters } from 'vuex'
import LabelDistribution from '~/components/metrics/LabelDistribution'
import MemberProgress from '~/components/metrics/MemberProgress'
import MemberLabelChoices from '~/components/discrepancies/MemberLabelChoices'

export default {
  components: {
    LabelDistribution,
    MemberProgress,
    MemberLabelChoices
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject', 'isProjectAdmin'],

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      categoryTypes: [],
      categoryDistribution: {},
      relationTypes: [],
      relationDistribution: {},
      spanTypes: [],
      spanDistribution: {},
      memberChoices: {}
    }
  },

  computed: {
    ...mapGetters('projects', ['project']),

    projectId() {
      return this.$route.params.id
    }
  },

  async created() {
    if (this.project.canDefineCategory) {
      this.categoryTypes = await this.$services.categoryType.list(this.projectId)
      this.categoryDistribution = await this.$repositories.discrepancies.fetchCategoryDistribution(
        this.projectId
      )
    }
    if (this.project.canDefineSpan) {
      this.spanTypes = await this.$services.spanType.list(this.projectId)
      this.spanDistribution = await this.$repositories.discrepancies.fetchSpanDistribution(this.projectId)
    }
    if (this.project.canDefineRelation) {
      this.relationTypes = await this.$services.relationType.list(this.projectId)
      this.relationDistribution = await this.$repositories.discrepancies.fetchRelationDistribution(
        this.projectId
      )
    }
    this.memberChoices = await this.$repositories.discrepancies.fetchMemberLabelChoices(this.projectId)
  }
}
</script>
