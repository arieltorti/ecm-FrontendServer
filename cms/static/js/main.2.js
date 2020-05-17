"use strict";

function getConfigInterval() {
  const storedConfig = localStorage.getItem(SIMULATION_ITER_CONFIG_KEY);
  if (storedConfig != null) {
    return JSON.parse(storedConfig);
  }
  return defaultIterConfig;
}

const app = new Vue({
  el: "#app",
  beforeMount(){
    this.fetchModels();
  },
  data: function () {
    return {
      SIM_STATE: SIM_STATE, // Declare enum variable so vue can access it on the template

      simulationState: SIM_STATE.DONE,
      errorMsg: null,
      statusMsg: null,
      modelList: {},
      modelSelected: null,
      simulation : {
        step : 1,
        days : 365,
        initial_conditions : {},
        params : {},
        iterate : {key : null, start: 0, end: 1, intervals: 10},
      },
      configInterval: getConfigInterval(),
      currentSimulation: null,
      simCancel: false,
      pendingChanges: true,
    };
  },
  computed: {
    currentModel: function () {
      return (this.modelSelected in this.modelList) ? 
        this.modelList[this.modelSelected] : { params: [], compartments: []};
    },
    modelVariables: function () {
      return Object.keys(this.simulation.params);
    },
  },
  watch: {
    configInterval: {
      handler(val) {
        this.pendingChanges = true;
        localStorage.setItem(SIMULATION_ITER_CONFIG_KEY, JSON.stringify(val));
      },
      deep: true,
    },
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
    modelChange: function($event) {
      this.simulation.initial_conditions = {};
      this.simulation.params = {};
      this.currentModel.compartments.forEach(comp => {
        this.simulation.initial_conditions[comp.name] = comp.default;
      });
      this.currentModel.params.forEach(param => {
        this.simulation.params[param.name] = param.default;
      });      
    },
    fetchModels: function () {
      const req = fetch("/api/models/").then(resp => {
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
    buildSimulation: function () {

      // Make all objects given to the simulation inmutable, as they're all bound to vue changes.
      this.currentSimulation = {
        model: this.currentModel,
        simulation: this.simulation
      };
      setTimeout(() => {this.pendingChanges = false}, 0); // Wrap in timeout, otherwise Vue doesn't take this change into account
    },
    stopSimulation: function () {
      this.simCancel = true;
    },
    setError: function (message) {
      this.errorMsg = "[ERROR]: " + message;
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
});
