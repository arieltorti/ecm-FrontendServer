<template>
  <div class="group" v-if="group.compartments.length > 0">
    <span>{{ group.name }}</span>
    <Condition
      v-for="comp in group.compartments"
      :key="comp.name"
      :comp="comp"
      :simulation="simulation"
    />
  </div>
</template>
<script>
import Condition from "./Condition.vue";

export default {
  components: { Condition },
  props: ["group", "simulation"],
};
</script>

<style lang="sass" scoped>
.group
    display: flex
    flex-wrap: wrap
    justify-content: center
    margin: 1em 0
    padding: .8em

    span
        flex-basis: 100%
        text-align: center
        margin: .3em 0 .8em 0
</style>
