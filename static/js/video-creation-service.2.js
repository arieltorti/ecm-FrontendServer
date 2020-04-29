"use strict";

const CURRENT_FRAME_REGEX = /frame=\s*(\d+)/;

function handleWorkerMessages(_onDone, _onMessage, _onError) {
  return function (e) {
    const msg = e.data;
    switch (msg.type) {
      case "stdout":
      case "stderr":
        console.debug(msg.data);
        _onMessage(msg.data);
        break;
      case "exit":
        if (msg.data === 1) {
          _onError("Process exited with code " + msg.data);
        }
        console.debug("Process exited with code " + msg.data);
        break;

      case "done":
        const blob = new Blob([msg.data.MEMFS[0].data], {
          type: "video/mp4",
        });
        console.debug(blob);
        _onDone(blob);
        break;
      default:
        console.debug(e);
    }

    if (msg.type == null) {
      console.debug(e);
    }
  };
}

function align(str, len) {
  return (new Array(len).fill("0").join("") + str).slice(-len);
}

function convertDataURIToBinary(dataURI) {
  var base64 = dataURI.replace(/^data[^,]+,/, "");
  var raw = window.atob(base64);
  var rawLength = raw.length;

  var array = new Uint8Array(new ArrayBuffer(rawLength));
  for (let i = 0; i < rawLength; i++) {
    array[i] = raw.charCodeAt(i);
  }
  return array;
}

// https://benohead.com/blog/2017/12/06/cross-domain-cross-browser-web-workers/
function createWorker(workerUrl) {
  let worker = null;
  try {
    // Non cross-origin case
    worker = new Worker(workerUrl);
  } catch (e) {
    try {
      // Cross-origin case
      var blob;
      try {
        blob = new Blob(["importScripts('" + workerUrl + "');"], {
          type: "application/javascript",
        });
      } catch (e1) {
        var blobBuilder = new (window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder)();
        blobBuilder.append("importScripts('" + workerUrl + "');");
        blob = blobBuilder.getBlob("application/javascript");
      }
      const url = window.URL || window.webkitURL;
      const blobUrl = url.createObjectURL(blob);
      worker = new Worker(blobUrl);
    } catch (e2) {
      throw e2;
    }
  }
  return worker;
}

const videoCreationService = (function () {
  let _state = VCStates.IDLE;
  let _done = false;
  let _cancel = false;
  let onDone = () => {};
  let onMessage = () => {};
  let onError = () => {};
  let _messageHandler = () => {};
  let worker = createWorker(
    "https://cdn.jsdelivr.net/gh/maks500/CMS-FrontendServer@WIP-video-rendering/static/js/ffmpeg-worker-mp4.js"
  );
  let images = [];
  let videoDuration = 0;

  function generateVideo(el) {
    const promiseArray = [];
    const messageHandler = handleWorkerMessages(_onDone, _onMessage, _onError);
    _messageHandler = messageHandler;
    worker.addEventListener("message", messageHandler);

    function getFrame() {
      promiseArray.push(
        html2canvas(el, {
          scrollX: -window.scrollX,
          scrollY: -window.scrollY,
        })
          .then((canvas) => {
            const imgString = canvas.toDataURL("image/jpeg", 1);
            const data = convertDataURIToBinary(imgString);

            images.push({
              name: `img${align(images.length, 6)}.jpeg`,
              data,
            });
          })
          .catch((err) => console.error(err))
      );

      if (_cancel) {
        return;
      }
    }

    function buildVideo() {
      plotDiv.removeListener("plotly_redraw", getFrame);
      plotDiv.removeListener("plotly_animated", buildVideo);

      const width = el.clientWidth % 2 == 0 ? el.clientWidth : el.clientWidth + 1;
      const height = el.clientHeight % 2 == 0 ? el.clientHeight : el.clientHeight + 1;

      // Wait for all images
      Promise.all(promiseArray).then(() => {
        const frameRate = (images.length / (videoDuration || 1)).toFixed(1);
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

    images = [];
    _state = VCStates.INPROGRESS;

    plotDiv.on("plotly_redraw", getFrame);
    plotDiv.on("plotly_animated", buildVideo);
  }

  function _onDone(blob) {
    _state = VCStates.DONE;
    worker.removeEventListener("message", _messageHandler);
    onDone(blob);
    _state = VCStates.IDLE;
  }

  function _onError(msg) {
    onError(msg);
  }

  function _onMessage(msg) {
    const match = msg.match(CURRENT_FRAME_REGEX);

    if (match != null) {
      onMessage({ currentFrame: match[1], totalFrames: images.length });
    }
  }

  function record(el, _videoDuration = 1, cb, messageCb, errorCb) {
    _cancel = false;
    _done = false;
    videoDuration = _videoDuration;

    if (cb == null) {
      throw new Error("A callback must be given to the video creation service");
    }
    onDone = cb;

    if (messageCb != null) {
      onMessage = messageCb;
    } else {
      onMessage = () => {};
    }

    if (errorCb != null) {
      onError = errorCb;
    } else {
      onError = () => {};
    }

    generateVideo(el);
  }

  function stop() {
    _done = true;
  }

  function cancel() {
    _state = VCStates.STOP;
    _cancel = true;
    onDone = () => {}; // Just in case we sent the message to the worker.
  }

  return {
    get state() {
      return _state;
    },
    record: record,
    stop: stop,
    cancel: cancel,
  };
})();
Object.freeze(videoCreationService);
