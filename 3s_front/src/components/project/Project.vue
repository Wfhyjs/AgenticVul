<template>
  <div class="container py-4">
    <div class="card table-responsive table-custom">
      <table class="table">
        <thead class="table-header">
        <tr>
          <th scope="col" class="text-center">项目名</th>
          <th scope="col" class="text-center">检测日期</th>
          <th scope="col" class="text-center">文件数量</th>
          <th scope="col" class="text-center">函数数量</th>
          <th scope="col" class="text-center">修复进度</th>
          <th scope="col" class="text-center">操作</th>
          <th scope="col" class="text-center">风险评分</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(project, index) in projectData" :key="index" class="table-row">
          <!-- 项目名称列 -->
          <td class="text-center">
            <div class="d-flex align-items-center" style="margin-left: 12%">
              <img src="/assets/img/icons/unicons/cc-primary.png" alt="Project Icon" class="project-icon me-2" />
              <span>{{ project.name }}</span>
            </div>
          </td>

          <!-- 检测日期列 -->
          <td class="text-center">{{ project.date }}</td>

          <!-- 文件数量列 -->
          <td class="text-center">{{ project.fileCount }}</td>

          <!-- 函数数量列 -->
          <td class="text-center">{{ project.functionCount }}</td>

          <!-- 检测进度列 -->
          <td class="text-center">
            <div class="progress">
              <div
                  class="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                  role="progressbar"
                  :style="{ width: progress(project) + '%' }"
                  :aria-valuenow="progress(project)"
                  aria-valuemin="0"
                  aria-valuemax="100"
              ></div>
            </div>
          </td>

          <!-- 操作列 -->
          <td class="text-center">
            <button
                class="btn btn-outline-primary btn-sm me-1"
                @click="goToProjectDetail(project.id)">
              <i class="bi bi-file-earmark-text"></i>
            </button>
            <button class="btn btn-outline-warning btn-sm me-1"
                    @click="startDetection(project)">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-outline-danger btn-sm me-1"
                    @click="deleteProject(project.id)">
              <i class="bi bi-trash"></i>
            </button>
            <button class="btn btn-outline-info btn-sm"
                    @click="downloadFile(project.id)">
              <i class="bi bi-download"></i>
            </button>
          </td>

          <!-- 风险评分列 -->
          <td class="text-center">
            <span v-if="project.risk === '安全'" class="badge badge-light-success">安全</span>
            <span v-else-if="project.risk === '危险'" class="badge badge-light-danger">危险</span>
            <span v-else class="badge badge-light-secondary">未检测</span>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const projectData = ref([]);
// 获取当前用户的 ID
const token = localStorage.getItem('token');

// 请求项目数据
const fetchProjectData = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/getProjectData',{
      headers: { Authorization: `Bearer ${token}` }});
    projectData.value = response.data;
    // response.data.forEach(project => {
    //   projectData.value.push(project);
    // })
    // response.data.forEach(project => {
    //   projectData.value.push(project);
    // })
    // response.data.forEach(project => {
    //   projectData.value.push(project);
    // })
  } catch (error) {
    console.error("Error fetching project data:", error);
  }
};
// 计算进度
const progress = (project) => {
  const Pvul = project.Pvul || 0; // 如果没有数据，默认值为 0
  const Pfix = project.Pfix || 0;
  const total = Pvul + Pfix;

  return total === 0 ? 0 : (Pfix / total) * 100; // 避免除以 0 的错误
};

// 页面加载时获取项目数据
onMounted(fetchProjectData);

// 跳转到项目详情页面
const goToProjectDetail =async  (id) => {
  const project = projectData.value.find(project => project.id === id);
  const pname = project.name;
  console.log(pname)
  if (project && project.status === '未检测') {
    alert('请先进行检测');
  } else {
    await router.push({name: "ProjectOverview", params: { id: id, pname: pname,file_path:pname }});
  }
};

// 删除项目
const deleteProject = async (id) => {
  try {
    const response = await axios.delete(`http://127.0.0.1:5000/deleteProject/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.status === 200) {
      alert('项目已删除');
      // 删除项目后重新获取数据
      await fetchProjectData();
    } else {
      alert('删除失败');
    }
  } catch (error) {
    console.error("Error deleting project:", error);
    alert('删除失败');
  }
};

//下载修复后文件
const downloadFile = async (id) => {
  const project = projectData.value.find(project => project.id === id);
  const pname = project.name;

  // 构建文件名，例如 'project 8(修复后).zip'
  const filename = `${pname}(修复后).zip`;

  try {
    // 发送 GET 请求，请求下载文件
    const response = await axios({
      url: `/download/${encodeURIComponent(filename)}`, // 使用 encodeURIComponent 确保文件名正确传输
      method: 'GET',
      responseType: 'blob', // 使得响应以 blob 格式返回
    });

    // 创建一个下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename); // 设置下载的文件名
    document.body.appendChild(link);
    link.click();

    // 清理链接
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('下载文件失败:', error);
  }
};

// 启动检测
const startDetection = async (project) => {
  alert('开始检测，请耐心等候');
  console.log(project);
  const token = localStorage.getItem('token');
  try {
    const response = await axios.post('http://127.0.0.1:5000/startDetection', {
      project_path: project.Pfilepath,
      Pmodel: project.Pmodel,
      repo_name: project.name,
      pid:project.id
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    if (response.status === 200) {
      //alert('检测已开始');
      // 在这里你可以更新进度条等UI反馈
      alert('检测成功');
    } else {
      alert('检测成功');
    }
  } catch (error) {
    console.error('Error starting detection:', error);
    alert('检测成功');
  }
};

</script>


<style scoped>
.container {
  width: 100%;
  height: 100%;
}
/* 给最外层表格容器添加圆角 */
.table-responsive.table-custom {
//border-radius: 8px; /* 添加圆角 */
  overflow: auto; /* 确保内容不溢出 */
  height: 80vh;
}

/* 表格整体样式去掉边框和竖线 */
.table {
  border-collapse: collapse; /* 去掉表格的竖线 */
  width: 100%;
  background-color: #fff;
}

/* 表头样式，背景为浅灰色 */
.table-header {
  background-color: #fff;
  font-weight: bold;
  color: #333;
  position: sticky;
  top: 0;
}

/* 表体行的背景色，统一浅白色 */
.table-row {
  background-color: #fff;
}

/* 移除表格单元格的边框 */
.table td,
.table th {
  border: none; /* 去掉单元格边框 */
}

/* 项目图标样式 */
.project-icon {
  width: 30px;
  height: 30px;
  border-radius: 4px;
}

/* 自定义操作按钮的样式 */
.btn-outline-primary {
  color: #7367f0;
  border-color: #7367f0;
}

.btn-outline-warning {
  color: #7367f0;
  border-color: #7367f0;
}

.btn-outline-danger {
  color: #ea5455;
  border-color: #ea5455;
}

/* 自定义风险标签样式 */
.badge-light-success {
  background-color: #d4edda;
  color: #28a745;
}

.badge-light-danger {
  background-color: #f8d7da;
  color: #dc3545;
}

.badge-light-secondary {
  background-color: #e2e3e5;
  color: #6c757d;
}
.btn-outline-download{
  color: #1939d9;
  background-color: #ffffff;
  border-color: #1939d9;

}
</style>
