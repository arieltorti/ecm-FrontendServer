"use strict";

function handleWorkerMessages(_onDone) {
  return function (e) {
    const msg = e.data;
    switch (msg.type) {
      case "stdout":
      case "stderr":
        console.debug(msg.data);
        break;
      case "exit":
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

const videoCreationService = (function () {
  let _state = VCStates.IDLE;
  let _done = false;
  let _cancel = false;
  let onDone = () => {};
  let _messageHandler = () => {};
  let worker = new Worker("js/ffmpeg-worker-mp4.js");

  function generateVideo(el) {
    const messageHandler = handleWorkerMessages(_onDone);
    _messageHandler = messageHandler;
    worker.addEventListener("message", messageHandler);

    function getFrame() {
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
      });

      if (_cancel) {
        return;
      }

      if (!_done) {
        requestAnimationFrame(getFrame);
      } else {
        requestAnimationFrame(buildVideo);
      }
    }

    function buildVideo() {
      const width = el.clientWidth % 2 == 0 ? el.clientWidth : el.clientWidth + 1;
      const height = el.clientHeight % 2 == 0 ? el.clientHeight : el.clientHeight + 1;

      worker.postMessage({
        type: "run",
        TOTAL_MEMORY: 1024 * 1024 * 1024,
        arguments: [
          "-r",
          "25",
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
    }

    const images = [];
    _state = VCStates.INPROGRESS;
    getFrame();
  }

  function _onDone(blob) {
    _state = VCStates.DONE;
    worker.removeEventListener("message", _messageHandler);
    onDone(blob);
    _state = VCStates.IDLE;
  }

  function state() {
    return _state;
  }

  function record(el, cb) {
    _cancel = false;
    _done = false;
    onDone = cb;
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
