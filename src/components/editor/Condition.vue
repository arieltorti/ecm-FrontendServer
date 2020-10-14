<template>
  <div>
    <label :for="comp"> <span v-katex="comp.initLatex"></span>: </label>
    <input
      v-model.number="simulation.initial_conditions[comp.name]"
      type="number"
      step="any"
    />
  </div>
</template>
<script>
export default {
  props: ["comp", "simulation"],
};
</script>
