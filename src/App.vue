<template>
  <div>
    <fieldset>
      <legend>Choose a model:</legend>
      <label for="model">Model: </label>
      <select
        style="display: inline-block"
        name="model"
        id="model"
        v-model="modelSelected"
      >
        <option v-for="(model, key) in modelList" :key="key" :value="key">{{
          model.name
        }}</option>
      </select>
    </fieldset>
    <fieldset v-if="modelSelected && currentModel">
      <CurrentModel :currentModel="currentModel" />
    </fieldset>

    <Editor
      v-if="modelSelected && currentModel"
      :model="currentModel"
      :simulation="simulation"
    />

    <fieldset v-if="modelSelected">
      <legend>Simulation</legend>
      <button
        :disabled="simulationState === SIM_STATE.INPROGRESS"
        @click="simulate"
      >
        Simulate
      </button>

      <Simulation
        v-if="currentModel"
        :sim="currentSimulation"
        :sim-cancel="simCancel"
        :sim-state="simulationState"
        @sim-start="handleSimStart"
        @sim-error="handleSimError"
        @sim-done="handleSimDone"
        @sim-cancel="handleSimCancel"
      />
    </fieldset>
    <Authors />
    <span class="license">
      This software is licensed under GPLv3 and can be obtained at
      <a href="https://github.com/maks500/ecm-FrontendServer"
        >ecm-FrontendServer</a
      >
    </span>
  </div>
</template>

<script>
import Authors from "./components/Authors.vue";
import Editor from "./components/Editor.vue";
import Simulation from "./components/Simulation.vue";
import CurrentModel from "./components/CurrentModel.vue";
import { SIM_STATE, SIMULATION_MODEL_KEY } from "./constants.js";

function populateGroups(model) {
  if (model.groups != null) {
    return;
  }
  model.groups = [];
  model.ungrouped = {
    compartments: [],
    params: [],
  };

  const compartmentToGroupMap = {};
  const paramToGroupMap = {};

  if (model.template && model.template.groups && model.template.groups.length) {
    for (const group of model.template.groups) {
      const newGroup = {
        name: group.name,
        visible: group.visible,
        compartments: [],
        params: [],
      };
      model.groups.push(newGroup);

      for (const param of group.parameters) {
        paramToGroupMap[param] = newGroup;
      }

      for (const compartment of group.compartments) {
        compartmentToGroupMap[compartment] = newGroup;
      }
    }
  }

  for (const compartment of model.compartments) {
    const group = compartmentToGroupMap[compartment.name];
    if (group != null) {
      group.compartments.push(compartment);
    } else {
      model.ungrouped.compartments.push(compartment);
    }
  }

  for (const param of model.params) {
    const group = paramToGroupMap[param.name];
    if (group != null) {
      group.params.push(param);
    } else {
      model.ungrouped.params.push(param);
    }
  }
}

function cloneSimulation(simulation) {
  const newSimulation = Object.assign({}, simulation);
  newSimulation.initial_conditions = Object.assign(
    {},
    simulation.initial_conditions
  );
  newSimulation.params = Object.assign({}, simulation.params);
  newSimulation.iterate = Object.assign({}, simulation.iterate);

  return newSimulation;
}

export default {
  beforeMount() {
    this.fetchModels();
  },
  data: function () {
    return {
      SIM_STATE: SIM_STATE, // Declare enum variable so vue can access it on the template

      simulationState: SIM_STATE.NONE,
      errorMsg: null,
      statusMsg: null,
      modelList: {},
      currentModel: null,
      modelSelected: 1,
      simulation: {
        step: 1,
        days: 365,
        initial_conditions: {},
        params: {},
        iterate: { key: null, start: 0, end: 1, intervals: 10 },
      },
      currentSimulation: null,
      simCancel: false,
      pendingChanges: true,
    };
  },
  components: { Simulation, Authors, Editor, CurrentModel },
  computed: {
    modelVariables: function () {
      return Object.keys(this.simulation.params);
    },
  },
  watch: {
    simulationModel: function (val) {
      this.pendingChanges = true;
      localStorage.setItem(SIMULATION_MODEL_KEY, val);
    },
    modelSelected: function (val) {
      this.simulationState = SIM_STATE.NONE;
      const current =
        val in this.modelList
          ? this.modelList[val]
          : { params: [], compartments: [] };
      const simulation = this.simulation;

      current.compartments.forEach((comp) => {
        simulation.initial_conditions[comp.name] = comp.default;
      });
      current.params.forEach((param) => {
        simulation.params[param.name] = param.default;
      });
      this.simulation = simulation;
      this.currentModel = current;
      populateGroups(this.currentModel);
    },
  },

  methods: {
    simulate: function () {
      if (this.simulationState === SIM_STATE.INPROGRESS) {
        this.stopSimulation();
      } else {
        this.buildSimulation();
      }
    },

    fetchModels: function () {
      const req = fetch("/api/models/");
      req.then((resp) => {
        if (resp.status >= 400 && resp.status < 600) {
          throw resp;
        }
        resp.json().then((json) => {
          json.models.forEach((element) => {
            this.modelList[element.id] = element;
          });
          this.modelSelected = 0;
        });
      });
    },
    buildSimulation: function () {
      // Make all objects given to the simulation inmutable, as they're all bound to vue changes.
      this.currentSimulation = {
        model: Object.assign({}, this.currentModel),
        simulation: cloneSimulation(this.simulation),
      };
      setTimeout(() => {
        this.pendingChanges = false;
      }, 0); // Wrap in timeout, otherwise Vue doesn't take this change into account
    },
    stopSimulation: function () {
      this.simCancel = true;
    },
    setError: function (message) {
      this.errorMsg = `[ERROR]: ${message}`;
      this.statusMsg = null;
    },
    setStatus: function (message) {
      this.errorMsg = null;
      this.statusMsg = message;
    },

    handleError: function (error) {
      console.error(error);
      this.setError(error.message);
    },
    handleSubmit: function (values) {
      if (this.simulationState === SIM_STATE.INPROGRESS) {
        this.stopSimulation();
      } else {
        this.buildSimulation(values);
      }
    },
    handleSimStart: function () {
      this.simulationState = SIM_STATE.INPROGRESS;
    },
    handleSimError: function () {
      this.simulationState = SIM_STATE.FAILED;
    },
    handleSimDone: function () {
      this.simulationState = SIM_STATE.DONE;
    },
    handleSimCancel: function () {
      this.simulationState = SIM_STATE.CANCELED;
      this.simCancel = false;
    },
  },
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

.hidden {
  display: none;
}
</style>
