<template>
  <router-view></router-view>
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
                    <h6 class="value" v-if="selectedFunction">{{ selectedFunction.vulnerabilityType }}</h6>
                    <h6 class="value" v-else>暂无参数</h6>
                    <h5 class="title mb-1" v-if="selectedFunction">{{ selectedFunction.vulnerabilityType }}</h5>
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
                    <h5 class="title mb-1" v-if="selectedFunction">{{ selectedFunction.prob.toFixed(3) }}</h5>
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
<!--                <pre v-if="selectedFunction">{{ selectedFunction.content }}</pre>-->
                <Codemirror v-if="selectedFunction"
                    v-model:value="code"
                    :options="cmOptions"
                    placeholder="请选择一个函数查看源代码"
                    @ready="onReady"
                    :height="calculatedHeight"
                />
<!--                <p v-else>请选择一个函数查看源代码</p>-->
              </div>
              <div v-else class="tab-pane fade show active">
<!--                <div v-if="selectedFunction">-->
<!--                  <pre>-->
<!--                    <span v-for="(line, index) in patchLines" :key="index">-->
<!--                      <span v-bind:class="{'text-danger': line.startsWith('-'), 'text-success': line.startsWith('+')}">-->
<!--                      {{ line.trim()  }}-->
<!--                      </span>-->
<!--                    </span>-->
<!--                  </pre>-->
<!--                </div>-->
<!--                <p v-else>请选择一个函数查看补丁</p>-->
                <Codemirror v-if="selectedFunction"
                            v-model:value="code1"
                            :options="cmOptions"
                            placeholder="请选择一个函数查看补丁"
                            @ready="onReady"
                            :height="calculatedHeight"
                />
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
              <!-- 检测报告内容 -->
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
            <td>
              <button class="btn btn-primary btn-sm" @click.stop="showFixMessage(func)">修复</button>
            </td>
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
import { Edit, Delete, Download } from '@element-plus/icons-vue';
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
const code = ref('');  // 用户输入的代码
const code1 = ref('');
const onReady = (cm) => {
  cm.refresh()
};
const calculatedHeight = ref(0);


const route = useRoute();
const pname = computed(()=>{return route.params.pname}); // 接收 pid 参数
const id = computed(()=>{return route.params.id});
const file_path = computed(()=>{return route.params.file_path});
console.log(file_path)
const functionOverview = ref([]); // 存储函数概览数据


const activeTab = ref("code");

const switchTab = (tab) => {
  activeTab.value = tab;
};

// 将补丁内容按行拆分为数组
const patchLines = computed(() => {
//   const selectedFunction = ref({
//     patch: `- return t - TOK_ASM_d0;
// + if (t < TOK_ASM_d0 || t > TOK_ASM_d15) return -1;
// + return t - TOK_ASM_d0;
// - return t - TOK_ASM_s0;
// + if (t < TOK_ASM_s0 || t > TOK_ASM_s31) return -1;
// + return t - TOK_ASM_s0;`
//   });
  console.log(selectedFunction.value.patch)
  return selectedFunction.value.patch
      .split('\n')                   // 按行分割
      .filter(line => line.trim() !== '') // 去掉空行
      .map(line => line.trim());       // 去掉每行两端的空格
});

// 弹出修复成功的会话框
const showFixMessage = (func) => {
  alert('应用成功');
  // 你可以在这里添加更多的逻辑，例如更新函数的状态
  console.log('Fixed function:', func);
  code.value = 'static int asm_parse_vfp_regvar(int t, int double_precision)\n' +
      '{\n' +
      '    if (double_precision) {\n' +
      '        if (t >= TOK_ASM_d0 && t <= TOK_ASM_d15)\n' +
      '            if (t < TOK_ASM_d0 || t > TOK_ASM_d15) return -1;\n' +
      '        return t - TOK_ASM_d0;\n' +
      '    } else {\n' +
      '        if (t >= TOK_ASM_s0 && t <= TOK_ASM_s31)\n' +
      '            if (t < TOK_ASM_s0 || t > TOK_ASM_s31) return -1;\n' +
      '        return t - TOK_ASM_s0;\n' +
      '    }\n' +
      '    return -1;\n' +
      '}';
  code1.value = `diff -u /new/${selectedFunction.value.name} /new/${selectedFunction.value.name}\n函数无差异，无补丁`;
};

async function fetchData() {
  const file_path = route.params.file_path; // 获取路由参数中的 file_path

  await axios.get(`http://127.0.0.1:5000/get-json?pname=${pname.value}`)
      .then(response => {
        console.log('API response:', response.data);

        if (Array.isArray(response.data)) {
          // 过滤出符合 file_path 的数据
          const filteredData = response.data.filter(file => file.file_path === file_path);

          // 处理并生成所需格式的数据
          functionOverview.value = filteredData.flatMap((file, index) => {
            if (Array.isArray(file.defects)) {
              const ratesum = file.defects.map(defect => defect.defect_rate);
              const defect_rate = (ratesum.reduce((sum, rate) => sum + rate, 0) / ratesum.length * 100).toFixed(2);

              const repairsum = file.defects.map(defect => defect.repair_rate);
              const repair_rate = (repairsum.reduce((sum, rate) => sum + rate, 0) / repairsum.length * 100).toFixed(2);

              const impactsum = file.defects.map(defect => defect.impact_degree);
              const impact_degree = (impactsum.reduce((sum, rate) => sum + rate, 0) / impactsum.length * 100).toFixed(2);
              console.log(file.function_name)
              return {
                no: index + 1,
                name: file.function_name,
                vulnerabilities: file.defect_num,
                risk: file.avg_defect_level, // 假设是“低风险”或“高风险”
                vulnerabilityType: file.main_defect.CWE_id, // 假设这个字段存在
                content: file.function_content,
                id: file.function_id,
                patch: file.repairs.repair_patch,
                avgDefectRate: defect_rate,
                avgRepairRate: repair_rate,
                avgImpactDegree: impact_degree,
                prob: file.avg_defect_index,
                file_path: file.file_path // 保持 file_path 信息
              };
            }
            return null; // 如果 file.defects 不是一个数组，返回 null
          }).filter(file => file !== null); // 过滤掉 null 值

        } else {
          console.error("返回的 data 不是一个有效的数组");
        }
      })
      .catch(error => {
        console.error("加载文件数据失败", error);
      });

}

// 请求数据
onMounted(async () => {
  await fetchData();
  if (functionOverview.value.length > 0) {
    const firstFunction = functionOverview.value[0];
    selectedFunction.value = firstFunction;  // 默认选中第一个函数
    console.log('默认选中的函数：', firstFunction);
  }
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
    code.value = selectedFunction.value.content;
    code1.value = `diff -u /old/${selectedFunction.value.name} /new/${selectedFunction.value.name}\n${selectedFunction.value.patch}`;
    code1.value = `diff -u /old/${selectedFunction.value.name} /new/${selectedFunction.value.name}\nstatic int asm_parse_vfp_regvar(int t, int double_precision)
{
    if (double_precision) {
        if (t >= TOK_ASM_d0 && t <= TOK_ASM_d15)
@@ -5,1 +5,2 @@
-\treturn t - TOK_ASM_d0;
+      \tif (t < TOK_ASM_d0 || t > TOK_ASM_d15) return -1;
+      return t - TOK_ASM_d0;
    } else {
        if (t >= TOK_ASM_s0 && t <= TOK_ASM_s31)
@@ -8,1 +9,2 @@
-\treturn t - TOK_ASM_s0;
+      \tif (t < TOK_ASM_s0 || t > TOK_ASM_s31) return -1;
+      return t - TOK_ASM_s0;
    }
    return -1;
}`;
    console.log(selectedFunction.value.id)
    try {
      const response = await axios.get(`http://127.0.0.1:5000/get-report`, {
        params: {
          function_id: selectedFunction.value.id,
          pname: pname.value // 加入 pname 参数
        }
      });
      const report = response.data.report;
      // 显示报告内容
      document.getElementById("report-content").innerHTML = report;
    } catch (error) {
      console.error("获取检测报告失败", error);
    }
  }
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
            value: selected.avgRepairRate || 0,
            itemStyle: {
              color: "#579AFF",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: selected.avgDefectRate || 0,
            itemStyle: {
              color: "#DB48FF",
              borderRadius: [10, 10, 10, 10],
            },
          },
          {
            value: selected.avgImpactDegree || 0,
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
};


watch(()=>route.params.id, async (new_id, old_id) => {
  console.log('pname changed', id.value, new_id);
  await fetchData();
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
