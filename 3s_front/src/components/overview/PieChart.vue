<template>
  <div class="chart-container">
    <canvas :id="chart" class="pie-chart"></canvas>
  </div>
</template>

<script setup>
//
//import {onMounted, ref, watch} from "vue";
//import * as echarts from "echarts";
//
//const props = defineProps({
//  data: {
//    type: Array,
//    required: true
//  }
//});
//console.log(props)
//const chart = ref(null);
//
//const initChart = (data) => {
//  const chartInstance = echarts.init(chart.value);
//
//  const option = {
//    tooltip: {
//      trigger: 'item'
//    },
//    series: [
//      {
//        name: '风险类型',
//        type: 'pie',
//        radius: '75%',
//        data: data.map(item => ({
//          name: item.name,
//          value: item.value
//        })),
//        emphasis: {
//          itemStyle: {
//            shadowBlur: 10,
//            shadowOffsetX: 0,
//            shadowColor: 'rgba(0, 0, 0, 0.5)'
//          }
//        }
//      }
//    ]
//  };
//
//  chartInstance.setOption(option);
//};
//
//onMounted(() => {
//  initChart(props.data);
//});
//
//watch(() => props.data, (newData) => {
//  if (chart.value) {
//    initChart(newData);
//  }
//});
import {computed, nextTick, onMounted, ref, watch} from "vue";
import * as echarts from "echarts";

const props = defineProps({
 data: {
   type: Array,
   required: true
 },
  chart: {
    type: String,
    default: 'pie-chart',
  },
});
const chart = ref(props.chart);
// 写死的静态数据，表示漏洞风险类型占比
const labels = ["高风险", "中风险", "低风险"]; // 风险类型的名称

const data = computed(()=>{
  if (props.data == null || props.data == undefined || props.data.length == 0) {
    return null;
  }
  return props.data.map(item => item.value);
})

function updateChart() {
  if (chart.value == null || chart.value == undefined) {
    console.error("chart.value is null");
    return;
  }
  console.log("开始创建", chart.value, data)
  const chartDom = document.getElementById(chart.value);
  const pieChart = echarts.init(chartDom);

  // 计算总值和最高值
  const total = data.value.reduce((sum, value) => sum + value, 0);
  const highestValue = Math.max(...data.value);
  const initialPercentage = ((highestValue / total) * 100).toFixed(1) + "%";

  // 配置图表选项
  const option = {
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)", // 鼠标悬停显示风险类型名称、值和占比
    },
    series: [
      {
        name: "漏洞风险占比",
        type: "pie",
        radius: ["70%", "90%"], // 环形饼图半径
        data: labels.map((label, index) => ({
          name: label,
          value: data.value[index],
        })),
        itemStyle: {
          borderColor: "#fff",
          borderWidth: 5,
        },
        label: {
          show: false, // 不显示单个标签
        },
        labelLine: {
          show: false,
        },
      },
    ],
    color: [
      "rgba(105,108,255,0.8)", // 涉赌颜色
      "#C2C3FF",  // 涉黄颜色
      "#5D43F9",   // 涉诈颜色

    ],
    graphic: {
      type: "group",
      left: "center",
      top: "center",
      children: [
        {
          type: "text",
          z: 100,
          left: "center",
          top: "center",
          style: {
            text: initialPercentage, // 显示最高占比
            fill: "#project 3",
            fontSize: 24,
            fontFamily: "Public Sans",
            fontWeight: "bold",
            textAlign: "center",
          },
        },
        {
          type: "text",
          z: 100,
          left: "center",
          top: 40,
          style: {
            text: "漏洞风险占比",
            fill: "#888",
            fontSize: 14,
            fontFamily: "Public Sans",
            textAlign: "center",
          },
        },
      ],
    },
  };

  // 初始化图表
  pieChart.setOption(option);

  // 自适应窗口大小
  window.addEventListener("resize", () => {
    pieChart.resize();
  });
}

onMounted(() => {
  nextTick(() => {
    if(data.value !== null && data.value !== undefined){
      updateChart();
    }
  });
});

// 监听 props.data 变化并更新图表
watch(
    () => data.value,
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
.chart-container {
  display: flex;
  justify-content: center;
  width: 100%; /* 容器宽度 */
  height: 100%; /* 容器高度 */
}

.pie-chart {
  //width: 100%; /* 与父容器匹配 */
  height: 95%;
}
</style>
