<template>
  <div id="app" v-cloak>
    <fieldset>
      <legend>Choose a model:</legend>
      <select name="model" id="model" v-model="modelSelected" @change="modelChange($event)">
        <option
          v-for="(model, key) in modelList"
          :key="key"
          :value="key"
          :selected="modelSelected == key"
        >{{ model.name }}</option>
      </select>
    </fieldset>
    <CurrentModel :modelSelected="modelSelected" :currentModel="currentModel" />

    <fieldset v-if="modelSelected">
      <legend>Simulation parameters</legend>
      <details>
        <summary>General</summary>
        <label for="days">Days:</label>
        <input name="days" v-model.number="simulation.days" type="number" />

        <label for="step">Step:</label>
        <input name="step" v-model.number="simulation.step" type="number" />
      </details>
      <details>
        <summary>Initial conditions</summary>
        <Condition
          v-for="comp in currentModel.compartments"
          :key="comp.name"
          :comp="comp"
          :simulation="simulation"
        />
      </details>
      <details v-if="modelSelected">
        <summary>Params</summary>
        <Param
          v-for="param in currentModel.params"
          :key="param.name"
          :param="param"
          :simulation="simulation"
        />
      </details>
    </fieldset>

    <fieldset v-if="modelSelected">
      <legend>Simulation</legend>
      <button
        style="margin: 1em; padding: 0.4em 0.8em; font-size: 1.15em;"
        @click="simulate"
      >Simulate</button>

      <Simulation
        :sim="currentSimulation"
        :sim-cancel="simCancel"
        :sim-state="simulationState"
        @sim-start="handleSimStart"
        @sim-error="handleSimError"
        @sim-done="handleSimDone"
        @sim-cancel="handleSimCancel"
      />
    </fieldset>
  </div>
</template>

<script>
import Simulation from "./components/Simulation.vue";
import Param from "./components/Param.vue";
import Condition from "./components/Condition.vue";
import CurrentModel from "./components/CurrentModel.vue";

import { SIM_STATE, SIMULATION_MODEL_KEY } from "./constants.js";
export default {
  beforeMount() {
    this.fetchModels();
  },
  data: function() {
    return {
      SIM_STATE: SIM_STATE, // Declare enum variable so vue can access it on the template

      simulationState: SIM_STATE.DONE,
      errorMsg: null,
      statusMsg: null,
      modelList: {},
      modelSelected: 1,
      simulation: {
        step: 1,
        days: 365,
        initial_conditions: {},
        params: {},
        iterate: { key: null, start: 0, end: 1, intervals: 10 }
      },
      currentSimulation: null,
      simCancel: false,
      pendingChanges: true
    };
  },
  components: { Simulation, Param, Condition, CurrentModel },
  computed: {
    currentModel: function() {
      const models = this.modelList;
      const selected = this.modelSelected;
      return selected in models
        ? models[selected]
        : { params: [], compartments: [] };
    },
    modelVariables: function() {
      return Object.keys(this.simulation.params);
    }
  },
  watch: {
    simulationModel: function(val) {
      this.pendingChanges = true;
      localStorage.setItem(SIMULATION_MODEL_KEY, val);
    }
  },

  methods: {
    simulate: function() {
      if (this.simulationState === SIM_STATE.INPROGRESS) {
        this.stopSimulation();
      } else {
        this.buildSimulation();
      }
    },
    paramUncheck: function(param) {
      if (this.simulation.iterate.key == param) {
        this.simulation.iterate.key = null;
      }
    },
    modelChange: function() {
      this.simulation.initial_conditions = {};
      this.simulation.params = {};
      this.currentModel.compartments.forEach(comp => {
        this.simulation.initial_conditions[comp.name] = comp.default;
      });
      this.currentModel.params.forEach(param => {
        this.simulation.params[param.name] = param.default;
      });
    },
    fetchModels: function() {
      const req = fetch("/api/models/");
      req.then(resp => {
        if (resp.status >= 400 && resp.status < 600) {
          throw resp;
        }
        resp.json().then(json => {
          json.models.forEach(element => {
            this.modelList[element.id] = element;
          });
          this.modelSelected = 0;
        });
      });
    },
    buildSimulation: function() {
      // Make all objects given to the simulation inmutable, as they're all bound to vue changes.
      this.currentSimulation = {
        model: this.currentModel,
        simulation: this.simulation
      };
      setTimeout(() => {
        this.pendingChanges = false;
      }, 0); // Wrap in timeout, otherwise Vue doesn't take this change into account
    },
    stopSimulation: function() {
      this.simCancel = true;
    },
    setError: function(message) {
      this.errorMsg = `[ERROR]: ${message}`;
      this.statusMsg = null;
    },
    setStatus: function(message) {
      this.errorMsg = null;
      this.statusMsg = message;
    },

    handleError: function(error) {
      console.error(error);
      this.setError(error.message);
    },
    handleSubmit: function(values) {
      if (this.simulationState === SIM_STATE.INPROGRESS) {
        this.stopSimulation();
      } else {
        this.buildSimulation(values);
      }
    },
    handleSimStart: function() {
      this.simulationState = SIM_STATE.INPROGRESS;
    },
    handleSimError: function() {
      this.simulationState = SIM_STATE.FAILED;
    },
    handleSimDone: function() {
      this.simulationState = SIM_STATE.DONE;
    },
    handleSimCancel: function() {
      this.simulationState = SIM_STATE.CANCELED;
      this.simCancel = false;
    }
  }
};
</script>
<style lang="css">
@import url("https://cdn.jsdelivr.net/gh/kognise/water.css@latest/dist/light.min.css");
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
#container {
  display: flex;
  width: 100%;
  box-sizing: border-box;
}

#container .inputContainer {
  margin: 1em;
  width: 100%;
  box-sizing: border-box;
  height: 400px;
  display: flex;
  flex-direction: column;
}

#container .inputContainer label {
  display: block;
}

#container .inputContainer textarea {
  width: 100%;
  flex: 1;
}

#errorMsg {
  color: red;
  display: block;
}

.variable-selector div.option {
  display: inline-block;
  margin: 0 0.8em;
}

#plotAnimDiv {
  /* This is a hack, TODO: look on plotly doc is there's a way to insert a DOM element as button for a better way to position this */
  position: absolute;
  bottom: 36px;
  left: 120px;
}

#plotAnimDiv button {
  padding: 0.6em 0.8em;
}

.slider-grip-rect {
  fill: #ff4242 !important;
}

/* Prevents the flash of unitialized vue instance */
[v-cloak] {
  display: none;
}

.interval-config label {
  display: inline-block !important;
  width: 4em;
  text-align: right;
}

.interval-config input {
  display: inline-block !important;
  width: 6em;
}
</style>
