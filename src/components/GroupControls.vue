<template>
  <div class="group-container">
    <div v-for="(group, idx) in this.model.groups" :key="group.name" class="group">
      <label :for="group.name">{{ group.name }} </label>
      <input
        type="checkbox"
        :id="group.name"
        :checked="group.visible"
        @click="$emit('changeGroupVisibility', idx, $event.target.checked)"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: ["model"],
};
</script>

<style lang="sass" scoped>
.group-container
    display: block

    .group
        display: inline-block
        margin: .3em .8em
</style>
