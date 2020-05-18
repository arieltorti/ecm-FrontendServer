<template>
  <fieldset v-if="modelSelected">
    <legend>Model Details</legend>
    <h3>Reactions</h3>
    <div v-for="reaction in currentModel.reactions" :key="reaction.name" class="reaction">
      <div>{{reaction.sfrom}} -> {{reaction.sto}}: {{ reaction.function }}</div>
    </div>
    <div v-if="currentModel.expressions">
      <h3>Where</h3>
      <div v-for="expr in currentModel.expressions" :key="expr.name" class="expression">
        <div>{{expr.name}} = {{ expr.value }}</div>
      </div>
    </div>
  </fieldset>
</template>
<script>
export default {
  props: ["currentModel", "modelSelected"]
};
</script>