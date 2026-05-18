import './assets/entrance.css'
import './assets/home.css'
import './assets/info.css'
import './assets/profile.css'
import './assets/appeal.css'
import './assets/news.css'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
