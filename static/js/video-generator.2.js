"use strict";

Vue.component("video-record-controls", {
  props: ["el"],
  data: function () {
    return {
      videoCreator: {},
      videoURL: null,
      statusMsg: "",
    };
  },
  created: function () {
    this.videoCreationService = videoCreationService;
  },
  methods: {
    videoDone: function (blob, err) {
      if (err == null) {
        this.$emit("video-done", blob);
        this.videoURL = URL.createObjectURL(blob);
        this.statusMsg = "";
      } else {
        this.statusMsg = "There was an error while processing the video.";
      }
    },
    record: function (el) {
      this.videoCreationService.record(el, this.videoDone.bind(this));
      this.statusMsg = "Recording video... (Try not to leave this tab, otherwise video may end up snappy)";
    },
    stop: function () {
      debugger;
      if (this.videoCreationService.state === VCStates.INPROGRESS) {
        this.statusMsg = "Rendering video...";
        setTimeout(() => {
          this.videoCreationService.stop();
        }, 1000); // Don't stop it immediately because we may lose frames.
      }
    },
  },
  template: `<div>
        <span>{{ statusMsg }}</span>
        <video controls v-if="videoURL" :src="videoURL"></video>
    </div>`,
});
