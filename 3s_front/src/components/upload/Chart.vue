<template>
  <div id="chart-container" className="chart-container"></div>
</template>

<script setup>
import {onMounted} from "vue";
import * as echarts from "echarts";

onMounted(() => {
  // 初始化 ECharts 实例
  const chart = echarts.init(document.getElementById("chart-container"));

  // 配置图表选项
  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "line", // 鼠标悬停时的指针样式
        lineStyle: {
          type: "dashed",
          color: "#d3d3d3",
          width: 1,
        },
      },
      backgroundColor: "#fff",
      borderColor: "#ccc",
      borderWidth: 1,
      padding: [10, 15],
      textStyle: {
        color: "#project 3",
        fontSize: 12,
      },
    },
    xAxis: {
      type: "category",
      data: ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"],
      axisLine: {
        show: true, // 显示 X 轴
        lineStyle: {
          color: "#ccc", // X轴线颜色
          width: 2,
        },
      },
      axisLabel: {
        color: "#project 3", // X轴标签颜色
      },
      axisTick: {
        show: false, // 去除 X 轴的刻度线
      },
      splitLine: {
        show: false, // 不显示 X 轴网格线
      },
    },
    yAxis: {
      type: "value",
      name: "数量",
      axisLine: {
        show: false, // 隐藏 Y 轴线
      },
      axisTick: {
        show: false, // 隐藏 Y 轴的刻度线
      },
      splitLine: {
        show: true, // 显示 Y 轴网格线
        lineStyle: {
          type: "dashed", // 虚线样式
          color: "#ddd", // 网格线颜色
        },
      },
    },
    grid: {
      left: "2%", // 左边距
      right: "2%", // 右边距
      bottom: "2%", // 底部边距
      top: "3%", // 上边距
      containLabel: true,
    },
    series: [
      {
        name: "SQL注入",
        type: "line",
        smooth: true, // 平滑曲线
        data: [2000, 4000, 6000, 8000, 7000, 5000, 4000, 6000, 7000, 8000],
        symbol: "none", // 不显示数据点
        areaStyle: {
          opacity: 0.2,
          color: "#CCB7FB",
        }, // 填充区域透明度
        lineStyle: {width: 4, color: "#8046FF"},
      },
      {
        name: "跨站脚本攻击",
        type: "line",
        smooth: true, // 平滑曲线
        data: [1000, 2000, 4000, 6000, 5000, 3000, 2000, 4000, 5000, 6000],
        symbol: "none", // 不显示数据点
        areaStyle: {
          opacity: 0.2,
          color: "#e4c1d8",
        }, // 填充区域透明度
        lineStyle: {width: 4, color: "#b395bd"},
      },
    ],
  };

  // 设置选项并渲染图表
  chart.setOption(option);

  // 窗口大小调整时自适应
  window.addEventListener("resize", () => {
    chart.resize();
  });
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%; /* 图表高度 */
  background-color: transparent;
  overflow: hidden; /* 防止内容溢出 */
}
</style>
