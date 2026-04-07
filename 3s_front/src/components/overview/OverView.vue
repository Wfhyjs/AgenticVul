<template>
  <div class="container-xxl flex-grow-1 container-p-y">
    <div class="row h-100">

      <!-- Left Column: Project Overview Section -->
      <div class="col-8 col-lg-8 h-100">
        <div class="card p-3 h-100">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="m-0">项目总览</h5>
            <div>
              <input type="text" placeholder="筛选项目" class="form-control d-inline-block" style="width: auto;">
              <i class="bx bx-search ms-2" />
            </div>
          </div>
          <div class="table-responsive mt-3" style="overflow-y: auto; max-height: calc(100vh - 100px);">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>项目</th>
                  <th>漏洞类型</th>
                  <th>风险类型</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(project, idx) in filteredProjects" :key="project.id">
                  <td>
                    <div>
                      <i class="bx bx-folder-open" /> {{ project.name }}
                    </div>
                    <div class="info-container d-flex flex-column align-items-start mt-2">
                      <span class="badge bg-label-primary text-center w-100">{{ project.date }}</span>
                      <span class="badge bg-label-success text-center w-100">漏洞总数: {{ project.vul }}</span>
                      <span class="badge bg-label-warning text-center w-100">风险评分: {{ project.danger }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="chart-placeholder">
                      <RadarChart :data="project.radarData" :chart="`radar-chart-${idx}`" />
                    </div>
                  </td>
                  <td>
                    <div class="chart-placeholder">
                      <PieChart :data="project.pieData" :chart="`pie-chart-${idx}`"></PieChart>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column: Statistics Cards Section -->
      <div class="col-4 col-lg-4 h-100">
        <!-- Row 1: Two small cards -->
        <div class="row h-25">
          <div class="col-6" style="">
            <div class="card card-item p-3 text-center d-flex align-items-center">
              <div class="d-flex card-item-content">
                <div class="avatar flex-shrink-0 icon-item">
                  <img
                    src="/assets/img/icons/unicons/cc-primary.png"
                    alt="chart success"
                    class="rounded"
                    style="width: 40px; height: 40px;"
                  >
                </div>
                <div class="ms-3 text-start">
                  <h6>检测项目数量</h6>
                  <h3>{{ projectStats.projectCount }}</h3>
                  <small class="text-success"><i class="bx bx-up-arrow-alt" /> +38.5%</small>
                </div>
              </div>
            </div>
          </div>

          <div class="col-6" style="">
            <div class="card card-item p-3 text-center d-flex align-items-center">
              <div class="d-flex card-item-content">
                <div class="avatar flex-shrink-0 icon-item">
                  <img
                      src="/assets/img/icons/unicons/paypal.png"
                      alt="chart success"
                      class="rounded"
                      style="width: 40px; height: 40px;"
                  >
                </div>
                <div class="ms-3 text-start">
                  <h6>已识别漏洞数量</h6>
                  <h3 style="margin-bottom: 0px;">
                    {{ projectStats.totalVulns }}
                  </h3>
                  <span data-v-59d9f251="" class="badge bg-label-warning mt-2 no-style">
                    <i data-v-59d9f251="" class="bx bx-up-arrow-alt"/> +15.3%</span>

                  <div class="progress mt-3" style="height: 8px;">
                    <div
                      class="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                      role="progressbar"
                      style="width: 75%;"
                      aria-valuenow="75"
                      aria-valuemin="0"
                      aria-valuemax="100"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 2: Risk Distribution and Large Vulnerability Count -->
        <div class="row h-25">
          <div class="col-6" style="">
            <div class="card card-item p-3 text-center">
              <h6 style="margin-bottom: 5px">风险占比</h6>
              <div class="risk-chart-container">
                <!-- 图表容器 -->
                <div id="risk-chart" class="chart" style=""/>
              </div>
            </div>
          </div>

          <div class="col-6" style="">
            <div class="card card-item p-3 text-center d-flex align-items-center">
              <div class="d-flex card-item-content">
                <div class="avatar flex-shrink-0 icon-item">
                  <img
                    src="/assets/img/icons/unicons/chart-success.png"
                    alt="chart danger"
                    class="rounded"
                    style="width: 40px; height: 40px;"
                  >
                </div>
                <div class="ms-3 text-start">
                  <h6>已修复漏洞数量</h6>
                  <h3>{{ projectStats.totalFixed }}</h3>
                  <small class="text-danger"><i class="bx bx-down-arrow-alt" /> -13.4%</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 3: Bar Chart for Vulnerability Proportion -->
        <div class="row h-50">
          <div class="col-12">
            <div class="card h-100">
              <h6 class="card-header">
                漏洞占比
              </h6>
              <div class="card-body" style="">
                <div id="vulnerability-distribution-chart" />
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch, nextTick} from "vue";
import * as echarts from "echarts";
import RadarChart from "@/components/overview/RadarChart.vue";  // 引入雷达图组件
import PieChart from "@/components/overview/PieChart.vue";      // 引入饼状图组件
import axios from "axios";

const filterName = ref("");  // 用于项目筛选
const projects = ref([]);  // 存储用户的所有项目
const projectStats = ref({
  projectCount: 0,
  totalVulns: 0,
  totalFixed: 0,
  dangermedium: 0,
  dangerhigh: 0,
  dangerlow: 0,
});
const projectStats1 = ref({
  dangermedium: 0,
  dangerhigh: 0,
  dangerlow: 0,
});


watch(projectStats, (newVal) => {
  console.log("projectStats updated:", newVal);
});

// 获取token并查询项目数据

const fetchProjects = async () => {
  const token = localStorage.getItem("token");
  console.log(token);
  if (!token) {
    console.error("No token found");
    return;
  }

  try {
    const response = await axios.get("http://127.0.0.1:5000/projects", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params: {
        pname: filterName.value, // 项目名称过滤
      },
    });

    // Ensure that projectStats has valid data
    projectStats.value = {
      projectCount: response.data.project_count,
      totalVulns: response.data.total_vulns,
      totalFixed: response.data.total_fixed,
    };
    console.log(projectStats.value.dangermedium);

    // 设置项目数据
    projects.value = response.data.projects;

    // projects.value = response.data.projects.map((project) => ({
    //   ...project,
    //   radarData: [],
    //   pieData: [],
    // }));
    //
    // // 获取每个项目的雷达图和饼图数据
    // const projectNames = projects.value.map((project) => project.name);
    // const statsResponse = await axios.get("http://127.0.0.1:5000/get-number", {
    //   headers: {
    //     Authorization: `Bearer ${token}`,
    //   },
    //   params: {
    //     pname: projectNames.join(","),
    //   },
    // });
    //
    // projects.value = projects.value.map((project) => {
    //   const stats = statsResponse.data[project.name];
    //   if (stats && !stats.error) {
    //     return {
    //       ...project,
    //       radarData: stats.top_5_cwe_ids.map((item) => ({ name: item[0], value: item[1] })),
    //       pieData: [
    //         { name: "High", value: stats.defect_level_counts.high },
    //         { name: "Medium", value: stats.defect_level_counts.medium },
    //         { name: "Low", value: stats.defect_level_counts.low },
    //       ],
    //     };
    //   } else {
    //     return project;
    //   }
  //   });
 }
    catch (error) {
    console.error("Error fetching JSON data:", error);
  }
};

const fetchProjectData = async () => {
  const token = localStorage.getItem("token");
  console.log(token);
  if (!token) {
    console.error("No token found");
    return;
  }
  const projectNames = projects.value.map((project) => project.name);
  const statsResponse = await axios.get('http://127.0.0.1:5000/get-number', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    params: {
      pname: projectNames.join(','),
    },
  });

  // console.log('stats-before', statsResponse.data)
  projects.value = projects.value.map((project) => {
    const stats = statsResponse.data[project.name];
    // console.log('stats', stats)
    if (stats && !stats.error) {
      // console.log('stats-true', stats)
      return {
        ...project,
        radarData: stats.top_5_cwe_ids.map((item) => ({ name: item[0], value: item[1] })),
        pieData: [
          { name: 'High', value: stats.defect_level_counts.高风险},
          { name: 'Medium', value: stats.defect_level_counts.中风险 },
          { name: 'Low', value: stats.defect_level_counts.低风险 },
        ],
      };
    } else {
      return {
        ...project,
        radarData: [{
          name: 'CWE-未知1',
          value: 0,
        },{
          name: 'CWE-未知2',
          value: 0,
        },{
          name: 'CWE-未知3',
          value: 0,
        },{
          name: 'CWE-未知4',
          value: 0,
        },{
          name: 'CWE-未知5',
          value: 0,
        }],
        pieData: [
          { name: 'High', value: 0},
          { name: 'Medium', value: 0 },
          { name: 'Low', value: 0 },
        ],
      };
    }
  });
};

// 初始化饼图
const initPieChart = (idx) => {
    const chartDom = document.querySelector(`#pie-chart-${idx}`);
    // console.log(chartDom)
    if (chartDom && projects.value[idx]?.pieData) {
      const myChart = echarts.init(chartDom);
      const option = {
        title: {
          text: 'Defect Levels',
          subtext: 'Project Defects',
          left: 'center',
          show: false,
        },
        tooltip: {
          trigger: 'item',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          show: false,
        },
        series: [
          {
            name: 'Defect Level',
            type: 'pie',
            radius: '50%',
            data: projects.value[idx].pieData.map((item, index) => ({
              ...item,
              itemStyle: {
                color: getColor(index), // 根据index设置颜色
              },
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      };
      myChart.setOption(option);
    }
};
// 获取颜色的方法，可以根据需要自定义颜色
function getColor(index) {
  const colors = ['#DB48FF', '#579AFF', '#8146FF'];
  return colors[index % colors.length]; // 避免越界，循环使用颜色
}
// 在组件挂载时获取项目数据
onMounted(async () => {
  try {
    await fetchProjects();
    await fetchProjectData();
    // // 等待数据加载完成后初始化所有图
    // await nextTick(() => {
    //   if (filteredProjects.value && filteredProjects.value.length > 0) {
    //     filteredProjects.value.forEach((_, idx) => {
    //       initPieChart(idx);
    //     });
    //   }
    // })


    const chartDom = document.getElementById("risk-chart");
    const myChart = echarts.init(chartDom);
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found");
      return;
    }
    // 使用 `.value` 来访问解构后的响应式属性
    // const data = [
    //   { value: dangerhigh.value, name: "高风险", itemStyle: { color: "#DB48FF" } },
    //   { value: dangermedium.value, name: "中风险", itemStyle: { color: "#579AFF" } },
    //   { value: dangerlow.value, name: "低风险", itemStyle: { color: "#8146FF" } },
    // ];
    const response1 = await axios.get("http://127.0.0.1:5000/projects", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params: {
        pname: filterName.value, // 项目名称过滤
      },
    });

    // Ensure that projectStats has valid data
    projectStats1.value = {
      dangermedium: response1.data.danger_medium || 0,  // Ensure default values
      dangerhigh: response1.data.danger_high || 0,
      dangerlow: response1.data.danger_low || 0,
    };
    console.log(projectStats1.value.dangermedium);

    // Ensure that the data object is valid before rendering the chart
    const data = [
      { value: projectStats1.value.dangerhigh, name: "高风险", itemStyle: { color: "#DB48FF" } },
      { value: projectStats1.value.dangermedium, name: "中风险", itemStyle: { color: "#579AFF" } },
      { value: projectStats1.value.dangerlow, name: "低风险", itemStyle: { color: "#8146FF" } },
    ];
    // 计算初始最高占比
    const total = data.reduce((sum, item) => sum + item.value, 0);
    console.log(total)
    const highestValue = Math.max(...data.map((item) => item.value));
    const initialPercentage = ((highestValue / total) * 100).toFixed(1) + "%";
    const option1 = {
      tooltip: {
        trigger: "item",
        formatter: "{b}: {c} ({d}%)",
      },
      grid: {
        left: "0%",
        right: "0%",
        bottom: "0%",
        top: "0%",
        // containLabel: true,
      },
      series: [
        {
          name: "风险分布",
          type: "pie",
          radius: ["70%", "90%"], // 圆环的内外半径
          avoidLabelOverlap: false,
          label: {
            show: false, // 不显示标签
          },
          labelLine: {
            show: false, // 不显示连接线
          },
          data: data.map((item) => ({
            ...item,
            itemStyle: {
              ...item.itemStyle,
              borderWidth: 2, // 设置边框宽度，形成间隙
              borderColor: "#fff", // 边框颜色为白色
            },
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.5)",
            },
          },
        },
      ],
      graphic: {
        // 图表中间的动态文字
        type: "text",
        left: "center",
        top: "center",
        style: {
          text: initialPercentage, // 初始显示最高占比
          textAlign: "center",
          fill: "#project 3", // 字体颜色
          fontSize: 18,
          fontWeight: "bold",
        },
      },
    };

    myChart.setOption(option1);

    // 更新中间百分比显示
    myChart.on("mouseover", (params) => {
      const percentage = params.percent ? params.percent.toFixed(1) + "%" : "0.0%";
      myChart.setOption({
        graphic: {
          style: {
            text: percentage,
          },
        },
      });
    });

    // 恢复为最高占比
    myChart.on("mouseout", () => {
      myChart.setOption({
        graphic: {
          style: {
            text: initialPercentage,
          },
        },
      });
    });

    window.addEventListener("resize", () => {
      myChart.resize();
    });


    //饼图：用于显示所有项目中出现最频繁的
    //柱状图：用于所有项目中显示最频繁出现的8个CWE-ID类型的数据（类型+数量）
    const chartDom1 = document.getElementById("vulnerability-distribution-chart");
    const myChart1 = echarts.init(chartDom1);
    const response = await axios.get("http://127.0.0.1:5000/get-vulnerability-stats", {
      headers: {
        Authorization: `Bearer ${token}`,  // Send token in Authorization header
      },
    });

    const cweStats = response.data.cwe_stats;
    const cweIds = cweStats.map(item => item[0]);  // Extract CWE_id
    const counts = cweStats.map(item => item[1]);  // Extract counts

    // Chart option configuration
    const option = {
      tooltip: {
        trigger: "item",
        formatter: "{b}: {c} 个",
        backgroundColor: "#8046FF",
        textStyle: {
          color: "#fff",
        },
      },
      xAxis: {
        type: "category",
        data: cweIds,  // Use the CWE_ids as categories
        axisLine: {show: false},
        axisTick: {show: false},
        axisLabel: {show: true},
      },
      yAxis: {
        type: "value",
        splitLine: {
          lineStyle: {
            type: "dashed",
            color: "#E0E0E0",
          },
        },
        axisLine: {show: false},
        axisTick: {show: false},
      },
      series: [
        {
          data: counts,  // Use the counts as the data for the bars
          type: "bar",
          itemStyle: {
            color: function (params) {
              return params.dataIndex === 2 ? "#8046FF" : "#CCB7FB";  // Highlight one bar (optional)
            },
            borderRadius: [5, 5, 0, 0],
          },
          emphasis: {
            itemStyle: {
              color: "#8046FF",
            },
          },
          label: {
            show: true,
            position: "top",
            color: "#8046FF",
          },
        },
      ],
      grid: {
        left: "2%",
        right: "2%",
        bottom: "2%",
        top: "3%",
        containLabel: true,
      },
    };

    // Set the option to update the chart
    myChart1.setOption(option);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});

// 计算筛选后的项目数据
const filteredProjects = computed(() => {
  return projects.value.filter((project) =>
      project.name.includes(filterName.value)
  );
});


</script>

<style scoped>
.small-text {
  font-size: 0.8rem;
}

.card.p-2 {
  padding: 0.5rem;
}

.pie-chart-placeholder,
.bar-chart-placeholder,
.compact-placeholder {
  height: 300px;
  background-color: #fff;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mb-3 {
  margin-bottom: 0.5rem !important;
}

#vulnerability-distribution-chart {
  width: 100%;
  height: 100%;
  //min-height: 300px;
}

/* 表格容器设置 */
.table-responsive {
  overflow-y: auto;
  max-height: calc(100vh - 100px); /* 限制表格高度 */
}

/* 表格样式 */
table {
  table-layout: fixed; /* 固定布局 */
  width: 100%; /* 占满容器宽度 */
  border-collapse: collapse; /* 合并单元格边框 */
}

table th,
table td {
  text-align: center; /* 水平居中 */
  vertical-align: middle; /* 垂直居中 */
  width: 33.33%; /* 等分为三列 */
}

/* 雷达图与饼状图居中样式 */
.chart-placeholder {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 150px; /* 固定高度，防止撑开 */
}

.radar-chart-placeholder,
.pie-chart-placeholder {
  width: 100%; /* 充满父容器宽度 */
  height: 150px; /* 固定高度，避免溢出 */
}


.info-container {
  display: flex;
  flex-direction: column; /* 垂直排列 */
  gap: 10px; /* 设置间距 */
}

.badge {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  padding: 10px 0; /* 上下内边距 */
  width: 100%; /* 占满父容器宽度 */
  font-size: 0.9rem; /* 调整文字大小，根据需要修改 */
}

.no-style {
  all: unset; /* 移除所有样式 */
  display: inline-block; /* 恢复正常布局 */
  border-radius: 5px;
}

.no-style .bx {
  font-size: inherit; /* 恢复内部图标样式 */
}

.risk-chart-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

#risk-chart {
  width: 100%;
  height: 100%;
}

.card-item {
  height: 85%;
}

.icon-item {
  margin-top: 18%;
}

.card-item-content {

}
</style>
