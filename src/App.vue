<template>
  <div id="app">
    <Editor :model.sync="modelInput" :config.sync="configInput" />
    <Simulation
      :modelVariables="modelVariables"
      :model="modelInput"
      :config="configInput"
    />
  </div>
</template>

<script lang="ts">
import "reflect-metadata";
import { Watch, Component, Vue } from "vue-property-decorator";
import Editor from "./components/Editor.vue";
import Simulation from "./components/Simulation.vue";

import { extractModelVariables } from "./utils/variable-extractor";

const defaultSimulationModel = `; simplemodel

(import (rnrs) (emodl cmslib))

(start-model "seir.emodl")

(species S 990)
(species E)
(species I 10)
(species R)

(observe susceptible S)
(observe exposed     E)
(observe infectious  I)
(observe recovered   R)

(param Ki 0.0005)
(param Kl 0.2)
(param Kr (/ 1 7))

(reaction exposure   (S I) (E I) (* Ki S I))
(reaction infection  (E)   (I)   (* Kl E))
(reaction recovery   (I)   (R)   (* Kr I))

(end-model)`;

const defaultConfigText = `{
    "duration" : 365,
    "runs" : 1,
    "samples" : 365,
    "solver" : "R",
    "output" : {
        "headers" : true
    },
    "tau-leaping" : {
        "epsilon" : 0.01
    },
    "r-leaping" : {}
}`;

const SIMULATION_MODEL_KEY = "simulationModel";
const SIMULATION_CONFIG_KEY = "simulationConfig";

@Component({
  components: {
    Editor,
    Simulation
  }
})
export default class App extends Vue {
  private modelInput: string =
    localStorage.getItem(SIMULATION_MODEL_KEY) || defaultSimulationModel;
  private configInput: string =
    localStorage.getItem(SIMULATION_CONFIG_KEY) || defaultConfigText;

  private modelVariables: string[] = [];

  created() {
    this.modelVariables = extractModelVariables(this.modelInput);
  }

  @Watch("modelInput")
  onModelChange(val: string, oldVal: string) {
    localStorage.setItem(SIMULATION_MODEL_KEY, val);

    this.modelVariables = extractModelVariables(val);
  }

  @Watch("configInput")
  onConfigChange(val: string, oldVal: string) {
    localStorage.setItem(SIMULATION_CONFIG_KEY, val);
  }
}
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

* {
  box-sizing: border-box;
}
</style>
