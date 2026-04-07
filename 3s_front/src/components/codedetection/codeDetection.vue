<template>
  <div class="container-xxl page-container">
    <div ref="uploadSection" class="upload-section card">
      <div ref="uploadHeader" class="upload-header">
        <i class="bi bi-upload upload-icon"></i>
        <span class="fw-bold">上传代码段</span>
        <div class="header-buttons">
          <button class="custom-detect-button" size="small" plain @click="handleDetect">
            <Edit style="width: 30px; height: 30px;" /> 检测
          </button>
          <button class="custom-clear-button" size="small" plain @click="handleClear">
            <Delete style="width: 30px; height: 30px;" /> 清空
          </button>
        </div>
      </div>
      <div class="upload-content">
        <!-- 上传代码的内容区域，假设使用一个textarea -->
        <!--        <textarea v-model="code" class="code-editor" placeholder="请输入代码..."></textarea>-->
        <!-- 使用 CodeMirror 编辑器 -->
        <Codemirror
            v-model:value="code"
            :options="cmOptions"
            placeholder="// 请输入脚本内容"
            @ready="onReady"
            :height="calculatedHeight"
        />
      </div>
    </div>
    <div class="report-section card">
      <div class="report-header">
        <i class="bi bi-file-earmark-text upload-icon bold-icon"></i>
        <span class="fw-bold">检测报告</span>
        <i class="bi bi-download download-icon bold-icon ml-auto"></i>
      </div>
      <div class="report-content">
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, reactive, ref} from 'vue';
import '/assets/css/bootstrap-icons.css';
// import { ElMessage } from 'element-plus';
import axios from 'axios';
import { Edit, Delete, Download } from '@element-plus/icons-vue';
import CodeMirror, {Editor, EditorConfiguration} from "codemirror";
import Codemirror from "codemirror-editor-vue3";
// 引入css文件
import 'codemirror/lib/codemirror.css'
// placeholder
import "codemirror/addon/display/placeholder.js";

// 引入语言模式 可以从 codemirror/mode/ 下引入多个
import "codemirror/mode/javascript/javascript.js";
import "codemirror/mode/python/python.js";
import "codemirror/mode/cmake/cmake.js";
import "codemirror/mode/go/go.js";
import "codemirror/mode/clike/clike.js";
// import "codemirror/mode/go/go.js";
// placeholder
import "codemirror/addon/display/placeholder.js";
// 引入主题 可以从 codemirror/theme/ 下引入多个
import 'codemirror/theme/idea.css'
import 'codemirror/theme/neat.css'
import * as marked from 'marked';

// 代码编辑器
const cmOptions = ref({
  mode: "javascript",
  theme: "neat", // Theme
  readOnly: false,
  lineNumbers: true,
  lineWiseCopyCut: true,
  gutters: ["CodeMirror-lint-markers"],
  lint: true,
})

const onReady = (cm) => {
  cm.refresh()
};


const code = ref('');  // 用户输入的代码
const report = ref('');  // 显示检测报告

// 用于存储 CodeMirror 编辑器实例
let editor = null;

const handleDetect = async () => {
  if (!code.value) {
    // ElMessage.warning('请输入代码');  // 如果没有输入代码，显示警告
    alert('请输入代码');
    return;
  }

  // try {
    // 向后端发送 POST 请求，传递代码内容
    const response = await axios.post('http://127.0.0.1:5000/upload_code', { code: code.value });

    // 接收后端返回的数据，并格式化为 JSON 字符串显示在前端
    const report = response.data;
    console.log(report)
  const report1 = report.join('\n');
    const html = marked.marked(report1);
    console.log(html)
    document.querySelector('.report-content').innerHTML = html;
  // } catch (error) {
  //   alert('检测失败');
  //   // ElMessage.error('检测失败');  // 请求失败时显示错误信息
  // }
};

const handleClear = () => {
  code.value = '';  // 清空输入框
  // report.value = '';  // 清空报告
  if (editor) {
    editor.setValue('');
  }
};


// 计算高度

// 定义对元素的引用
const uploadSection = ref(null);
const uploadHeader = ref(null);

// 定义一个响应式变量用于存储计算后的高度
const calculatedHeight = ref(0);

function calculateHeight() {
  if (uploadSection.value && uploadHeader.value) {
    // 获取 .upload-section 的高度
    const sectionHeight = uploadSection.value.getBoundingClientRect().height;

    // 获取 .upload-section 的 padding-top 和 padding-bottom
    const sectionStyles = window.getComputedStyle(uploadSection.value);
    const paddingTop = parseInt(sectionStyles.paddingTop, 10);
    const paddingBottom = parseInt(sectionStyles.paddingBottom, 10);

    // 获取 .upload-header 的高度
    const headerHeight = uploadHeader.value.getBoundingClientRect().height;

    // 计算最终的高度
    calculatedHeight.value = sectionHeight - paddingTop - paddingBottom - headerHeight - 20;
    return calculatedHeight.value;
  }
}

onMounted(() => {
  calculatedHeight.value = calculateHeight();
});
</script>

<style scoped>
/* Add your styles here */
</style>



<style scoped>
.page-container {
  display: flex;
  justify-content: space-between;
}

.card {
//padding: 20px;
//border: 1px solid #ddd;
//border-radius: 5px;
//box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.upload-section, .report-section {
  width: 49%;
}

.upload-header, .report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.upload-icon, .download-icon {
  margin-right: 5px;
}

.report-content pre {
  white-space: pre-wrap;
  word-break: break-all;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 5px;
  background-color: #f9f9f9;
}

/* 页面容器的样式 */
.page-container {
  display: flex;
  gap: 20px;
  padding: 25px;
  height: 800px;
  background-color: #f5f6fa;
}

/* 卡片样式 */
.card {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
//width: 10%;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 上传部分样式 */
.upload-section {
  display: flex;
  flex-direction: column;
}

/* 上传和报告头部样式 */
.upload-header,
.report-header {
  display: flex;
  align-items: center;
  font-weight: bold;
  margin-bottom: 10px;
}

/* 上传和报告图标样式 */
.upload-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #6c757d;
}

/* 头部按钮样式，右对齐 */
.header-buttons {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

/* 自定义检测按钮样式 */
.custom-detect-button {
  background-color: #eef4ff;
  color: #4285f4;
  border-radius: 8px;
  border: none;
  box-shadow: none;
  padding: 8px 12px;
  display: flex;
  width: 100px;
  align-items: center;
}

.custom-detect-button .el-icon-edit {
  color: #4285f4;
  margin-right: 4px; /* 图标与文字的间距 */
}

/* 自定义清空按钮样式 */
.custom-clear-button {
  background-color: #ffeef0;
  color: #e74c3c;
  border-radius: 8px;
  border: none;
  box-shadow: none;
  padding: 8px 12px;
  display: flex;
  width: 100px;
  align-items: center;
}

.custom-clear-button .el-icon-delete {
  color: #e74c3c;
  margin-right: 4px; /* 图标与文字的间距 */
}

/* 上传内容和报告内容样式 */
.upload-content,
.report-content {
  flex: 1;
  overflow-y: auto; /* 超出内容时显示垂直滚动条 */
  box-sizing: border-box; /* 包括内边距和边框在内的总高度 */
  border-radius: 8px;
  padding: 10px;
  background: #f9fafb;
  min-height: 300px; /* 根据需求调整高度 */
}


/* 下载图标的样式调整 */
.download-icon {
  font-size: 24px;
  color: #6c757d;
  margin-left: auto;
  cursor: pointer;
}

.codemirror-container {
  font-size: 15px;
}

</style>
