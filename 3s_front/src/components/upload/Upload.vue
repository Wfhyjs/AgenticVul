<template>
  <transition name="fade">
    <div class="loader-container" v-if="loading">
      <div class="loader-bar"></div>
    </div>
  </transition>
  <div class="col-12 container-xxl page-content">

    <div class="row row-up" >
      <div class="detect-content-wrapper">
        <!-- GitHub Upload Section -->
        <div class="col-md-4" style="width: 50%;">
          <div class="card mb-4 link-card">
            <h5 class="card-header">GitHub</h5>
            <div style="text-align: center; display: flex; justify-content: center; align-items: center; height: 100px;">
              <i class="bx bxl-github" style="font-size: 100px;"></i>
            </div>
            <div class="card-body demo-vertical-spacing demo-only-element">
              <form @submit.prevent="submitForm('git')">
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="Proname">项目名称</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bxs-file"></i></span>
                      <input
                          type="text"
                          class="form-control"
                          placeholder="Project Name"
                          v-model="form.Proname"
                          id="Proname"
                          name="Proname"
                      />
                    </div>
                  </div>
                </div>
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="basic-url1">仓库地址</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <span class="input-group-text">https://github.com/</span>
                      <input
                          type="text"
                          class="form-control"
                          placeholder="URL"
                          v-model="form.Pfilepath"
                          id="basic-url1"
                          name="Pfilepath"
                      />
                    </div>
                  </div>
                </div>
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="model">选择模型</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <select class="form-select" v-model="form.Pmodel" id="model" name="Pmodel">
                        <option value="ReGVD">ReGVD</option>
                        <option value="CodeBERT">CodeBERT</option>
                        <option value="GraphCodeBERT">GraphCodeBERT</option>
                        <option value="CodeT5">CodeT5</option>
                        <option value="Devign">Devign</option>
                        <option value="DFEVD">DFEPT</option>
                      </select>
                      <button class="btn btn-outline-primary" name="submit_button" value="file" type="submit">
                        上传！
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Local Upload Section -->
        <div class="col-md-4" style="width: 50%;">
          <div class="card mb-4 local-card">
            <h5 class="card-header">本地</h5>
            <div style="text-align: center; display: flex; justify-content: center; align-items: center; height: 100px;">
              <i class="bx bx-code-block" style="font-size: 100px;"></i>
            </div>
            <div class="card-body demo-vertical-spacing demo-only-element">
              <form @submit.prevent="submitForm('file')" enctype="multipart/form-data">
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="Proname2">项目名称</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bxs-file"></i></span>
                      <input
                          type="text"
                          class="form-control"
                          placeholder="Project Name"
                          v-model="form.Proname"
                          id="Proname2"
                          name="Proname"
                      />
                    </div>
                  </div>
                </div>
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="inputGroupFile01">上传项目(.zip)</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <label class="input-group-text" for="inputGroupFile01"><i class="bx bxs-file-archive"></i></label>
                      <input
                          type="file"
                          class="form-control"
                          id="inputGroupFile01"
                          name="uploaded_file"
                          accept=".zip,application/zip"
                          ref="fileInput"
                          @change="handleFileChange"
                      />
                    </div>
                  </div>
                </div>
                <div class="row mb-3">
                  <label class="col-sm-3 col-form-label" for="model2">选择模型</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <select class="form-select" v-model="form.Pmodel" id="model2" name="Pmodel">
                        <option value="ReGVD">ReGVD</option>
                        <option value="CodeBERT">CodeBERT</option>
                        <option value="GraphCodeBERT">GraphCodeBERT</option>
                        <option value="CodeT5">CodeT5</option>
                        <option value="Devign">Devign</option>
                        <option value="DFEVD">DFEPT</option>
                      </select>
                      <button class="btn btn-outline-primary" type="submit">
                        上传！
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="card" style="margin-top: 10px;">
      <h5 class="card-header">模型介绍</h5>
      <div class="table-responsive text-nowrap">
        <table class="table" style="text-align: center;">
          <colgroup>
            <col> <!-- 第一列（模型），使用默认宽度 -->
            <col style="width: 12%;"> <!-- 第二列（精度） -->
            <col style="width: 12%;"> <!-- 第三列（速度） -->
            <col> <!-- 第四列（推荐），使用默认宽度 -->
            <col> <!-- 第五列（类型），使用默认宽度 -->
            <col> <!-- 第六列（可解释），使用默认宽度 -->
          </colgroup>
          <thead>
          <tr>
            <th>模型</th>
            <th>精度</th>
            <th>速度</th>
            <th>推荐</th>
            <th>类型</th>
            <th>可解释</th>
          </tr>
          </thead>
          <tbody class="table-border-bottom-0">
          <tr class="table-warning">
            <td><i class="fab fa-sketch fa-lg text-warning me-3"></i> <strong>ReGVD</strong></td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 65%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 65%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-primary me-1">High</span></td>
            <td>
              GNN-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck2" disabled="" checked="">
            </td>
          </tr>
          <tr class="table-info">
            <td><i class="fab fa-react fa-lg text-info me-3"></i> <strong>CodeBERT</strong></td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 69%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>

            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 55%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-primary me-1">High</span></td>
            <td>
              Transformer-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck2" disabled="">
            </td>
          </tr>
          <tr class="table-primary">
            <td><i class="fab fa-angular fa-lg text-danger me-3"></i> <strong>GraphCodeBERT</strong></td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 60%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 45%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-info me-1">Medium</span></td>
            <td>
              Transformer-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck3" disabled="" checked>
            </td>
          </tr>
          <tr class="table-secondary">
            <td><i class="fab fa-vuejs fa-lg text-success me-3"></i> <strong>CodeT5</strong></td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 65%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 45%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-info me-1">Medium</span></td>
            <td>
              Transformer-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck4" disabled="">
            </td>
          </tr>
          <tr class="table-success">
            <td>
              <i class="fab fa-bootstrap fa-lg text-primary me-3"></i> <strong>Devign</strong>
            </td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 50%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 90%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-warning me-1">Low</span></td>
            <td>
              GNN-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck5" checked disabled="">
            </td>
          </tr>
          <tr class="table-danger">
            <td><i class="fab fa-sketch fa-lg text-warning me-3"></i> <strong>DFEPT</strong></td>
            <td>
              <div class="progress" style="margin: auto;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" role="progressbar" style="width: 70%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td>
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning" role="progressbar" style="width: 75%" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"></div>
              </div>
            </td>
            <td><span class="badge bg-label-danger me-1">Very High</span></td>
            <td>
              GNN-Based
            </td>
            <td>
              <input class="form-check-input" type="checkbox" value="" id="disabledCheck1" disabled="" checked>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Progress Section -->
<!--    <div class="row row-down">-->
<!--      <div class="col-md-12" style="width: 100%; height: 100%">-->
<!--        <div class="card detect-card">-->
<!--          <div class="d-flex align-items-center align-content-center justify-content-between">-->
<!--            <h5 class="card-header w-25">检测进度 <span class="text-primary">0%</span></h5>-->
<!--            <div class="px-4">-->
<!--              <button class="btn-primary btn rounded w-15" @click="startDetection">-->
<!--                开始检测-->
<!--              </button>-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="card-body body-container">-->
<!--            &lt;!&ndash; 进度条 &ndash;&gt;-->
<!--            <div class="progress">-->
<!--              <div-->
<!--                  class="progress-bar progress-bar-striped progress-bar-animated bg-primary"-->
<!--                  role="progressbar"-->
<!--                  style="width: 0%"-->
<!--                  aria-valuemin="0"-->
<!--                  aria-valuemax="100"-->
<!--              ></div>-->
<!--            </div>-->

<!--            &lt;!&ndash; 图表区域 &ndash;&gt;-->
<!--            <div class="row chart-report-container">-->

<!--              &lt;!&ndash; Chart Component &ndash;&gt;-->
<!--              <div class="line-chart-container">-->
<!--                <Chart />-->
<!--              </div>-->

<!--              &lt;!&ndash; Card Body &ndash;&gt;-->
<!--              <div class="card-body report-container">-->
<!--                <p>-->
<!--                  在您成功上传项目后，系统将自动生成并展示相应的项目报告。该报告会详细记录项目的各项数据，包括但不限于项目的整体情况、各项测试的结果分析以及项目在各个阶段的进展情况。报告内容将帮助您更好地理解项目的状态，并为后续的决策和优化提供有力的依据。-->
<!--                </p>-->
<!--                <p>-->
<!--                  项目报告不仅涵盖了基础的项目描述，还包括了详细的技术实现与难点分析。每一项测试数据都经过严谨的验证，确保报告中的信息准确可靠。此外，报告中还将提供一些建议和改进措施，帮助您优化项目的实施方案。-->
<!--                </p>-->
<!--                <p>-->
<!--                  上传的项目报告会实时更新，确保每次查看时，您都能看到最新的进展和数据。无论是检测结果、性能分析，还是项目进度，所有信息都会第一时间展现给您。通过这些数据，您可以及时发现问题并采取必要的措施，确保项目按计划顺利进行。-->
<!--                </p>-->
<!--                <p>-->
<!--                  如果报告中有任何异常或需要进一步解读的地方，您可以通过系统提供的反馈机制，向相关人员提出问题和建议。我们的团队会在第一时间处理您的反馈，帮助您解决遇到的困难，确保您能够顺利完成项目的后续工作。-->
<!--                </p>-->
<!--                <p>-->
<!--                  随着项目的不断推进，报告内容会根据项目的不同阶段进行更新和扩展。每一份报告都将在原有基础上加入最新的分析和结论，使您始终掌握项目的最新动态。-->
<!--                </p>-->
<!--                <p>-->
<!--                  项目报告将作为您管理和优化项目的重要工具，提供一个全面、清晰的数据展示平台。希望通过该报告的帮助，您能够在项目的每个环节中都做出明智的决策，推动项目向更高的目标迈进。-->
<!--                </p>-->
<!--                &lt;!&ndash; More paragraphs to trigger overflow &ndash;&gt;-->
<!--                <p>为了确保所有项目的报告都能够及时展示，系统将自动处理上传后的数据并生成报告，避免人工干预，确保每一份报告的高效生成与精准性。</p>-->
<!--                <p>每次报告更新后，您都可以在报告中查看到最新的测试结果和项目优化建议，这对于长期监控项目进度非常有帮助。</p>-->

<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->

  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import Chart from "@/components/upload/Chart.vue";

// 表单数据
const form = ref({
  Proname: '',
  Pfilepath: '',
  Pmodel: '',
  uploaded_file: null
});

// 加载状态
const loading = ref(false);

// 处理文件选择事件
const handleFileChange = event => {
  form.value.uploaded_file = event.target.files[0];
};

// 提交表单
const submitForm = async (submitType) => {
  try {
    const formData = new FormData();
    formData.append('Proname', form.value.Proname);
    formData.append('Pmodel', form.value.Pmodel);

    if (submitType === 'git') {
      formData.append('Pfilepath', form.value.Pfilepath);
      formData.append('submit_button', 'git');
    } else if (submitType === 'file') {
      formData.append('uploaded_file', form.value.uploaded_file);
      formData.append('submit_button', 'file');
    }

    loading.value = true;

    const token = localStorage.getItem('token');  // 假设 token 存储在 localStorage 中
    if (!token) {
      console.error('No token found. Please login first.');
      return;
    }
    const response = await axios.post('http://127.0.0.1:5000/uploadProject', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.status === 200) {
      alert(response.data.message);

      // 确保表单数据更新，设置上传的项目路径、模型等
      form.value.Pfilepath = response.data.project_path;  // 假设后端返回了项目路径
      form.value.Pmodel = response.data.model;  // 假设后端返回了选择的模型
      form.value.Proname = response.data.project_name;  // 假设后端返回了项目名称
      form.value.pid = response.data.pid;
    }
  } catch (error) {
    console.error('Error uploading project:', error);
    alert('上传失败，请重试！');
  } finally {
    loading.value = false;
  }
};

// 开始检测
const startDetection = async () => {
  // 先确保上传的项目已保存到数据库
  if (!form.value.Pfilepath || !form.value.Pmodel || !form.value.Proname) {
    alert("请先上传项目!");
    return;
  }

  loading.value = true;

  try {
    // 发送开始检测请求
    const token = localStorage.getItem('token');
    const response = await axios.post('http://127.0.0.1:5000/startDetection', {
      project_path: form.value.Pfilepath, // 项目路径
      Pmodel: form.value.Pmodel,         // 模型名称
      repo_name: form.value.Proname,      // 项目名称
      pid:form.value.pid
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
      alert('检测失败');
    }
  } catch (error) {
    console.error('Error starting detection:', error);
    alert('检测失败，请稍后再试');
  } finally {
    loading.value = false;
  }
};
</script>


<style scoped>
.loader-container {
  width: 100%;
  height: 4px;
  margin-top: 0.8%;
  position: relative;
}

.loader-bar {
  width: 10%;
  height: 100%;
  background-color: rgb(96, 91, 255);
  position: absolute;
  animation: slide 4s ease-in-out infinite;
}

@keyframes slide {
  from {
    left: -10%;
  }
  to {
    left: 100%;
  }
}

.row {
  display: flex;
  justify-content: space-between;
}

.chat-right .role-container {
  margin-left: 10px;
  margin-right: 0;
}

.chat-right .speech-bubble {
  background-color: #d0e6ff;
}

.body-container {
  padding-top: 0px;
  height: 80%;
}

.progress {
  margin-bottom: 30px;
}

.detect-content-wrapper {
  display: flex;
  flex-direction: row;
  margin-top: 5px;
  width: 100%;
  height: 100%;
}

.row-up {
  width: 100%;
  height: 38%;
  margin-bottom: 20px;
}

.row-down {
  width: calc(100% + 25px);
  height: 62%;
}

.detect-card {
  margin-top: 20px;
  width: 100%;
  height: 80%;
}

.chart-report-container {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 80%;
}

.line-chart-container {
  width: 60%;
  height: 100%;
}

.report-container {
  width: 40%;
  height: 100%;
  overflow-y: auto;
//margin-right: 18px;
  background-color: #f8f9fa;
  border-radius: 8px;
//padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.link-card {
  height: 100%;
}

.local-card {
  width: 100%;
  height: 100%;
  margin-left: 25px;
}

.page-content {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
