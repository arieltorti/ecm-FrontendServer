import html2canvas from "html2canvas";
import { SimEventBus, SimulationService } from "../services/simulation-service";

export const CURRENT_FRAME_REGEX = /frame=\s*(\d+)/;

function handleWorkerMessages() {
  let blob = null;
  let video = null;

  return function(e) {
    const msg = e.data;
    switch (msg.type) {
      case "stdout":
      case "stderr":
        SimEventBus.$emit("video-message", msg.data);
        console.debug(msg.data);
        break;
      case "exit":
        console.debug("Process exited with code " + msg.data);
        break;

      case "done":
        blob = new Blob([msg.data.MEMFS[0].data], {
          type: "video/mp4",
        });
        console.debug(blob);
        SimEventBus.$emit("video-done", blob);

        video = document.createElement("video");
        video.src = URL.createObjectURL(blob);
        video.setAttribute("controls", "");
        document.body.appendChild(video);

        break;
      default:
        console.debug(e);
    }

    if (msg.type == null) {
      console.debug(e);
    }
  };
}

function align(str: string | number, len: number) {
  return (new Array(len).fill("0").join("") + str).slice(-len);
}

function convertDataURIToBinary(dataURI: string) {
  const base64 = dataURI.replace(/^data[^,]+,/, "");
  const raw = window.atob(base64);
  const rawLength = raw.length;

  const array = new Uint8Array(new ArrayBuffer(rawLength));
  for (let i = 0; i < rawLength; i++) {
    array[i] = raw.charCodeAt(i);
  }
  return array;
}

// https://benohead.com/blog/2017/12/06/cross-domain-cross-browser-web-workers/
function createWorker(workerUrl: string) {
  let worker = null;
  try {
    // Non cross-origin case
    worker = new Worker(workerUrl);
  } catch (e) {
    try {
      // Cross-origin case
      let blob;
      try {
        blob = new Blob(["importScripts('" + workerUrl + "');"], {
          type: "application/javascript",
        });
      } catch (e1) {
        const blobBuilder = new (window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder)();
        blobBuilder.append("importScripts('" + workerUrl + "');");
        blob = blobBuilder.getBlob("application/javascript");
      }
      const url = window.URL || window.webkitURL;
      const blobUrl = url.createObjectURL(blob);
      worker = new Worker(blobUrl);
    } catch (e) {
      console.debug("Could not create worker");
      throw e;
    }
  }
  return worker;
}

export interface FfmpegImage {
  name: string;
  data: Uint8Array;
}

export const VideoCreationService = (function() {
  const worker = createWorker(
    "https://cdn.jsdelivr.net/gh/maks500/CMS-FrontendServer@WIP-video-rendering/static/js/ffmpeg-worker-mp4.js"
  );
  worker.addEventListener("message", handleWorkerMessages());

  function record(el: HTMLElement, videoDuration: number) {
    const promiseArray: Promise<any>[] = [];
    const images: FfmpegImage[] = [];

    function getFrame() {
      promiseArray.push(
        html2canvas(el, {
          scrollX: -window.scrollX,
          scrollY: -window.scrollY,
        }).then((canvas) => {
          const imgString = canvas.toDataURL("image/jpeg", 1);
          const data = convertDataURIToBinary(imgString);

          images.push({
            name: `img${align(images.length, 6)}.jpeg`,
            data,
          });
        })
      );
    }

    function buildVideo() {
      clean();
      const width = el.clientWidth % 2 == 0 ? el.clientWidth : el.clientWidth + 1;
      const height = el.clientHeight % 2 == 0 ? el.clientHeight : el.clientHeight + 1;

      // Wait for all images
      Promise.all(promiseArray).then(() => {
        const frameRate = (images.length / (videoDuration || 1)).toFixed(1);

        SimEventBus.$emit("render-start", images);

        worker.postMessage({
          type: "run",
          TOTAL_MEMORY: 1024 * 1024 * 1024,
          arguments: [
            "-r",
            frameRate,
            "-i",
            "img%06d.jpeg",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-vf",
            `scale=${width}:${height}`,
            "-pix_fmt",
            "yuv420p",
            "out.mp4",
          ],
          MEMFS: images,
        });
      });
    }

    function clean() {
      el.removeListener("plotly_redraw", getFrame);
      el.removeListener("plotly_animated", buildVideo);
    }

    function stop() {
      clean();
      SimulationService.pause();
      SimEventBus.$emit("video-stop");
    }

    el.on("plotly_redraw", getFrame);
    el.on("plotly_animated", buildVideo);
    SimulationService.play(true, true);

    SimEventBus.$emit("video-start");

    return { stop };
  }

  return {
    record,
  };
})();
Object.freeze(VideoCreationService);
