<template>
  <fieldset>
    <legend>Simulation parameters</legend>
    <details>
      <summary>General</summary>
      <label for="days">Days:</label>
      <input
        name="days"
        v-model.number="simulation.days"
        type="number"
        step="any"
      />

      <label for="step">Step:</label>
      <input
        name="step"
        v-model.number="simulation.step"
        type="number"
        step="any"
      />
    </details>
    <details>
      <summary>Initial conditions</summary>
      <ConditionGroup :group="model.ungrouped" :simulation="simulation" />
      <ConditionGroup
        v-for="group in model.groups"
        :key="group.name"
        :group="group"
        :simulation="simulation"
      />
    </details>
    <details>
      <summary>Params</summary>
      <ParamGroup :group="model.ungrouped" :simulation="simulation" />
      <ParamGroup
        v-for="group in model.groups"
        :key="group.name"
        :group="group"
        :simulation="simulation"
      />
    </details>
  </fieldset>
</template>
<script>
import ParamGroup from "./editor/ParamGroup.vue";
import ConditionGroup from "./editor/ConditionGroup.vue";

export default {
  props: ["model", "simulation"],
  components: { ParamGroup, ConditionGroup },
};
</script>
