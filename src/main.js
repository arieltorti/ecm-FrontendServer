import Vue from "vue";
import App from "./App.vue";
import VueKatex from "vue-katex";
import "katex/dist/katex.min.css";
import titleMixin from "./mixins/titleMixin";

Vue.config.productionTip = false;

Vue.mixin(titleMixin);
Vue.use(VueKatex, {
  globalOptions: {
    //... Define globally applied KaTeX options here
  },
});

new Vue({
  render: (h) => h(App),
}).$mount("#app");
