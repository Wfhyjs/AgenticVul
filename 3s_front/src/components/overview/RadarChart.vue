<template>
  <div class="chart-container">
    <canvas :id="chart" class="radar-chart"></canvas>
  </div>
</template>

<script setup>
import {computed, nextTick, onMounted, ref, watch} from "vue";
import { Chart } from "chart.js";
import { RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip } from "chart.js";

// 注册必要的组件和插件
Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip);

const props = defineProps({
  data: {
    type: Array,
    required: true,
  },
  chart: {
    type: String,
    default: 'chart',
  },
});


const chart = ref(props.chart)
// console.log(chart.value)
let chartInstance = null;

const updateChart = () => {
  if (chart.value == null || chart.value == undefined) {
    console.error("chart.value is null");
    return;
  }
  // console.log("开始创建", chart.value, props.data)
  // console.log(props.data.map(item => item.name))
  chartInstance = new Chart(document.getElementById(chart.value), {
    type: 'radar',
    data: {
      labels: props.data.map(item => item.name), // 雷达图的指标名称
      datasets: [
        {
          label: '漏洞类型分布', // 数据集标签
          data: props.data.map(item => item.value), // 雷达图的值
          fill: true,
          backgroundColor: 'rgba(204, 183, 251, 0.5)', // 填充颜色
          borderColor: '#8046FF', // 边框颜色
          borderWidth: 2, // 边框宽度
          pointRadius: 0, // 隐藏点
        },
      ],
    },
    options: {
      responsive: true, // 使图表在容器大小变化时自动调整
      maintainAspectRatio: false, // 确保图表按容器比例调整
      scales: {
        r: {
          angleLines: {
            display: true, // 是否显示角度线
          },
          pointLabels: {
            display: false, // 隐藏五个角的文字
          },
          suggestedMin: 0,
          suggestedMax: 20, // 设置最大值
        },
      },
      plugins: {
        legend: {
          display: false, // 隐藏图例
        },
        tooltip: {
          enabled: true, // 启用提示工具
          mode: 'nearest', // 鼠标附近显示提示
          callbacks: {
            label: function (context) {
              // 返回悬停时显示的内容
              const label = context.label || '';
              const value = context.raw;
              return `${label}: ${value}`;
            },
          },
        },
        filler: {
          propagate: true, // 使提示工具能在覆盖区域内触发
        },
      },
      hover: {
        mode: 'nearest', // 鼠标悬停模式
        intersect: false, // 允许触发覆盖区域
      },
    },
  });
  // console.log("结束")
}

onMounted(() => {
  nextTick(() => {
    if(props.data !== null && props.data !== undefined){
      updateChart();
    }
  });
});

// 监听 props.data 变化并更新图表
watch(
    () => props.data,
    (newData) => {
      if (newData !== null && newData !== undefined) {
        // chartInstance.data.labels = newData.map(item => item.name);
        // chartInstance.data.datasets[0].data = newData.map(item => item.value);
        // chartInstance.update(); // 更新图表
        nextTick(()=>{
          updateChart();
        })
      }
    },
);
</script>

<style scoped>
/* 图表容器样式 */
.chart-container {
  display: flex;
  justify-content: center; /* 水平居中 */
  width: 180px; /* 容器宽度 */
  height: 180px; /* 容器高度 */
  margin-top: 20px;
}

.radar-chart {
  width: 100%; /* 图表宽度适配容器 */
  height: 100%; /* 图表高度适配容器 */
}
</style>
