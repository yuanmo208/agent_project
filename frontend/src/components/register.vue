<template>
  <div class="register-container">
    <el-card class="register-card" shadow="hover">
      <!-- 顶部标题与返回按钮 -->
      <div class="register-header">
        <h2>注册密码</h2>
        <el-button link type="primary" @click="back">返回登录</el-button>
      </div>

      <!-- 步骤条：根据 isShow 自动推进，纯展示不改动逻辑 -->
      <el-steps :active="isShow ? 1 : 0" align-center class="register-steps">
        <el-step title="验证邮箱" />
        <el-step title="设置密码" />
      </el-steps>

      <el-form label-position="top" class="register-form">
        <el-form-item label="邮箱号">
          <el-input v-model="email" placeholder="请输入邮箱" :disabled="isDisabled" clearable />
        </el-form-item>

        <el-form-item label="验证码">
          <div class="code-row">
            <el-input v-model="code" v-bind:disabled="!isDisabled" placeholder="请输入验证码" clearable />
            <el-button type="primary" @click="sendEmail">
              {{ isDisabled ? '重新发送' : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 验证码发送成功后才显示密码框（保留原 v-show 逻辑） -->
        <transition name="slide-fade">
          <el-form-item v-show="isShow" label="密码">
            <el-input v-model="password" type="password" placeholder="请设置密码" show-password clearable />
          </el-form-item>
        </transition>

        <el-form-item>
          <el-button type="primary" class="full-btn" @click="checkRegister" :disabled="!isDisabled">修改密码</el-button>
        </el-form-item>
      </el-form>

      <!-- 底部提示 -->
      <div class="register-footer">
        <span class="hint-text"></span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";
import {ElMessage} from "element-plus";
import {useRouter} from "vue-router";

let proxy = getCurrentInstance().proxy;
let router = useRouter();

let isShow = ref(false);
let isDisabled = ref(false);
let email = ref("1026473161@qq.com");
let code = ref("");
let password = ref("");

function sendEmail() {
  proxy.$axios({
    url: "account/register",
    method: "get",
    params: {email: email.value}
  }).then(res => {
    let code = res.data.code;
    let msg = res.data.msg;
    let data = res.data.data;
    if (code === 200) {
      ElMessage.success(msg);
      isDisabled.value = true;
      isShow.value = true;
    } else {
      ElMessage.error(msg);
    }

  })
}

function checkRegister() {
  let accountentity = {
    email: email.value,
    code: code.value,
    password: password.value
  }
  proxy.$axios({
    url: "account/checkRegister",
    method: "post",
    data: JSON.stringify(accountentity)
  }).then(res => {
    let code = res.data.code;
    let msg = res.data.msg;
    if (code === 200) {
      ElMessage.success(msg);
      setTimeout(() => {
        router.push({path: '/'})
      }, 2000)
    } else {
      ElMessage.error(msg);
    }
  })
}

function back() {
  router.push({path: '/'})
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  box-sizing: border-box;
}

.register-card {
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  padding: 10px;
}

.register-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.register-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.register-steps {
  margin-bottom: 24px;
}

.register-steps :deep(.el-step__title) {
  font-size: 13px;
}

.register-form :deep(.el-form-item__label) {
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

.register-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #909399;
}

/* 密码框出现时的过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>