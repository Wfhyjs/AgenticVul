<template>
  <div class="container-xxl py-4">
    <div class="row">
      <!-- 左侧区域 -->
      <div class="col-md-6">
        <!-- 可视化分析 -->
        <div class="card mb-4" style="height: 300px;">
          <div class="card-body">
            <h5 class="card-title d-flex align-items-center">
              <i class="bi bi-graph-up-arrow me-2"></i> 可视化分析
            </h5>
            <div class="d-flex justify-content-between">
              <!-- 左侧条形图部分 -->
              <div id="bar-chart" style="width:200%; height: 200px;"></div>

              <!-- 右侧指标部分 -->
              <div class="w-100" style="margin-top: 10px;margin-left: 40px">
                <!-- 第一项 -->
                <div class="indicator-item mb-4 d-flex align-items-center">
                  <div class="icon-container me-3">
                    <img src="/assets/img/icons/unicons/cc-primary.png" alt="Icon" class="icon" />
                  </div>
                  <div class="text-container">
                    <h6 class="value">主要漏洞类型</h6>
                    <h5 class="title mb-1" v-if="data">{{ data.top_cwe_ids}}</h5>
                    <h5 class="title mb-1" v-else>暂无参数</h5>
                  </div>
                </div>

                <!-- 第二项 -->
                <div class="indicator-item d-flex align-items-center">
                  <div class="icon-container me-3">
                    <img src="/assets/img/icons/unicons/50.png" alt="Icon" class="icon" />
                  </div>
                  <div class="text-container">
                    <h6 class="value">含有漏洞概率</h6>
                    <h5 class="title mb-1" v-if="data" >{{ data.avg_defect_index}}</h5>
                    <h5 class="title mb-1" v-else>暂无参数</h5>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card" style="height: 300px;">
          <div class="card-body">
            <!-- 顶部标题和导航按钮 -->
            <div class="d-flex justify-content-between align-items-center">
              <!-- 图标和标题 -->
              <h5 class="card-title d-flex align-items-center">
                <i class="bi bi-code-slash me-2"></i>
                {{ activeTab === "code" ? "源代码" : "补丁" }}
              </h5>
              <!-- 导航按钮 -->
              <ul class="nav nav-pills" role="tablist">
                <li class="nav-item">
                  <button
                      type="button"
                      class="nav-link"
                      :class="{ active: activeTab === 'code' }"
                      @click="switchTab('code')"
                      role="tab"
                  >
                    源代码
                  </button>
                </li>
                <li class="nav-item">
                  <button
                      type="button"
                      class="nav-link"
                      :class="{ active: activeTab === 'patch' }"
                      @click="switchTab('patch')"
                      role="tab"
                  >
                    补丁
                  </button>
                </li>
              </ul>
            </div>

            <!-- 内容区域 -->
            <div class="tab-content mt-4">
              <div v-if="activeTab === 'code'" class="tab-pane fade show active">
                <p>请选择具体函数查看源代码</p>
              </div>
              <div v-else class="tab-pane fade show active">
                <p>请选择具体函数查看补丁</p>
              </div>
            </div>
          </div>
        </div>


      </div>

      <!-- 右侧检测报告 -->
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex align-items-center justify-content-between">
              <h5 class="card-title d-flex align-items-center">
                <i class="bi bi-file-earmark-bar-graph me-2"></i> 检测报告
              </h5>
              <button class="btn btn-link">
                <i class="bi bi-download"></i>
              </button>
            </div>
            <div id="report-content" class="report-content">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 函数总览 -->
    <div class="card mt-4">
      <div class="card-body">
        <h5 class="card-title d-flex align-items-center">
          <i class="bi bi-list-task me-2"></i> 函数总览
        </h5>

        <!-- 筛选框 -->
        <div class="row g-2 mb-3">
          <div class="col-md-4">
            <input
                type="text"
                class="form-control"
                placeholder="函数名搜索"
                v-model="filters.name"
                @input="filterTable"
            />
          </div>
          <div class="col-md-4">
            <select class="form-select" v-model="filters.risk" @change="filterTable">
              <option value="">风险等级</option>
              <option value="高风险" >高风险</option>
              <option value="低风险" >低风险</option>
              <option value="安全" >安全</option>
            </select>
          </div>
          <div class="col-md-4">
            <select class="form-select" v-model="filters.vulnerabilityType" @change="filterTable">
              <option value="">漏洞类型</option>
              <option value="SQL注入">SQL注入</option>
              <option value="XSS攻击">XSS攻击</option>
              <option value="其他">其他</option>
            </select>
          </div>
        </div>

        <!-- 表格 -->
        <table class="table table-hover table-custom">
          <thead class="table-header">
          <tr>
            <th>No</th>
            <th>函数名</th>
            <th>漏洞数量</th>
            <th>风险等级</th>
            <th>主要漏洞类型</th>
            <th>Action</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(func, index) in filteredFunctions" :key="index" @click="selectFunction(func)">
            <td>{{ func.no }}</td>
            <td>{{ func.name }}</td>
            <td>{{ func.vulnerabilities }}</td>
            <td>
<span
    :class="[
    'badge',
    func.risk === '高风险' ? 'bg-danger' :
    func.risk === '低风险' ? 'bg-warning' :
    'bg-success'
  ]"
>
  {{ func.risk }}
</span>

            </td>
            <td>{{ func.vulnerabilityType }}</td>
            <td>---</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref, computed, watch} from "vue";
import { useRoute } from "vue-router";
import * as echarts from "echarts";
import '/assets/css/bootstrap-icons.css';
// import { ElMessage } from 'element-plus';
import axios from 'axios';
import { marked } from 'marked'
import { markedHighlight } from "marked-highlight"
import hljs from 'highlight.js'
// 注意引入样式，你可以前往 node_module 下查看更多的样式主题
import 'highlight.js/styles/base16/google-light.css'

let rendererMD = new marked.Renderer();  // 创建一个自定义的渲染器实例

marked.setOptions({
  renderer: rendererMD,  // 使用自定义的渲染器 rendererMD
  // highlight: function(code) {  // 配置代码高亮方法
  //   return hljs.highlightAuto(code).value;  // 使用 highlight.js 自动检测代码语言并高亮显示
  // },
  pedantic: false,  // 禁用严格模式，允许一些非标准的 Markdown 语法
  gfm: true,  // 启用 GitHub Flavored Markdown (GFM) 语法支持
  tables: true,  // 启用表格语法支持
  breaks: false,  // 禁用换行符（\n）自动转换为 <br> 标签
  sanitize: true,  // 启用 HTML 清理功能，防止 XSS 攻击
  smartLists: true,  // 启用智能列表功能，自动转换列表的顺序
  smartypants: false,  // 禁用智能排版（例如：转换引号为弯引号）
  xhtml: false  // 设置为 false，使用 HTML5 标准格式，而不是 XHTML
});

// 高亮拓展
marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'shell'
    return hljs.highlight(code, { language }).value
  }
}))



const route = useRoute();
const pname = computed(()=>{return route.params.pname}); // 接收 pid 参数

const functionOverview = ref([]); // 存储函数概览数据


const activeTab = ref("code");

const switchTab = (tab) => {
  activeTab.value = tab;
};
const data = ref(null);


async function fetchData() {
  const response = await axios.get(`http://127.0.0.1:5000/get-overall-data`,{
    params: {
      pname: pname.value // 加入 pname 参数
    }});
  data.value = response.data;
  const chartDom = document.getElementById("bar-chart");
  const myChart = echarts.init(chartDom);

  const option = {
    grid: {
      left: "2%",
      right: "2%",
      bottom: "2%",
      top: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: ["修复概率", "漏洞风险", "影响程度"],
      axisLabel: {
        fontSize: 14,
        color: "#666",
      },
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
    },
    yAxis: {
      type: "value",
      max: 100,
      splitLine: {
        lineStyle: {
          type: "dashed",
          color: "#e9ecef",
        },
      },
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        fontSize: 12,
        color: "#999",
        formatter: "{value}%",
      },
    },
    series: [
      {
        data: [
          {
            value: data.value.repair_rate || 0,
            itemStyle: {
              color: "#579AFF",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: data.value.project_danger || 0,
            itemStyle: {
              color: "#DB48FF",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: data.value.impact_degree || 0,
            itemStyle: {
              color: "#8146FF",
              borderRadius: [10, 10, 10, 10],
            },
          },
        ],
        type: "bar",
        barWidth: "30%",
        barGap: "0%", // 保证柱子与背景的对齐
        label: {
          show: true,
          position: "top",
          fontSize: 14,
          fontWeight: "bold",
          color: "#project 3",
          formatter: "{c}%",
        },
      },
      {
        // 背景条形框
        type: "bar",
        barWidth: "40%",
        barGap: "-120%", // 和前景条留有距离
        data: [
          {
            value: 100,
            itemStyle: {
              color: "#F4F4F5",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: 100,
            itemStyle: {
              color: "#F4F4F5",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: 100,
            itemStyle: {
              color: "#F4F4F5",
              borderRadius: [10, 10, 10, 10],
            },
          },
        ],
        z: 1, // 设置图层为背景
      },
    ],
    tooltip: {
      trigger: "item",
      formatter: "{b}<br />{c}%",
    },
    barCategoryGap: "30%", // 保证每一组柱子之间的均匀间距
  };

  myChart.setOption(option);

  window.addEventListener("resize", () => {
    myChart.resize();
  });
}

// 请求数据
// onMounted(async () => {
//   await fetchData();
//     const response = await axios.get(`http://127.0.0.1:5000/get-overall-report`, {
//       params: {
//         pname: pname.value // 加入 pname 参数
//       }
//     });
//     const report = response.data.report;
//     console.log(report);
//     // 清理转义字符或多余的空格
//     const cleanedReport = report.replace(/\\n/g, '\n').replace(/\\r/g, '\r');
//     // 渲染成 HTML
//     const htmlContent = marked.marked(cleanedReport);
//     console.log(htmlContent);  // 查看渲染结果
//
//     // 插入渲染的 HTML 内容
//     const reportContent = document.querySelector('.report-content');
//     reportContent.innerHTML = htmlContent;  // 使用 innerHTML 插入 HTML
// });

const renderReport = async () => {
  const response = await axios.get(`http://127.0.0.1:5000/get-overall-report`, {
    params: {
      pname: pname.value // 加入 pname 参数
    }
  });
  let report = response.data.report;

  // 通过循环遍历 report 数组，处理每一行内容
  // const htmlContent = report.map(line => {
  //   // 处理 Markdown 或直接渲染到页面
  //   return marked(line);  // 这里使用 marked 将 Markdown 转换成 HTML
  // }).join('');  // 将所有行合并成一个字符串
  // console.log(report);
  report = report.replace(/\\n/g, '\n').replace(/\\r/g, '\r');
  report = report.replace(/\\\n/g, '\n').replace(/\\\r/g, '\r');
  report = report.replace(/\\"/g, '\"');
  // 显示报告内容
  document.querySelector('.report-content').innerHTML = '';
  document.querySelector('.report-content').innerHTML =  marked.parse(report);
}
onMounted(async () => {
  await fetchData();
  await renderReport();
});


const filters = ref({
  name: "",
  risk: "",
  vulnerabilityType: "",
});

const filteredFunctions = computed(() => {
  return functionOverview.value.filter((func) => {
    return (
        (!filters.value.name || func.name.includes(filters.value.name)) &&
        (!filters.value.risk || func.risk === filters.value.risk) &&
        (!filters.value.vulnerabilityType || func.vulnerabilityType === filters.value.vulnerabilityType)
    );
  });
});

const selectedFunction = ref(null); // 用于存储当前选中的函数

// 点击行时，展示函数的源代码
const selectFunction = async (func) => {
  console.log(func)
  const selected = functionOverview.value.find(f => f.id === func.id);
  console.log(selected.content)
  if (selected) {
    selectedFunction.value = selected; // 更新选中的函数信息
    console.log(selectedFunction.value.id)
    try {
      const response = await axios.get(`http://127.0.0.1:5000/get-overall-report`, {
        params: {
          pname: pname // 加入 pname 参数
        }
      });
      const report = response.data.report;
      // 显示报告内容
      document.getElementById("report-content").innerHTML = report;
    } catch (error) {
      console.error("获取检测报告失败", error);
    }
  }

};


watch(()=>route.params.id, async (new_id, old_id) => {
  console.log('pname changed', id.value, new_id);
  await fetchData();
  await renderReport();
})



const filterTable = () => {};
</script>

<style scoped>

#bar-chart {
  background-color: #fff;
  border-radius: 12px;

  padding: 10px;
}

.card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}






.icon {
  width: 40px;
  height: 40px;
  display: block;
}

/* 表头样式 */
.table-header {
  background-color: #f8f9fa;
  font-size: 0.95rem;
  font-weight: bold;
}

/* 表格样式 */
.table-custom tr:hover {
  background-color: #f1f3f5;
}

.table {
  margin-top: 10px;
}

.table th,
.table td {
  text-align: center;
  vertical-align: middle;
}



.indicator-item {
  display: flex;
  margin-right: 20px;
  align-items: center; /* 垂直居中 */
  justify-content: start; /* 水平对齐文字 */
  width: 200px;
}

.icon-container {
  background-color: #f5f5ff; /* 柔和背景色 */
  border-radius: 12px; /* 圆角 */
  padding: 10px; /* 内边距 */
  width: 50px; /* 固定宽度 */
  height: 50px; /* 固定高度 */
  display: flex;
  margin-right: 20px;
  align-items: center; /* 居中图标 */
  justify-content: center; /* 居中图标 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影 */
}

.icon {
  width: 50px; /* 固定宽度 */
  height: 50px; /* 固定高度 */
}

.text-container {
  text-align: left; /* 左对齐文字 */
}

.title {
  font-size: 1.5rem;
  font-weight: bold;

  color: #333;
  margin: 0;
}

.value {
  font-size: 0.8rem;
  font-weight: normal;
  color: #666;
  margin: 0;


}

/* 活动按钮样式 */
.btn.active {
  background-color: #007bff;
  color: white;
}

/* 内容区域的样式 */
.source-code-area,
.patch-area {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
}

.source-code-area {
  color: #333;
}

.patch-area {
  color: #333;
}

.text-danger {
  color: #dc3545;
}

.text-success {
  color: #28a745;
}

.nav-pills .nav-link {
  color: #6c757d;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: bold;
}

.nav-pills .nav-link.active {
  background-color: #CCB7FB;
  color: #fff;
  font-weight: bold;
}

.nav-pills .nav-link:hover {
  color: #8046FF;
}

.card {
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tab-content {
  margin-top: -10px;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.25rem;
  max-height: 180px;
  overflow-y: auto;
}
#report-content {
  height: 500px; /* 设置固定高度 */
  overflow-y: auto; /* 超出内容时显示垂直滚动条 */
  box-sizing: border-box; /* 包括内边距和边框在内的总高度 */
  margin-top: 10px;
}
#report-content pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  white-space: pre-wrap; /* 自动换行 */
  word-wrap: break-word;
}

#report-content code {
  font-family: 'Courier New', Courier, monospace;
}


</style>
