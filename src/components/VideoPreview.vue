<template>
  <div>
    <button @click="record">{{ recording ? "Stop Recording" : "Record Video" }}</button>
    <span>{{ status }}</span>
  </div>
</template>

<script lang="ts">
import { Component, PropSync, Prop, Vue } from "vue-property-decorator";
import { VideoCreationService, FfmpegImage, CURRENT_FRAME_REGEX } from "../services/video-creating-service";
import { SimEventBus } from "../services/simulation-service";
import { downloadLink } from "../utils/file-download";

@Component({})
export default class VideoPreview extends Vue {
  @Prop() videoDuration!: number;
  private recording = false;
  private status = "";
  private totalImages = 0;

  private stop: (() => void) | null = null;

  created() {
    SimEventBus.$on("video-stop", this.onVideoStop);
    SimEventBus.$on("video-done", this.onVideoDone);
    SimEventBus.$on("video-message", this.onVideoMessage);
    SimEventBus.$on("video-start", this.onVideoStart);

    SimEventBus.$on("render-start", this.onRenderStart);
  }

  beforeDestroy() {
    SimEventBus.$off("video-stop", this.onVideoStop);
    SimEventBus.$off("video-done", this.onVideoDone);
    SimEventBus.$off("video-message", this.onVideoMessage);
    SimEventBus.$off("video-start", this.onVideoStart);

    SimEventBus.$off("render-start", this.onRenderStart);
  }

  onRenderStart(images: FfmpegImage[]) {
    this.totalImages = images.length;
  }

  onVideoStop() {
    this.recording = false;
    this.status = "";
  }

  onVideoDone(blob: Blob) {
    this.recording = false;
    const videoURL = URL.createObjectURL(blob);
    downloadLink(videoURL, "mp4");
  }

  onVideoMessage(msg: string) {
    const match = msg.match(CURRENT_FRAME_REGEX);

    if (match != null) {
      this.status = "Rendering " + (parseInt(match[1], 10) / this.totalImages) * 100 + "%";
    }
  }

  onVideoStart() {
    this.status = "Recording...";
    this.totalImages = 0;
    this.recording = true;
  }

  record() {
    if (this.recording) {
      this.stop && this.stop();
      return;
    }

    // TODO: This is hardcoded, how can we make this more flexible ?
    const plotDiv = document.getElementById("plotDiv");

    if (plotDiv == null) {
      throw new Error("plotDiv does not exist.");
    }
    const { stop } = VideoCreationService.record(plotDiv, this.videoDuration);
    this.stop = stop;
  }
}
</script>

<style lang="scss" scoped>
span {
  display: block;
}
</style>
