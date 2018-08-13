import Vue from 'vue'
import axios from 'axios'

import App from './App'
import router from './router'
import store from './store'

// Install Sentry
import Raven from 'raven-js'
import RavenVue from 'raven-js/plugins/vue'

Raven.config('https://8f4470dadf3c4264883978c1a2092f19@sentry.io/1256668')
Raven.addPlugin(RavenVue, Vue)
Raven.install()

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')
