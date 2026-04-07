<script setup>
import {ref, onMounted, handleError} from "vue";
import axios from "axios";
axios.defaults.withCredentials = true; // 启用跨域请求时携带 cookies

const user = ref({});


// 修改密码
const old_password = ref('');
const password = ref('');
const confirm_password = ref('');

onMounted(() => {
  const storedUserInfo = sessionStorage.getItem('userInfo');
  if (storedUserInfo) {
    user.value = JSON.parse(storedUserInfo);
  } else {
    alert('未登录，请先登录');
    window.location.href = '/login'; // 跳转到登录页面
  }
});

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    // Display the selected file's preview (optional)
    user.value.UFacePath = URL.createObjectURL(file);
  } else {
    console.error('No file selected.');
    alert('请选择一个文件上传');
  }
};


const saveProfile = async () => {
  try {
    const token = localStorage.getItem('token');

    if (!token) {
      console.error('No token found. Please login first.');
      return;
    }
    const response = await axios.post('http://127.0.0.1:5000/profile/update', {
      firstName: user.value.UFirstName,
      lastName: user.value.ULastName,
      email: user.value.Uemail,
      organization: user.value.Uorgnization,
      phone: user.value.Uphone,
      position: user.value.Uposition,
    }, {
      headers: { Authorization: `Bearer ${token}` }});
    if (response.status === 200) {
      alert('信息已更新');
    } else {
      alert(`更新失败：${response.data.msg}`);
    }
  } catch (error) {
    console.error('更新失败：', error);
    alert('更新失败，请稍后重试');
  }
};

const changPassword = async () => {
  if (password.value !== confirm_password.value) {
    alert('两次输入的密码不一致！');
    return;
  }
  try {
    const token = localStorage.getItem('token');

    if (!token) {
      console.error('No token found. Please login first.');
      return;
    }
    const response = await axios.post(
        'http://127.0.0.1:5000/profile/change_password',
        {
          old_password: old_password.value,
          password: password.value,
        },  {
          headers: { Authorization: `Bearer ${token}` }
        }// 确保请求携带会话 cookies
    );
    if (response.status === 200) {
      alert('密码修改成功，请重新登录');
      sessionStorage.clear();
      window.location.href = '/login';
    } else {
      alert(`密码修改失败：${response.data.msg}`);
    }
  } catch (error) {
    console.error('密码修改失败：', error);
    alert('修改密码失败，请稍后重试');
  }
};


const deleteAccount = async () => {
  try {
    const token = localStorage.getItem('token');

    if (!token) {
      console.error('No token found. Please login first.');
      return;
    }
    const response = await axios.post('http://127.0.0.1:5000/profile/delete',{
      headers: { Authorization: `Bearer ${token}` }});
    if (response.status === 200) {
      alert('账户已删除');
      sessionStorage.clear();
      window.location.href = '/login';
    } else {
      alert(`删除失败：${response.data.msg}`);
    }
  } catch (error) {
    console.error('删除失败：', error);
    alert('删除账户失败，请稍后重试');
  }
};

const upgradePhoto = async (event) => {
  // Check if a file is selected before submitting the form
  const file = document.getElementById('upload').files[0];
  if (!file) {
    console.error('No files selected.');
    alert('请选择一个文件上传');
    return;
  }

  const formData = new FormData();
  formData.append('upload', file);

  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token found. Please login first.');
      alert('请先登录');
      return;
    }

    // Send the request without manually setting the Content-Type
    const response = await axios.post('http://127.0.0.1:5000/profile/upload_photo', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      user.value.UFacePath = response.data.url;
      alert('头像已更新');
    } else {
      alert(`上传头像失败：${response.data.msg}`);
    }
  } catch (error) {
    console.error('上传头像失败：', error);
    alert('上传头像失败，请稍后重试');
  }
};



import { createApp } from 'vue';

// createApp({
//   data() {
//     return {
//       currentAvatar: '/static/photo/default-avatar.jpg',
//       selectedFile: null,
//     };
//   },
//   methods: {
//     handleFileUpload(event) {
//       const file = event.target.files[0];
//       if (file) {
//         this.selectedFile = file;
//         this.currentAvatar = URL.createObjectURL(file);
//       }
//     },
//     async upgradePhoto() {
//       if (!this.selectedFile) {
//         alert('请先选择一个头像文件');
//         return;
//       }
//
//       const formData = new FormData();
//       formData.append('upload', this.selectedFile);
//
//       try {
//         const response = await axios.post('http://127.0.0.1:5000/profile/upload_photo', formData, {
//           headers: {
//             'Content-Type': 'multipart/form-data',
//             Authorization: `Bearer ${localStorage.getItem('token')}`
//           }
//         });
//
//         if (response.status === 200) {
//           this.currentAvatar = response.data.url;
//           alert('头像已更新');
//         } else {
//           alert('头像上传失败，请重试');
//         }
//       } catch (error) {
//         console.error('上传头像失败:', error);
//         alert('上传头像失败，请稍后重试');
//       }
//     }
//   }
// }).mount('#app');

// const upgradePhoto = async (event) => {
//   // Check if a file is selected before submitting the form
//   const file = document.getElementById('upload').files[0];
//
//   if (!file) {
//     console.error('No files selected.');
//     alert('请选择一个文件上传');
//     return;
//   }
//
//   const formData = new FormData();
//   formData.append('upload', file);
//
//   try {
//     const token = localStorage.getItem('token');
//     if (!token) {
//       console.error('No token found. Please login first.');
//       alert('请先登录');
//       return;
//     }
//
//     // Send the request without manually setting the Content-Type
//     const response = await axios.post('http://127.0.0.1:5000/profile/upload_photo', formData, {
//       headers: {
//         'Authorization': `Bearer ${token}`,
//       },
//     });
//
//     if (response.status === 200) {
//       user.value.UFacePath = response.data.url;
//       alert('头像已更新');
//     } else {
//       alert(`上传头像失败：${response.data.msg}`);
//     }
//   } catch (error) {
//     console.error('上传头像失败：', error);
//     alert('上传头像失败，请稍后重试');
//   }
// };

</script>

<template>
  <!-- Content -->

  <div class="container-xxl flex-grow-1 container-p-y" style="height: 100%;">

    <div class="row" style="height: 100%">
      <div class="col-md-12" style="height: 100%">
        <ul class="nav nav-pills flex-column flex-md-row mb-3">
          <li class="nav-item">
            <a class="nav-link active" href="javascript:void(0);">
              <i class="bx bx-user me-1"></i> 账户
            </a>
          </li>
        </ul>
        <div class="card mb-4">
          <h5 class="card-header">详细信息</h5>
          <!-- Account -->
          <div class="card-body">
            <div class="d-flex align-items-start align-items-sm-center gap-4">
              <img
                  :src="user.UFacePath==''?user.UFacePath:'/assets/photo/default.png'"
                  alt=""
                  class="d-block rounded"
                  height="100"
                  width="100"
                  id="uploadedAvatar"
              />
              <div class="button-wrapper">
                <form method="POST" @submit.prevent="upgradePhoto"
                      enctype="multipart/form-data" id="uploadForm">
                  <label for="upload" class="btn btn-primary me-2 mb-4" tabindex="0">
                    <span class="d-none d-sm-block">上传新头像</span>
                    <i class="bx bx-upload d-block d-sm-none"></i>
                    <input
                        type="file"
                        id="upload"
                        class="account-file-input"
                        name="upload"
                        hidden
                        accept="image/png, image/jpeg"
                        @change="handleFileUpload"
                    />
                  </label>

                  <button type="submit"
                          class="btn btn-outline-secondary account-image-reset mb-4">
                    <i class="bx bx-reset d-block d-sm-none"></i>
                    <span class="d-none d-sm-block">保存头像</span>
                  </button>
                </form>
                <p class="text-muted mb-0">仅支持上传JPG或PNG格式的图片.</p>
              </div>
            </div>
          </div>
          <hr class="my-0"/>
          <div class="card-body">
            <form id="formAccountSettings" method="POST" @submit.prevent="saveProfile">
              <div class="row">
                <div class="mb-3 col-md-6">
                  <label for="firstName" class="form-label">姓</label>
                  <input
                      class="form-control"
                      type="text"
                      id="firstName"
                      name="firstName"
                      v-model="user.UFirstName"
                      autofocus
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label for="lastName" class="form-label">名</label>
                  <input class="form-control" type="text" name="lastName" id="lastName"
                         v-model="user.ULastName"/>
                </div>
                <div class="mb-3 col-md-6">
                  <label for="email" class="form-label">邮箱地址</label>
                  <input
                      class="form-control"
                      type="text"
                      id="email"
                      name="email"
                      v-model="user.Uemail"
                      placeholder="john.doe@example.com"
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label for="organization" class="form-label">组织</label>
                  <input
                      type="text"
                      class="form-control"
                      id="organization"
                      name="organization"
                      v-model="user.Uorgnization"
                  />
                </div>
                <div class="mb-3 col-md-6">
                  <label class="form-label" for="phoneNumber">手机</label>
                  <div class="input-group input-group-merge">
                    <span class="input-group-text">China (+86)</span>
                    <input
                        type="text"
                        id="phoneNumber"
                        name="phoneNumber"
                        class="form-control"
                        placeholder="Phone Number"
                        v-model="user.Uphone"
                    />
                  </div>
                </div>
                <div class="mb-3 col-md-6">
                  <label for="address" class="form-label">职位</label>
                  <input type="text" class="form-control" id="address" name="address"
                         placeholder="Address" v-model="user.Uposition"/>
                </div>

              </div>
              <div class="mt-2">
                <button type="submit" class="btn btn-primary me-2">保存修改</button>
              </div>
            </form>
          </div>
          <!-- /Account -->
        </div>
        <div class="card mb-4">
          <div class="card">
            <h5 class="card-header">修改密码</h5>
            <div class="card-body">
              <form id="changepassword" @submit.prevent="changPassword" method="post">
                <div class="mb-3 col-12 mb-0">
                  <div class="mb-3 col-md-12">
                    <label for="old_password" class="form-label">请输入当前密码</label>
                    <input type="password" class="form-control" id="old_password"
                           v-model="old_password" placeholder="*********"/>
                  </div>
                  <div class="mb-3 col-md-12">
                    <label for="password" class="form-label">输入新密码</label>
                    <input class="form-control" type="password" id="password"
                           v-model="password" placeholder="**********"/>
                  </div>
                  <div class="mb-3 col-md-12">
                    <label for="confirm-password"
                           class="form-label">再次输入新密码</label>
                    <input class="form-control" type="password" id="confirm-password"
                           v-model="confirm_password" placeholder="**********"/>
                  </div>
                </div>

                <button type="submit" class="btn btn-primary me-2" id="changePasswordBtn">
                  确认修改
                </button>
              </form>
            </div>
          </div>
        </div>


        <div class="card">
          <h5 class="card-header">删除账户</h5>
          <div class="card-body">
            <div class="mb-3 col-12 mb-0">
              <div class="alert alert-warning">
                <h6 class="alert-heading fw-bold mb-1">您确定要删除此账户吗？</h6>
                <p class="mb-0">注意！此操作无法更改，请您慎重考虑！</p>
              </div>
            </div>
            <form id="formAccountDeactivation" @submit.prevent="deleteAccount" method="post">
              <div class="form-check mb-3">
                <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="accountActivation"
                    id="accountActivation"
                />
                <label class="form-check-label" for="accountActivation"
                >我确认要删除此账户</label
                >
              </div>
              <button type="submit" class="btn btn-danger deactivate-account">删除账户！
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- / Content -->
</template>

<style scoped>

</style>