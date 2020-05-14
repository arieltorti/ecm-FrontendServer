<template>
  <div>
    <label for="iter-var">Iterate var:</label>
    <select name="iterating-var" v-model="currentIterVar">
      <option :value="null">None</option>
      <option
        v-for="variable in modelVariables"
        :value="variable"
        :key="variable"
        >{{ variable }}</option
      >
    </select>

    <IterationControls
      v-if="currentIterVar"
      :from.sync="fromInput"
      :to.sync="toInput"
      :step.sync="stepInput"
    />
  </div>
</template>

<script lang="ts">
import {
  Emit,
  Watch,
  Component,
  Prop,
  PropSync,
  Vue
} from "vue-property-decorator";
import IterationControls from "./IterationControls.vue";

@Component({
  components: {
    IterationControls
  }
})
export default class SimulationControls extends Vue {
  @Prop() modelVariables!: string[];
  @PropSync("iterVar") currentIterVar!: string;
  @PropSync("from") fromInput!: number;
  @PropSync("to") toInput!: number;
  @PropSync("step") stepInput!: number;
}
</script>

<style lang="scss" scoped></style>
