<template>
  <div>
    <label :for="comp"><strong>{{ comp.name }}_0:</strong></label>
    <input v-model.number="simulation.initial_conditions[comp.name]" type="number" />
  </div>
</template>
<script>
export default {
    props: ["comp", "simulation"]
}
</script>