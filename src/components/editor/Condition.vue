<template>
  <div>
    <label :for="comp"><h4>{{ comp.name }}_0:</h4></label>
    <input v-model.number="simulation.initial_conditions[comp.name]" type="number" />
  </div>
</template>
<script>
export default {
    props: ["comp", "simulation"]
}
</script>