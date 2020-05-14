import Vue from "vue";
import { replaceModelVariableValue } from "../utils/variable-extractor";
import { preciseRound } from "../utils/numbers";
import { makeGraphData, plotData, plotMetadata } from "../utils/graph-data";

export interface IterationConfig {
  iterVar: string | null;
  from?: number;
  to?: number;
  step?: number;
}

export interface SimulationConfig {
  model: string;
  config: string;
  iterationConfig: IterationConfig;
}

export const SimEventBus = new Vue();

export const SimulationService = (function() {
  let abortController: AbortController | null = null;

  function _simulateOnce(
    model: string,
    config: string,
    graphHistoricData: plotData[],
    metadata?: plotMetadata
  ): Promise<any> {
    SimEventBus.$emit("sim-update");

    const body = new FormData();
    body.append("model", model);
    body.append("config", config);

    const controller = new AbortController();
    const signal = controller.signal;
    abortController = controller;

    const req = fetch("/api/compute", {
      method: "POST",
      body,
      signal
    });

    return req
      .then(res => {
        if (res.status >= 400 && res.status < 600) {
          throw res;
        }
        return res.json();
      })
      .then(data => {
        const graphData = makeGraphData(data, metadata);
        graphHistoricData.push(graphData);
      });
  }

  function _simulateIterating(
    model: string,
    config: string,
    iterationConfig: IterationConfig,
    graphHistoricData: plotData[]
  ): Promise<any> {
    const { from, to, step, iterVar } = iterationConfig;

    if (from == null || to == null || step == null) {
      throw new Error("Invalid iteration configuration given to simulation");
    }

    if (step == 0) {
      throw new Error("Iteration step cannot be 0");
    }

    if ((to < from && step > 0) || (from < to && step < 0)) {
      throw new Error(
        `Cant simulate from ${from} to ${to} when step is ${step}`
      );
    }

    // If we selected an interating variable send as many request as needed chaining them
    // to avoid overloading the server.
    let promiseChain = Promise.resolve();

    for (let _from = from; _from <= to; _from = preciseRound(_from + step)) {
      promiseChain = promiseChain.then(() => {
        return _simulateOnce(
          replaceModelVariableValue(model, iterVar as string, _from),
          config,
          graphHistoricData,
          { iterationValue: _from } as plotMetadata
        );
      });
    }

    return promiseChain;
  }

  function handleError(error) {
    if (error.ABORT_ERR && error.code === error.ABORT_ERR) {
      console.debug("Request aborted");
    } else {
      SimEventBus.$emit("sim-error", error);
    }
  }

  function simulate(simulationConfig: SimulationConfig): void {
    const { model, config, iterationConfig } = Object.assign(
      {},
      simulationConfig
    ); // Clone to avoid mutating passed data.
    SimEventBus.$emit("sim-processing", model, config, iterationConfig);

    if (model == null || model.length === 0) {
      throw new Error("Empty model given to simulation");
    }

    if (config == null || config.length === 0) {
      throw new Error("Empty configuration given to simulation");
    }

    const graphHistoricData: plotData[] = [];

    try {
      if (iterationConfig.iterVar != null) {
        _simulateIterating(model, config, iterationConfig, graphHistoricData)
          .then(val => {
            SimEventBus.$emit("sim-done", graphHistoricData);
            return val;
          })
          .catch(handleError);
      } else {
        _simulateOnce(model, config, graphHistoricData)
          .then(val => {
            SimEventBus.$emit("sim-done", graphHistoricData);
            return val;
          })
          .catch(handleError);
      }
    } catch (e) {
      handleError(e);
    }
  }

  function cancel() {
    abortController?.abort();
    SimEventBus.$emit("sim-canceled");
  }

  function play(redraw = true, fromStart = false) {
    SimEventBus.$emit("sim-anim-play", redraw, fromStart);
  }

  function pause() {
    SimEventBus.$emit("sim-anim-pause");
  }

  return {
    simulate,
    cancel,
    play,
    pause,
  };
})();
Object.freeze(SimulationService);
