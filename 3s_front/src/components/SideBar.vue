<script setup>
import { useRoute } from 'vue-router';
import { ref, watch } from 'vue';
import axios from 'axios';

const route = useRoute();

// 定义 sidebar 的类型，默认值是 'default'
const sidebarType = ref(route.meta.sidebar || 'default');

// 监听路由变化，更新 sidebarType
watch(route, (newRoute) => {
  sidebarType.value = newRoute.meta.sidebar || 'default';
});

const files = ref([]);  // 用于存储项目文件列表
const pname = ref(route.params.pname || 'defaultPname');// 获取 pname 参数

// 获取文件列表
const fetchFiles = async (pname) => {
  try {
    console.log('Request params:', { pname });  // 打印请求参数
    const response = await axios.get('http://127.0.0.1:5000/get-json', {
      params: { pname: pname },
    });

    // 检查 response.data 的类型
    console.log('API response:', response.data);  // 打印 API 返回的数据

    // 如果返回的是数组
    if (Array.isArray(response.data)) {
      // 如果是文件数组，直接去重并显示
      const uniqueFiles = Array.from(new Set(response.data.map(file => file.file_path)))
          .map(file_path => response.data.find(file => file.file_path === file_path));
      files.value = uniqueFiles;
    } else {
      // 如果返回的是对象，且包含 files 属性
      if (response.data.files && Array.isArray(response.data.files)) {
        const uniqueFiles = Array.from(new Set(response.data.files.map(file => file.file_path)))
            .map(file_path => response.data.files.find(file => file.file_path === file_path));
        files.value = uniqueFiles;
      } else {
        console.error("Invalid response format: Missing 'files' array");
      }
    }
  } catch (error) {
    console.error('Error fetching project files:', error);
  }
};

// 监听 pname 变化并获取相应文件列表
// 监听 pname 变化并获取文件列表
watch(() => route.params.pname, async (newPname) => {
  if (newPname) {
    pname.value = newPname;
    await fetchFiles(pname.value);
  } else {
    console.warn('pname is undefined');
  }
}, { immediate: true });

// 判断当前路由是否活跃
const isActive = (path) => route.path === path;
const isStart = (path) => route.path.startsWith(path);
const isLogin = true; // 假设用户已登录
</script>

<template>
  <aside id="layout-menu" class="layout-menu menu-vertical menu bg-menu-theme">
    <div class="app-brand demo">
      <a href="/home/index" class="app-brand-link" style="height: 100%;">
        <span class="app-brand-text demo menu-text fw-bolder ms-2" style="height: 100%; text-transform: uppercase;">
            <img src="../../assets/picture/Logo.png" class="mb-2" alt="" width="6%">AGenticVul
        </span>
      </a>
      <a href="javascript:void(0);" class="layout-menu-toggle menu-link text-large ms-auto d-block d-xl-none">
        <i class="bx bx-chevron-left bx-sm align-middle"></i>
      </a>
    </div>

    <div class="menu-inner-shadow"></div>

    <ul class="menu-inner py-1">
      <!-- 默认 sidebar -->
      <template v-if="sidebarType === 'default'">
        <li v-show="isLogin" :class="{ 'active': isActive('/home/index'), 'menu-item': true }">
          <router-link to="/home/index" class="menu-link">
            <i class="menu-icon tf-icons bx bx-home-circle"></i>
            <div data-i18n="Analytics">检测总览</div>
          </router-link>
        </li>
        <li v-show="isLogin" :class="{ 'active': isActive('/home/project'), 'menu-item': true }">
          <router-link to="/home/project" class="menu-link">
            <i class="menu-icon tf-icons bx bx-detail"></i>
            <div data-i18n="Form Elements">项目管理</div>
          </router-link>
        </li>
        <li v-show="isLogin" :class="{ 'active': isActive('/home/upload'), 'menu-item': true }">
          <router-link to="/home/upload" class="menu-link">
            <i class="menu-icon tf-icons bx bx-upload"></i>
            <div data-i18n="Form Elements">项目检测</div>
          </router-link>
        </li>
        <li v-show="isLogin" :class="{ 'active': isActive('/home/codedetection'), 'menu-item': true }">
          <router-link to="/home/codedetection" class="menu-link">
            <i class="menu-icon tf-icons bx bxs-cog"></i>
            <div data-i18n="Form Elements">实时检测</div>
          </router-link>
        </li>
        <li v-show="isLogin" :class="{ 'active': isActive('/home/chat'), 'menu-item': true }">
          <router-link to="/home/chat" class="menu-link">
            <i class="menu-icon tf-icons bx bx-cube-alt"></i>
            <div data-i18n="Account Settings">智能问答</div>
          </router-link>
        </li>
        <li v-show="isLogin" :class="{ 'active': isActive('/home/account'), 'menu-item': true }">
          <router-link to="/home/account" class="menu-link">
            <i class="menu-icon tf-icons bx bx-dock-top"></i>
            <div data-i18n="Account Settings">账号设置</div>
          </router-link>
        </li>
      </template>

      <!-- 项目详情的 sidebar -->
      <template v-if="sidebarType === 'project'">
        <!-- 返回首页的选项 -->
        <li v-show="isLogin" :class="{ 'active': isActive('/home/project'), 'menu-item': true }">
          <router-link to="/home/project" class="menu-link">
            <i class="menu-icon tf-icons bx bx-home"></i>
            <div>返回首页</div>
          </router-link>
        </li>
        <!-- 项目概览的选项 -->
        <li v-show="isLogin" :class="{ 'active': isActive('/home/ProjectOverview'), 'menu-item': true }">
          <router-link :to="{ name: 'ProjectOverview', params: { pname: pname } }" class="menu-link">
            <i class="menu-icon tf-icons bx bx-home"></i>
            <div>项目概览</div>
          </router-link>
        </li>
        <!-- 项目文件列表 -->
        <li v-for="file in files" :key="file.file_path" v-show="isLogin" :class="{ 'active': isActive(file.file_path), 'menu-item': true }">
          <router-link :to="{ name: 'ProjectDetail', params: { id: file.file_path, pname: pname, file_path: file.file_path } }" class="menu-link">
            <i class="menu-icon tf-icons bx bx-file"></i>
            <div>{{ file.file_path }}</div>
          </router-link>
        </li>



        <!-- 添加更多的文件菜单项 -->
      </template>
    </ul>
  </aside>
</template>

<style scoped>
@import url('/assets/vendor/fonts/boxicons.css');
@import url('/assets/vendor/css/core.css');
@import url('/assets/vendor/css/theme-default.css');
@import url('/assets/css/demo.css');
@import url('/assets/vendor/libs/perfect-scrollbar/perfect-scrollbar.css');
@import url('/assets/vendor/libs/apex-charts/apex-charts.css');

.custom-image {
  display: block;
  margin: 0 auto;
  width: 200px; /* 可根据需求调整宽度 */
  height: auto;
}
</style>