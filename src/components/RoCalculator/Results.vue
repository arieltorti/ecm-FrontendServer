<template>
  <table>
    <tbody>
      <tr>
        <td :colspan="Object.keys(results).length">Results</td>
      </tr>

      <tr>
        <th>N</th>
        <th>c (mean)</th>
        <th>Ro</th>
        <th>Rt</th>
      </tr>
      <tr>
        <td>{{ results.N }}</td>
        <td>{{ results.c_mean }}</td>
        <td>{{ results.Ro }}</td>
        <td>{{ results.Rt }}</td>
      </tr>
    </tbody>
  </table>
</template>
<script>
export default {
  props: ["results"],
};
</script>

<style lang="sass" scoped>
table
    input
        border: 1px solid black

        &.small
            width: 2em
        &.normal
            width: 6em

    th,
    td
        text-align: center
</style>
