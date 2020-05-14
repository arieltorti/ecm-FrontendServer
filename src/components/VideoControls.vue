<template>
  <div>
    <!-- <label for="recordWhenDone">Record when done: </label> -->
    <!-- <input type="checkbox" name="recordWhenDone" v-model="autoRecord" /> -->

    <div v-if="simState > SIM_STATE.IDLE">
      <label for="">Video duration (in seconds):</label>
      <input type="number" min="1" v-model.number="videoDurationInput" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, PropSync, Prop } from "vue-property-decorator";
import { SIM_STATE } from "../components/Simulation.vue";

@Component({})
export default class SimulationControls extends Vue {
  @Prop() simState!: number;
  @PropSync("recordWhenDone") autoRecord!: boolean;
  @PropSync("videoDuration") videoDurationInput!: number;

  private SIM_STATE = SIM_STATE;
}
</script>

<style lang="scss" scoped></style>
