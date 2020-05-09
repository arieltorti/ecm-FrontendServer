Vue.component('error-msg', {
  props: ['error'],
  template: '<pre id="errorMsg">{{ error }}</pre>'
})