export interface GraphData {
  SampleTimes: number[];
  ChannelData: number[][];
  ObservableNames: string[];
}

interface PlotMetadata {
  iterationValue?: number;
}

/** Plotly supports react-plotly types but not vanilla Plotly. */
export interface PlotFrame {
  x: number[];
  y: number[];
  name: string;
}

export interface PlotData extends Array<PlotFrame> {
  metadata?: PlotMetadata;
}

function arrayMean(array: number[]): number[] {
  const arrayCopy = array.slice();
  for (let i = 1; i < arrayCopy.length - 1; i++) {
    const prev = array[i - 1];
    const next = array[i + 1];

    arrayCopy[i] = (prev + array[i] + next) / 3;
  }

  return arrayCopy;
}

/**
 * Extract graph data from JSON request output
 *
 * @param {*} data
 */
export function makeGraphData(data: GraphData, metadata?: PlotMetadata): PlotData {
  const { SampleTimes, ChannelData, ObservableNames } = data;

  const xAxis = SampleTimes;
  const graphData: PlotData = [];

  for (let i = 0; i < ChannelData.length; i++) {
    graphData.push({
      x: arrayMean(xAxis),
      y: ChannelData[i],
      name: ObservableNames[i],
    });
  }
  graphData.metadata = metadata;

  return graphData;
}

const EPSILON = 0.0000001;
export function calculateTotalSteps(to: number, from: number, step: number): number {
  return Math.floor(1 + Math.floor((to - from) / step + EPSILON));
}
