Vue.component("iter-controls", {
  props: ["configInterval", "modelVariables", "buttonDisabled", "buttonText"],
  data: function () {
    return {
      formData: Vue.util.extend({}, this.configInterval), // Make a copy so we don't modify the parent's state
    };
  },
  methods: {
    handleSubmit: function (ev) {
      this.$emit("submit", this.formData);
    },
  },
  template: `<form @submit.prevent="handleSubmit">
    <button type="button" @click="$emit('reset')" style="float: right; margin-right: 2em;">
      Reset to default
    </button>

    <div>
      <div>
        <label for="iter-var">Iterate var:</label>
        <select
          name="iteratingVariable"
          id="iter-var"
          v-model="formData.iteratingVariable"
          style="margin: 1.5em 0; min-width: 10em;"
        >
          <option :value="null">None</option>
          <option v-for="(variable, index) in modelVariables" :value="variable">{{ variable }}</option>
        </select>

        <div class="interval-config">
          <label for="from">From: </label>
          <input
            type="number"
            name="from"
            step="0.000001"
            v-model.number="formData.from"
          />

          <label for="to">To: </label>
          <input
            type="number"
            name="to"
            step="0.000001"
            v-model.number="formData.to"
          />

          <label for="step">Step: </label>
          <input
            type="number"
            name="step"
            step="0.000001"
            min="0.000001"
            v-model.number="formData.step"
          />
        </div>
      </div>
    </div>

    <button
      style="margin: 1em; padding: 0.4em 0.8em; font-size: 1.15em;"
      :disabled="buttonDisabled"
    >
      {{ buttonText }}
    </button>
  </form>`,
});
