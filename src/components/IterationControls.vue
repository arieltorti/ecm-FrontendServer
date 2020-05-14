<template>
  <div class="interval-config">
    <label for="from">From: </label>
    <input
      type="number"
      name="from"
      step="0.000001"
      v-model.number="fromInput"
    />

    <label for="to">To: </label>
    <input type="number" name="to" step="0.000001" v-model.number="toInput" />

    <label for="step">Step: </label>
    <input
      type="number"
      name="step"
      step="0.000001"
      min="0.000001"
      v-model.number="stepInput"
    />
  </div>
</template>

<script lang="ts">
import { Component, PropSync, Vue } from "vue-property-decorator";

@Component({})
export default class IterationControls extends Vue {
  @PropSync("from") fromInput!: number;
  @PropSync("to") toInput!: number;
  @PropSync("step") stepInput!: number;
}
</script>

<style lang="scss" scoped></style>
