"use strict";

Vue.component("video-record-controls", {
  props: ["el"],
  data: function () {
    return {
      videoCreator: {},
      statusMsg: "",
    };
  },
  created: function () {
    this.videoCreationService = videoCreationService;
  },
  methods: {
    handleError: function(msg) {
      this.videoDone(null, msg);
    },
    renderingUpdate: function (stats) {
      const _videoRenderingProgress = (
        stats.currentFrame / stats.totalFrames * 100
      ).toFixed(2);

      this.statusMsg = `Rendering video... ${_videoRenderingProgress}%`;
    },
    videoDone: function (blob, err) {
      if (err == null) {
        this.$emit("video-done", blob);
        const videoURL = URL.createObjectURL(blob);
        downloadLink(videoURL, "mp4");
        this.statusMsg = "";
      } else {
        this.$emit("video-error");
        this.statusMsg = "There was an error while processing the video.";
      }
    },
    record: function (el, videoDuration) {
      this.videoCreationService.record(
        el,
        videoDuration,
        this.videoDone.bind(this),
        this.renderingUpdate.bind(this),
        this.handleError.bind(this),
      );
      this.statusMsg =
        "Recording video... (Try not to leave this tab, otherwise video may end up snappy)";
    },
    stop: function () {
      if (this.videoCreationService.state === VCStates.INPROGRESS) {
        this.statusMsg = "Rendering video...";
        setTimeout(() => {
          this.videoCreationService.stop();
        }, 1800); // Don't stop it immediately because we may lose frames.
      }
    },
  },
  template: `<div>
        <span>{{ statusMsg }}</span>
    </div>`,
});
