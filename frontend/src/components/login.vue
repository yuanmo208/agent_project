<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <!-- 顶部标题与切换按钮 -->
      <div class="login-header">
        <h2>{{ isShow ? '验证码登录' : '密码登录' }}</h2>
        <el-button link type="primary" @click="loginChange">
          {{ isShow ? '切换到密码登录' : '切换到验证码登录' }}
        </el-button>
      </div>

      <!-- 验证码登录表单 -->
      <el-form v-show="isShow" label-position="top" class="login-form">
        <el-form-item label="邮箱号">
          <el-input v-model="email" placeholder="请输入邮箱" :disabled="isDisabled" clearable />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="code-row">
            <el-input v-model="code" v-bind:disabled="!isDisabled" placeholder="请输入验证码" clearable />
            <el-button type="primary" :disabled="isDisabled" @click="sendEmail">
              {{ isDisabled ? '已发送' : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="full-btn" @click="codeLogin">登 录</el-button>
        </el-form-item>
      </el-form>

      <!-- 密码登录表单 -->
      <el-form v-show="!isShow" label-position="top" class="login-form">
        <el-form-item label="邮箱号">
          <el-input v-model="email" placeholder="请输入邮箱" :disabled="isDisabled" clearable />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" show-password clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="full-btn" @click="pwdLogin">登 录</el-button>
        </el-form-item>
      </el-form>

      <!-- 底部注册入口 -->
      <div class="login-footer">
        <span class="hint-text"></span>
        <el-button link type="primary" @click="register">注册密码 →</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
let isDisabled = ref(false);
let isShow = ref(true);
let proxy = getCurrentInstance().proxy;
let router = useRouter();

let email = ref('1026473161@qq.com');
let code = ref('');
let password = ref('');

console.log(email.value);

// 发送验证码
function sendEmail() {
  let sendemail = email.value
  proxy.$axios({
    url: "email/sendEmail",
    method: "get",
    params: {email: sendemail}
  }).then(res => {
    let code = res.data.code;
    let msg = res.data.msg;
    let username = res.data.data;
    if (code === 200) {
      isDisabled.value = true;
      ElMessage.success(msg);
    } else {
      ElMessage.error(msg);
    }
  })
}

// 对比验证码并登录
function codeLogin() {
  proxy.$axios({
    url: "email/checkCode",
    method: "get",
    params: {
      email: email.value,
      code: code.value
    }
  }).then(res => {
    let code = res.data.code;
    let msg = res.data.msg;
    let data = res.data.data;
    if (code === 500){
      ElMessage.error(msg);
    }
    if (code === 200){
      ElMessage.success(msg);
      // 登录成功后将用户名存入sessionStorage
      sessionStorage.setItem("username", data);
      // 设置登录时延迟页面跳转
      setTimeout(() => {
        router.push({path: '/chat'});
      }, 2000)
    }
  })
}

// 变化登录方式
function loginChange() {
  isShow.value = !isShow.value;
}

// 密码登录
function pwdLogin() {
  proxy.$axios({
    url: "account/login",
    method: "get",
    params: {
      email: email.value,
      password: password.value
    }
  }).then(res => {
    let code = res.data.code;
    let msg = res.data.msg;
    let data = res.data.data;
    if (code === 500) {
      ElMessage.error(msg);
    } else if (code === 200) {
      ElMessage.success(msg);
      // 登录成功后将用户名存入sessionStorage
      sessionStorage.setItem("username", data);
      // 设置登录时延迟页面跳转
      setTimeout(() => {
        router.push({path: '/chat'});
      }, 2000)
    }
  })
}

// 注册密码跳转页面
function register() {
  router.push({path: '/register'});
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  padding: 10px;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #606266;
}

.code-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-row .el-input {
  flex: 1;
}

.full-btn {
  width: 100%;
  height: 42px;
  font-size: 16px;
  border-radius: 8px;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.hint-text {
  font-size: 12px;
  color: #909399;
}
</style>