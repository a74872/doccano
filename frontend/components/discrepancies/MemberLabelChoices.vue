<template>
  <v-card>
    <v-card-title>Member Label Choices</v-card-title>
    <v-divider />
    <v-card-text>
      <v-expansion-panels>
        <v-expansion-panel v-for="(choices, member) in memberChoices" :key="member">
          <v-expansion-panel-header class="text-capitalize">
            {{ member }}
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-list>
              <v-list-item v-for="(label, dataset) in choices" :key="dataset">
                <v-list-item-content>
                  <v-list-item-title>Dataset: {{ dataset }}</v-list-item-title>
                  <v-list-item-subtitle>Label: {{ label }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { MemberLabelChoices } from '~/domain/models/discrepancies/discrepancies'

export default Vue.extend({
  props: {
    memberChoices: {
      type: Object as () => MemberLabelChoices,
      required: true
    }
  }
})
</script> 