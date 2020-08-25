module.exports = {
  publicPath:
    process.env.NODE_ENV === "production"
      ? "https://cdn.jsdelivr.net/gh/maks500/ecm-FrontendServer@release/static"
      : "/static/",
  outputDir: "static/",
  configureWebpack: {
    devtool: "source-map",
  },
  devServer: {
    proxy: {
      "^/(api|simulate)": {
        target: "http://127.0.0.1:5000",
      },
    },
  },
};
