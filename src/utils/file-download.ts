import { PlotData } from "./graph-data";

/**
 * Returns current date formatted as YYYYmmdd-HHMMss
 */
export function getCurrentDate(): string {
  function pad(str: number) {
    return ("0" + str).slice(0, 2);
  }

  const now = new Date();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  return `${now.getUTCFullYear()}${month}${day}-${hours}${minutes}${seconds}`;
}

export function downloadLink(href: string, extension = "csv"): void {
  const linkEl = document.createElement("a");
  linkEl.setAttribute("href", href);
  linkEl.setAttribute("download", `sim-${getCurrentDate()}.${extension}`);

  document.body.appendChild(linkEl);
  linkEl.click();
  linkEl.remove();
}

/**
 * Generates transposed CSV content
 *
 * @param {*} plotData
 */
export function generateCSV(plotData: PlotData[]): void {
  const csvHeader = "sampletimes," + plotData.data.map(x => x.name).join(",");
  const sampleTimes = plotData.data[0].x;
  const data = plotData.data.map(x => x.y);

  let csv = csvHeader + "\r\n";
  for (let i = 0; i < sampleTimes.length; i++) {
    csv += sampleTimes[i] + "," + data.map(x => x[i]).join(",") + "\n";
  }

  const CSVBlob = new Blob([csv], { type: "text/csv" });
  downloadLink(window.URL.createObjectURL(CSVBlob));
}
