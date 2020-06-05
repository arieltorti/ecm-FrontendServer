<template>
  <div class="group" v-if="group.params.length > 0">
    <span>{{ group.name }}</span>
    <Param
      v-for="param in group.params"
      :key="param.name"
      :param="param"
      :simulation="simulation"
    />
  </div>
</template>
<script>
import Param from "./Param.vue";

export default {
  components: { Param },
  props: ["group", "simulation"],
};
</script>

<style lang="sass" scoped>
.group
    display: flex
    flex-wrap: wrap
    justify-content: center
    align-items: flex-start
    margin: 1em 0
    padding: .8em

    span
        flex-basis: 100%
        text-align: center
        margin: .3em 0 .8em 0
</style>
