<template>
  <fieldset>
    <legend>Simulation parameters</legend>
    <details>
      <summary>General</summary>
      <label for="days">Days:</label>
      <input name="days" v-model.number="simulation.days" type="number" />

      <label for="step">Step:</label>
      <input name="step" v-model.number="simulation.step" type="number" />
    </details>
    <details>
      <summary>Initial conditions</summary>
      <Condition
        v-for="comp in model.compartments"
        :key="comp.name"
        :comp="comp"
        :simulation="simulation"
      />
    </details>
    <details>
      <summary>Params</summary>
      <Param
        v-for="param in model.params"
        :key="param.name"
        :param="param"
        :simulation="simulation"
      />
    </details>
  </fieldset>
</template>
<script>
import Param from "./editor/Param.vue";
import Condition from "./editor/Condition.vue";
export default {
  props: ["model", "simulation"],
  components: { Param, Condition }
};
</script>