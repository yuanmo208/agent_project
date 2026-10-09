<template>
  <div class="chat-container">
    <!-- ==================== 左侧历史聊天记录栏 ==================== -->
    <div class="sidebar">
      <!-- 用户信息区 -->
      <div class="sidebar-header">
        <el-avatar :size="38" class="user-avatar">
          {{ username.charAt(0).toUpperCase() || 'U' }}
        </el-avatar>
        <span class="username">{{ username || '用户' }}</span>
        <el-dropdown trigger="click">
          <el-icon class="more-icon"><MoreFilled /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 新建对话按钮 -->
      <div class="new-chat-section">
        <el-button type="primary" class="new-chat-btn" @click="createNewChat">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </el-button>
      </div>

      <!-- 搜索栏 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          class="history-search"
          placeholder="搜索聊天记录..."
          clearable
          @change="queryHistory"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 聊天记录列表 -->
      <div class="chat-list">
        <el-scrollbar height="100%">
          <div
            v-for="(chat, index) in historyList"
            :key="chat.historyId"
            class="chat-item"
            :class="{ active: currentChatId === chat.historyId }"
            @click="selectHistory(chat.historyId)"
          >
            <div class="chat-item-content">
              <el-icon class="chat-icon">
                <ChatDotRound />
              </el-icon>
              <div class="chat-info">
                <span class="chat-title">{{ chat.title }}</span>
                <span class="chat-time">{{ chat.time }}</span>
              </div>
            </div>
            <el-popconfirm
              title="确定要删除此聊天记录吗？"
              @confirm="deleteHistory(chat.historyId)"
            >
              <template #reference>
                <el-button
                  class="delete-btn"
                  :icon="Delete"
                  circle
                  size="small"
                  type="danger"
                  text
                  @click.stop
                />
              </template>
            </el-popconfirm>
          </div>
        </el-scrollbar>
      </div>

      <!-- 侧边栏底部装饰 -->
      <div class="sidebar-footer">
        <span class="footer-text">AI Chat Assistant</span>
      </div>
    </div>

    <!-- ==================== 右侧聊天栏 ==================== -->
    <div class="main-chat">
      <!-- 聊天窗口头部 -->
      <div class="chat-header">
        <div class="chat-header-left">
          <span class="chat-header-title">当前对话</span>
        </div>
        <div class="chat-header-right">
          <span class="online-dot"></span>
          <span class="online-text">在线</span>
        </div>
      </div>

      <!-- 聊天消息区域 -->
      <div class="chat-window">
        <el-scrollbar ref="scrollbarRef" class="message-scrollbar">
          <div class="message-list">
            <!-- 欢迎提示（无消息时显示） -->
            <div v-if="messages.length === 0" class="welcome-section">
              <div class="welcome-icon-wrapper">
                <el-icon :size="44" color="#fff"><ChatDotRound /></el-icon>
              </div>
              <h2>欢迎使用 AI 助手</h2>
              <p>有什么可以帮助您的吗？开始输入即可对话</p>
            </div>

            <!-- 消息列表 -->
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-item"
              :class="msg.role"
            >
              <!-- 用户消息 -->
              <template v-if="msg.role === 'user'">
                <div class="message-bubble user-bubble">
                  <span v-html="renderMarkdown(msg.content)"></span>
                </div>
                <el-avatar :size="34" class="message-avatar">
                  {{ username.charAt(0).toUpperCase() || 'U' }}
                </el-avatar>
              </template>

              <!-- AI消息 -->
              <template v-else>
                <el-avatar :size="34" class="message-avatar ai-avatar">
                  <el-icon><Monitor /></el-icon>
                </el-avatar>
                <div class="message-bubble ai-bubble">
                  <span v-html="renderMarkdown(msg.content)"></span>
                </div>
              </template>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="question"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 5 }"
            placeholder="请输入消息，按 Enter 发送，Shift+Enter 换行..."
            resize="none"
            class="message-input"
            @keydown.enter.exact.prevent="chat"
          />
          <el-button
            type="primary"
            class="send-btn"
            :icon="Promotion"
            circle
            :disabled="sendDisabled"
            @click="chat"
          />
        </div>
        <div class="input-footer">
          <span class="input-tip">AI 助手可能会犯错，请注意甄别信息</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from "vue";
import {Plus, Delete, ChatDotRound, MoreFilled, Monitor, Promotion, Search} from "@element-plus/icons-vue";
import {ElMessage} from "element-plus";
import { marked } from "marked";
import DOMPurify from "dompurify";

// 创建代理对象
let proxy = getCurrentInstance().proxy;

// Markdown 渲染（局部定义，避免 globalProperties 挂载时序问题导致 template 取不到）
marked.setOptions({ breaks: true, gfm: true, smartLists: true });
function renderMarkdown(text) {
  if (!text) return "";
  return DOMPurify.sanitize(marked.parse(text));
}

// 搜索的关键词
let searchKeyword = ref("");

// ==================== 响应式数据 ====================
let username = ref("");
let question = ref("");
let sendDisabled = ref(false);
let currentChatId = ref(0);
// 后端会话ID（由后端 /chat/create_session 返回，区别于历史记录 currentChatId）
let sessionId = ref("");

// 历史记录栏位
let historyList = ref();

// 正在对话的消息
let messages = ref([]);
// ==================== 聊天记录功能 ====================
function historyListMenu() {
  proxy.$axios({
    url: 'history/historyListMenu',
    method: 'get',
    params: {
      username: username.value,
    },
  }).then(res => {
    historyList.value = res.data.data;
  })
}

// ==================== 聊天对话功能 ====================
async function chat() {
  let myQuestion = question.value.trim();
  question.value = "";

  if (myQuestion.length === 0){
    ElMessage.warning("请输入问题");
    return
  }
  sendDisabled.value = true;
  messages.value.push({ role: "user", content: myQuestion });
  messages.value.push({ role: "assistant", content: "正在生成回复..." });

  // 首次发送时先创建会话，拿到后端 session_id（区别于历史记录 currentChatId）
  if (!sessionId.value) {
    try {
      let res = await proxy.$axios({
        url: 'chat/create_session',
        method: 'get',
        params: { user_id: username.value }
      });
      sessionId.value = res.data.session_id;
    } catch (e) {
      ElMessage.error("创建会话失败");
      sendDisabled.value = false;
      return;
    }
  }

  let urlSearchParams = new URLSearchParams({
        question: myQuestion,
        session_id: sessionId.value,
        user_id: username.value
  })
  let es = new EventSource("http://localhost:8000/chat/chat?" + urlSearchParams.toString())
  let s = "";
  es.onmessage = (event) => {
    // 后端 SSE 协议：{ data: 片段内容, done: 是否结束 }
    let parsed = JSON.parse(event.data);
    let data = parsed.data;
    if (parsed.done){
      if (data) {
        s += data;
        messages.value[messages.value.length - 1].content = s;
      }
      es.close();
      sendDisabled.value = false;
      saveConversation(myQuestion, s);
    }
    else{
      s += data;
      messages.value[messages.value.length - 1].content = s;
    }
  };
  es.onerror = () => {
    es.close();
    sendDisabled.value = false;
    ElMessage.error("连接异常，请重试");
  };
}

// ==================== 选择聊天记录功能 ====================
function selectHistory(historyId) {
  currentChatId.value = historyId;
  proxy.$axios({
    url: 'history/selectHistory',
    method: 'get',
    params: {
      historyId: historyId,
      username: username.value
    }
  }).then(res => {
    messages.value = res.data.data;
    // 恢复后端会话上下文，使后续对话接上历史
    sessionId.value = res.data.session_id || "";
  })
}
// ==================== 保存聊天记录功能 ====================
function saveConversation(question, answer) {
  proxy.$axios({
    url: 'chat/saveConversation',
    method: 'post',
    data: JSON.stringify({
      question: question,
      username: username.value,
      parentId: currentChatId.value,
      answer: answer,
      sessionId: sessionId.value,
    })
  }).then(res => {
    if(currentChatId.value === 0){
      currentChatId.value = res.data.data;
      historyListMenu();
     }
  })
}
// ==================== 创建新对话 ====================
function createNewChat() {
  messages.value = [];
  currentChatId.value = 0;
  sessionId.value = "";
}
// ==================== 删除聊天记录 ====================
function deleteHistory(historyId) {
  if (historyId === currentChatId.value) {
    createNewChat();
  }
  proxy.$axios({
    url: 'history/deleteHistory',
    method: 'get',
    params: {
      historyId: historyId,
      username: username.value
    }
  }).then(res => {
    let code = res.data.code;
    if (code === 200) {
      ElMessage.success("删除成功");
    } else {
      ElMessage.error("删除失败");
    }
    historyListMenu()
  })

}

function logout() {
  sessionStorage.removeItem("username");
  ElMessage.success("退出登录成功");
  setTimeout(() => {
    proxy.$router.push({ path: '/' })
  }, 3000)
}


function queryHistory() {
  proxy.$axios({
    url: 'history/queryHistory',
    method: 'get',
    params: {
      username: username.value,
      keyword: searchKeyword.value
    }
  }).then(res => {
    if (searchKeyword.value === ""){
      historyListMenu()
    }
    historyList.value = res.data.data;
  })
}

// ==================== 生命周期 ====================
onMounted(() => {
  username.value = sessionStorage.getItem("username") || "开发者";
  historyListMenu()
});
</script>

<style scoped>
/* ==================== 全局布局 ==================== */
.chat-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: #f0f2f5;
  font-family: "Inter", "Helvetica Neue", Helvetica, "PingFang SC",
    "Microsoft YaHei", Arial, sans-serif;
}

/* ==================== 左侧边栏 ==================== */
.sidebar {
  width: 290px;
  min-width: 290px;
  background: linear-gradient(180deg, #16162a 0%, #1e1e3a 50%, #252547 100%);
  display: flex;
  flex-direction: column;
  border-right: none;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 20px 18px 16px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 700;
  font-size: 15px;
  flex-shrink: 0;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
}

.username {
  flex: 1;
  color: #f0f0f5;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-icon {
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  font-size: 18px;
  transition: all 0.25s ease;
  padding: 4px;
  border-radius: 6px;
}

.more-icon:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
}

/* 新建对话 */
.new-chat-section {
  padding: 14px 16px 10px;
}

.new-chat-btn {
  width: 100%;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.35);
  transition: all 0.3s ease;
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.new-chat-btn:active {
  transform: translateY(0);
}
/* ==================== 搜索栏 ==================== */
.search-section {
  padding: 2px 16px 8px;
}

.history-search :deep(.el-input__wrapper) {
  height: 38px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.07);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s ease;
}

.history-search :deep(.el-input__wrapper:hover) {
  background-color: rgba(255, 255, 255, 0.11);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.18) inset;
}

.history-search :deep(.el-input__wrapper.is-focus) {
  background-color: rgba(255, 255, 255, 0.13);
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.85) inset,
              0 0 0 3px rgba(102, 126, 234, 0.18);
}

/* 输入文字与占位符 */
.history-search :deep(.el-input__inner) {
  color: #e9e9f7;
  font-size: 13px;
  caret-color: #8b9cf5;
}

.history-search :deep(.el-input__inner::placeholder) {
  color: rgba(205, 205, 235, 0.4);
}

/* 前缀搜索图标 */
.history-search :deep(.el-input__prefix-inner > .el-icon) {
  color: rgba(185, 185, 225, 0.55);
  font-size: 15px;
  transition: color 0.3s ease;
}

.history-search :deep(.el-input__wrapper.is-focus .el-input__prefix-inner > .el-icon) {
  color: #a78bfa;
}

/* 清除按钮 */
.history-search :deep(.el-input__clear) {
  color: rgba(205, 205, 235, 0.45);
  font-size: 14px;
  transition: color 0.25s ease;
}

.history-search :deep(.el-input__clear:hover) {
  color: #ffffff;
}

/* 聊天列表 */
.chat-list {
  flex: 1;
  overflow: hidden;
  padding: 6px 10px;
}

.chat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  margin-bottom: 4px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.chat-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.04);
}

.chat-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-color: rgba(102, 126, 234, 0.3);
}

.chat-item-content {
  display: flex;
  align-items: center;
  gap: 11px;
  flex: 1;
  overflow: hidden;
}

.chat-icon {
  color: rgba(160, 160, 200, 0.7);
  font-size: 17px;
  flex-shrink: 0;
}

.chat-item.active .chat-icon {
  color: #a78bfa;
}

.chat-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-title {
  color: #d4d4e8;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.chat-item.active .chat-title {
  color: #ffffff;
}

.chat-time {
  color: rgba(160, 160, 200, 0.5);
  font-size: 11px;
  margin-top: 3px;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.chat-item:hover .delete-btn {
  opacity: 1;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  text-align: center;
}

.footer-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  letter-spacing: 1px;
  font-weight: 500;
}

/* ==================== 右侧主聊天区 ==================== */
.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fc;
  min-width: 0;
}

/* 聊天头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  border-bottom: 1px solid #eef0f5;
  background-color: #ffffff;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.03);
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-header-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: 0.2px;
}

.chat-header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.online-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.online-text {
  font-size: 12px;
  color: #6ee7b7;
  font-weight: 500;
}

/* 聊天窗口 */
.chat-window {
  flex: 1;
  overflow: hidden;
  background: linear-gradient(180deg, #f8f9fc 0%, #f3f4f8 100%);
}

.message-scrollbar {
  height: 100%;
}

.message-list {
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  min-height: 100%;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 320px;
  color: #909399;
}

.welcome-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.35);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.welcome-section h2 {
  margin-top: 20px;
  color: #1a1a2e;
  font-size: 22px;
  font-weight: 700;
}

.welcome-section p {
  margin-top: 10px;
  color: #9ca3af;
  font-size: 14px;
}

/* 消息项 */
.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 78%;
  animation: msg-in 0.3s ease-out;
}

@keyframes msg-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-item.assistant {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
  margin-top: 3px;
  font-weight: 700;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* ==================== 消息气泡（已修复 Markdown 排版） ==================== */
.message-bubble {
  padding: 13px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
  white-space: normal;
  position: relative;
}

.user-bubble {
  background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
  color: #ffffff;
  border-bottom-right-radius: 6px;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.25);
}

.ai-bubble {
  background-color: #ffffff;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

/* ========== Markdown 内容排版样式 ========== */
.message-bubble :deep(p) {
  margin: 0 0 8px 0;
}
.message-bubble :deep(p:last-child) {
  margin-bottom: 0;
}
.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}
.message-bubble :deep(li) {
  margin-bottom: 4px;
}
.message-bubble :deep(pre) {
  background-color: rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  padding: 12px 14px;
  margin: 10px 0;
  overflow-x: auto;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.5;
}
.user-bubble :deep(pre) {
  background-color: rgba(255, 255, 255, 0.18);
}
.message-bubble :deep(code) {
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}
.message-bubble :deep(:not(pre) > code) {
  background-color: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
.user-bubble :deep(:not(pre) > code) {
  background-color: rgba(255, 255, 255, 0.2);
}
.message-bubble :deep(blockquote) {
  border-left: 3px solid rgba(102, 126, 234, 0.5);
  margin: 10px 0;
  padding: 4px 14px;
  color: #6b7280;
  background-color: rgba(102, 126, 234, 0.05);
  border-radius: 0 6px 6px 0;
}
.user-bubble :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.5);
  color: rgba(255, 255, 255, 0.85);
  background-color: rgba(255, 255, 255, 0.1);
}
.message-bubble :deep(table) {
  border-collapse: collapse;
  margin: 10px 0;
  width: 100%;
  font-size: 13px;
}
.message-bubble :deep(th),
.message-bubble :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}
.user-bubble :deep(th),
.user-bubble :deep(td) {
  border-color: rgba(255, 255, 255, 0.25);
}
.message-bubble :deep(th) {
  background-color: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}
.user-bubble :deep(th) {
  background-color: rgba(255, 255, 255, 0.12);
}
.message-bubble :deep(a) {
  color: #667eea;
  text-decoration: none;
}
.user-bubble :deep(a) {
  color: #c4b5fd;
}
.message-bubble :deep(a:hover) {
  text-decoration: underline;
}
.message-bubble :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 14px 0;
}
.user-bubble :deep(hr) {
  border-top-color: rgba(255, 255, 255, 0.25);
}
.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3),
.message-bubble :deep(h4),
.message-bubble :deep(h5),
.message-bubble :deep(h6) {
  margin: 12px 0 8px 0;
  font-weight: 700;
  line-height: 1.4;
}
.message-bubble :deep(h1) { font-size: 1.4em; }
.message-bubble :deep(h2) { font-size: 1.25em; }
.message-bubble :deep(h3) { font-size: 1.1em; }
.message-bubble :deep(h4) { font-size: 1em; }
.message-bubble :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
}

/* ==================== 输入区域 ==================== */
.input-area {
  padding: 18px 28px 14px;
  border-top: 1px solid #eef0f5;
  background-color: #ffffff;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background-color: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  padding: 10px 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background-color: #ffffff;
}

.message-input :deep(.el-textarea__inner) {
  background-color: transparent;
  border: none;
  box-shadow: none;
  padding: 6px 0;
  font-size: 14px;
  color: #1f2937;
  line-height: 1.5;
}

.message-input :deep(.el-textarea__inner::placeholder) {
  color: #b0b5c0;
}

.send-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.5);
}

.send-btn:disabled {
  opacity: 0.5;
  box-shadow: none;
}

.input-footer {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.input-tip {
  font-size: 12px;
  color: #c4c9d4;
  letter-spacing: 0.2px;
}

/* ==================== 滚动条美化 ==================== */
:deep(.el-scrollbar__bar) {
  opacity: 0.2;
}

:deep(.el-scrollbar__bar:hover) {
  opacity: 0.5;
}

/* 侧边栏滚动条 */
.sidebar :deep(.el-scrollbar__bar.is-vertical) {
  width: 4px;
}

.sidebar :deep(.el-scrollbar__thumb) {
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

.sidebar :deep(.el-scrollbar__thumb:hover) {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 主区域滚动条 */
.main-chat :deep(.el-scrollbar__thumb) {
  background-color: #d1d5db;
  border-radius: 4px;
}

.main-chat :deep(.el-scrollbar__thumb:hover) {
  background-color: #9ca3af;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
    min-width: 64px;
  }

  .sidebar-header .username,
  .sidebar-header .more-icon,
  .new-chat-section,
  .chat-info,
  .delete-btn,
  .sidebar-footer {
    display: none;
  }

  .sidebar-header {
    justify-content: center;
    padding: 16px 8px;
  }

  .chat-item {
    justify-content: center;
    padding: 12px 8px;
  }

  .message-item {
    max-width: 92%;
  }

  .message-list {
    padding: 16px;
  }

  .input-area {
    padding: 12px 16px 10px;
  }

  .chat-header {
    padding: 14px 16px;
  }
}
</style>