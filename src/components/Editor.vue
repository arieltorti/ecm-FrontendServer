<template>
  <div class="container">
    <div class="input-container model">
      <label for="modelInput">Simulation Model: </label>
      <textarea name="modelInput" v-model="modelInput"></textarea>
    </div>

    <div class="input-container config">
      <label for="configInput">Configuration: </label>
      <textarea name="configInput" v-model="configInput"></textarea>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, PropSync, Vue } from "vue-property-decorator";

@Component
export default class Editor extends Vue {
  @PropSync("model") modelInput!: string;
  @PropSync("config") configInput!: string;
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.container {
  display: flex;
  width: 100%;

  .input-container {
    margin: 1em;
    width: 100%;
    height: 400px;
    display: flex;
    flex-direction: column;

    &.config {
      flex-basis: 400px;
    }

    &.model {
      flex: 1;
    }

    textarea {
      flex: 1;
    }
  }
}
</style>
