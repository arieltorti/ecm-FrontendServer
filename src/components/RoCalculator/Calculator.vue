<template>
  <div class="container">
    <details>
      <summary>Ro Calculator</summary>

      <span>Enter number of individuals and contact rates:</span>

      <div class="section">
        <label for="p">p:</label>
        <input
          name="p"
          type="number"
          step="any"
          v-model.number="variables.p"
          @change="calculateRo"
        />

        <label for="gamma">Gamma:</label>
        <input
          name="gamma"
          type="number"
          step="any"
          v-model.number="variables.gamma"
          @change="calculateRo"
        />

        <label for="s" title="Number of susceptibles">S:</label>
        <input
          name="s"
          type="number"
          step="any"
          v-model.number="variables.s"
          @change="calculateRo"
        />
      </div>

      <div class="section">
        <table>
          <tbody>
            <tr>
              <th>Group</th>
              <th>Nc</th>
              <th
                v-for="n in numberContagionRates"
                :title="'Contact rate ' + n"
                :key="n"
              >
                c{{ n }}
              </th>
              <th>c</th>
              <th>Nc * c</th>
            </tr>

            <tr v-for="(group, idx) in tableData" :key="idx">
              <td>{{ idx + 1 }}</td>
              <td>
                <input
                  class="normal"
                  type="number"
                  step="any"
                  :value="group.n"
                  @change="(ev) => handlePopulationChange(idx, ev)"
                  v-on:paste="(ev) => handlePaste(idx, -1, ev)"
                />
              </td>
              <td v-for="(c, c_idx) in group.contagionRates" :key="c_idx">
                <input
                  class="small"
                  type="number"
                  step="any"
                  :value="c"
                  @change="(ev) => handleContagionChange(idx, c_idx, ev)"
                  v-on:paste="(ev) => handlePaste(idx, c_idx, ev)"
                />
              </td>
              <td>{{ group.totalContagion }}</td>
              <td>{{ group.product | toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <Results :results="results" />
      </div>
    </details>
  </div>
</template>
<script>
const NUMBER_GROUPS = 10;
const NUMBER_CONTAGION_RATES = 6;

import Results from "./Results";
import { preciseRound } from "../../utils";

function initialTableData(groups, contagionRates) {
  // eslint-disable-next-line no-unused-vars
  return new Array(groups).fill().map((_) => ({
    n: 0,
    contagionRates: new Array(contagionRates).fill(0),
    totalContagion: 0,
    product: 0,
  }));
}

export default {
  components: { Results },
  data: function () {
    return {
      numberGroups: NUMBER_GROUPS,
      numberContagionRates: NUMBER_CONTAGION_RATES,

      tableData: initialTableData(NUMBER_GROUPS, NUMBER_CONTAGION_RATES),

      variables: {
        p: 0,
        gamma: 0,
        s: 0,
      },

      results: {
        N: 0,
        c_mean: 0,
        Ro: "-",
        Rt: "-",
      },
    };
  },
  created: function () {
    this.loadValues();
  },
  filters: {
    toFixed(value, decimals) {
      return value.toFixed(decimals);
    },
  },
  methods: {
    handlePopulationChange(g_idx, ev) {
      const value = ev.target.value && Number(ev.target.value);
      const group = this.tableData[g_idx];

      group.n = value;
      group.product = group.totalContagion * group.n;

      this.calculateRo();
    },
    handleContagionChange(g_idx, c_idx, ev) {
      const value = ev.target.value && Number(ev.target.value);
      const group = this.tableData[g_idx];

      group.contagionRates[c_idx] = value;
      group.totalContagion = group.contagionRates.reduce((x, y) => x + y, 0);
      group.product = group.totalContagion * group.n;

      this.calculateRo();
    },
    handlePaste(g_idx, c_idx = -1, ev) {
      ev.preventDefault();

      let paste = (ev.clipboardData || window.clipboardData).getData("text");
      const pasteFields = paste.trim().split(/\s/);

      let group = this.tableData[g_idx];

      for (let i = 0; i < pasteFields.length; i++) {
        const value = parseInt(pasteFields[i], 10);

        if (c_idx === -1) {
          group.n = value;
        } else {
          group.contagionRates[c_idx] = value;
        }
        c_idx += 1;

        if (c_idx >= this.numberContagionRates) {
          this.handleContagionChange(g_idx, c_idx - 1, {
            target: { value: group.contagionRates[c_idx - 1] },
          });
          c_idx = -1;
          g_idx += 1;
          group = this.tableData[g_idx];
        }
      }
      this.handleContagionChange(g_idx, c_idx - 1, {
        target: { value: group.contagionRates[c_idx - 1] },
      });
    },

    calculateRo() {
      let N = 0;
      let c_mean = 0;

      Object.values(this.tableData).forEach((value) => {
        N += value.n;
        c_mean += value.product;
      });

      c_mean /= N;

      this.results.N = preciseRound(N, 4);
      this.results.c_mean = preciseRound(c_mean, 4);

      this.results.Ro = preciseRound(
        (this.variables.p / this.variables.gamma) * c_mean,
        4
      );
      this.results.Rt = preciseRound(
        (this.results.Ro * this.variables.s) / N,
        4
      );

      this.storeValues();
    },

    /** Stores all the calculation data in the local storage */
    storeValues() {
      const RoCalculationData = {
        variables: this.variables,
        tableData: this.tableData,
      };

      if (typeof window.localStorage !== "undefined") {
        window.localStorage.setItem(
          "RoCalculationData",
          btoa(JSON.stringify(RoCalculationData))
        );
      }
    },
    loadValues() {
      if (typeof window.localStorage !== "undefined") {
        const RawRoCalculationData = window.localStorage.getItem(
          "RoCalculationData"
        );

        if (RawRoCalculationData !== undefined) {
          const RoCalculationData = JSON.parse(atob(RawRoCalculationData));

          this.variables = RoCalculationData.variables;
          this.tableData = RoCalculationData.tableData;
        }
        this.calculateRo();
      }
    },
  },
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

.section
  margin-bottom: 2em
</style>
