import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import VueApexCharts from "vue3-apexcharts";
import axios from "axios";


axios.defaults.withCredentials = true; // 发送凭据
axios.defaults.xsrfCookieName = 'session:'; // 以‘session:’识别会话

const app = createApp(App);
app.use(router);
// app.use(VueApexCharts);
// app.component("apexchart", VueApexCharts);
app.mount('#app1');
