// vue.config.js
module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        'vue': 'vue/dist/vue.esm-bundler.js'
      }
    }
  },
  chainWebpack: (config) => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0]['__VUE_OPTIONS_API__'], JSON.stringify(true));
      Object.assign(definitions[0]['__VUE_PROD_DEVTOOLS__'], JSON.stringify(false));
      Object.assign(definitions[0]['__VUE_PROD_HYDRATION_MISMATCH_DETAILS__'], JSON.stringify(false));
      return definitions;
    });
  },
};
