<template>
  <div>
    <strong>
      <span v-katex="param.nameLatex"></span>:
    </strong>
    <div v-if="param.iterable">
      <label for="param">with range:</label>
      <input
        type="radio"
        v-model="simulation.iterate.key"
        id="param"
        :value="param.name"
        @click="paramUncheck(param.name)"
      />
    </div>
    <div v-if="simulation.iterate.key == param.name">
      <label :for="param + 'Start'">Start:</label>
      <input v-model.number="simulation.iterate.start" :id="param + 'Start'" type="number" />
      <label :for="param + 'End'">End:</label>
      <input v-model.number="simulation.iterate.end" :id="param + 'End'" type="number" />
      <label :for="param + 'Intervals'">Intervals:</label>
      <input v-model.number="simulation.iterate.intervals" :id="param + 'Intervals'" type="number" />
    </div>
    <div v-else>
      <label :for="param">Value:</label>
      <input v-model.number="simulation.params[param.name]" type="number" :id="param" />
    </div>
  </div>
</template>
<script>
export default {
  props: ["param", "simulation"],
  methods: {
    paramUncheck: function(val) {
      if (this.simulation.iterate.key == val) {
        this.simulation.iterate.key = null;
      }
    }
  }
};
</script>