/**
 * Pro. Paper - 前端主逻辑
 */

// ─── 配置 ─────────────────────────────────────────

const API_BASE = 'http://localhost:8000';

const API_PRESETS = {
  zhipu: {
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4/',
    models: ['glm-4-plus', 'glm-4', 'glm-4-flash']
  },
  deepseek: {
    baseUrl: 'https://api.deepseek.com/v1',
    models: ['deepseek-chat', 'deepseek-coder']
  },
  openai: {
    baseUrl: 'https://api.openai.com/v1',
    models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
  },
  custom: {
    baseUrl: '',
    models: []
  }
};

// ─── 状态管理 ─────────────────────────────────────────

let state = {
  pdfUploaded: false,
  analyzing: false,
  analyses: {},
  eventSource: null
};

// ─── DOM 元素 ─────────────────────────────────────────

const elements = {
  // API 配置
  apiProvider: document.getElementById('apiProvider'),
  apiKey: document.getElementById('apiKey'),
  baseUrlGroup: document.getElementById('baseUrlGroup'),
  baseUrl: document.getElementById('baseUrl'),
  modelSelect: document.getElementById('modelSelect'),
  temperature: document.getElementById('temperature'),
  tempValue: document.getElementById('tempValue'),
  maxTokens: document.getElementById('maxTokens'),
  tokensValue: document.getElementById('tokensValue'),
  researchDirectionGroup: document.getElementById('researchDirectionGroup'),
  researchDirection: document.getElementById('researchDirection'),
  
  // 上传
  uploadArea: document.getElementById('uploadArea'),
  pdfInput: document.getElementById('pdfInput'),
  
  // 预览
  previewSection: document.getElementById('previewSection'),
  paperTitle: document.getElementById('paperTitle'),
  paperPages: document.getElementById('paperPages'),
  paperChars: document.getElementById('paperChars'),
  paperTokens: document.getElementById('paperTokens'),
  chaptersList: document.getElementById('chaptersList'),
  
  // 分析
  analyzeSection: document.getElementById('analyzeSection'),
  startAnalyzeBtn: document.getElementById('startAnalyzeBtn'),
  analyzeStatus: document.getElementById('analyzeStatus'),
  progressContainer: document.getElementById('progressContainer'),
  progressFill: document.getElementById('progressFill'),
  progressText: document.getElementById('progressText'),
  analysisResults: document.getElementById('analysisResults'),
  
  // 导出
  exportSection: document.getElementById('exportSection'),
  exportMdBtn: document.getElementById('exportMdBtn'),
  exportHtmlBtn: document.getElementById('exportHtmlBtn'),
  
  // Toast
  toast: document.getElementById('toast')
};

// ─── 初始化 ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initMermaid();
  initEventListeners();
});

function initMermaid() {
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'neutral'
    });
  }
}

function initEventListeners() {
  // API 提供商切换
  elements.apiProvider.addEventListener('change', handleProviderChange);
  
  // 滑块实时显示
  elements.temperature.addEventListener('input', (e) => {
    elements.tempValue.textContent = e.target.value;
  });
  
  elements.maxTokens.addEventListener('input', (e) => {
    elements.tokensValue.textContent = e.target.value;
  });
  
  // 复选框变化（构建课题）
  document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', handleModuleChange);
  });
  
  // 上传区域
  elements.uploadArea.addEventListener('click', () => elements.pdfInput.click());
  elements.pdfInput.addEventListener('change', handleFileSelect);
  
  // 拖拽上传
  elements.uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.uploadArea.classList.add('dragover');
  });
  
  elements.uploadArea.addEventListener('dragleave', () => {
    elements.uploadArea.classList.remove('dragover');
  });
  
  elements.uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.pdf')) {
      uploadPDF(file);
    } else {
      showToast('请上传 PDF 文件');
    }
  });
  
  // 开始分析
  elements.startAnalyzeBtn.addEventListener('click', startAnalysis);
  
  // 导出
  elements.exportMdBtn.addEventListener('click', exportMarkdown);
  elements.exportHtmlBtn.addEventListener('click', exportHTML);
}

// ─── 事件处理 ─────────────────────────────────────────

function handleProviderChange(e) {
  const provider = e.target.value;
  const preset = API_PRESETS[provider];
  
  // 显示/隐藏 Base URL
  if (provider === 'custom') {
    elements.baseUrlGroup.style.display = 'block';
  } else {
    elements.baseUrlGroup.style.display = 'none';
    elements.baseUrl.value = preset.baseUrl;
  }
  
  // 更新模型列表
  updateModelSelect(preset.models);
}

function updateModelSelect(models) {
  elements.modelSelect.innerHTML = models.map(model => 
    `<option value="${model}">${model}</option>`
  ).join('');
}

function handleModuleChange() {
  const modules = getSelectedModules();
  const hasTopicModule = modules.includes('构建课题');
  
  elements.researchDirectionGroup.style.display = hasTopicModule ? 'block' : 'none';
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    uploadPDF(file);
  }
}

// ─── 核心功能 ─────────────────────────────────────────

async function uploadPDF(file) {
  try {
    showToast('正在上传并解析 PDF...');
    console.log('=== 开始上传 PDF ===');
    
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('发送请求到:', `${API_BASE}/api/upload`);
    const response = await fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      body: formData
    });
    
    console.log('响应状态:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('上传失败:', errorText);
      throw new Error(`上传失败: ${response.status} ${errorText}`);
    }
    
    const data = await response.json();
    console.log('服务器返回数据:', data);
    
    // 更新 UI
    state.pdfUploaded = true;
    console.log('更新 state.pdfUploaded =', state.pdfUploaded);
    
    elements.paperTitle.textContent = data.metadata.title || '未检测到标题';
    elements.paperPages.textContent = data.metadata.pages || '?';
    elements.paperChars.textContent = data.char_count.toLocaleString();
    elements.paperTokens.textContent = `~${data.token_estimate.toLocaleString()}`;
    
    // 显示章节
    if (data.sections && data.sections.length > 0) {
      elements.chaptersList.innerHTML = `<ul>${data.sections.map(s => `<li>${s}</li>`).join('')}</ul>`;
    } else {
      elements.chaptersList.innerHTML = '<p class="hint">未检测到明显章节</p>';
    }
    
    // 显示预览和分析区域
    console.log('=== 准备显示分析区域 ===');
    console.log('previewSection 元素:', elements.previewSection);
    console.log('analyzeSection 元素:', elements.analyzeSection);
    
    if (elements.previewSection) {
      elements.previewSection.style.display = 'block';
      console.log('✅ previewSection 已显示');
    } else {
      console.error('❌ previewSection 未找到');
    }
    
    if (elements.analyzeSection) {
      elements.analyzeSection.style.display = 'block';
      elements.analyzeSection.style.border = '3px solid #3b82f6'; // 临时边框，确保可见
      console.log('✅ analyzeSection 已显示，添加蓝色边框');
      
      // 添加高亮动画
      elements.analyzeSection.classList.add('highlight');
      setTimeout(() => {
        elements.analyzeSection.classList.remove('highlight');
      }, 1000);
      
      // 滚动到分析区域
      setTimeout(() => {
        elements.analyzeSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        console.log('✅ 已滚动到分析区域');
      }, 100);
    } else {
      console.error('❌ analyzeSection 未找到！检查元素 ID');
    }
    
    showToast('✅ PDF 解析成功！请配置 API 并开始分析');
    
    console.log('=== PDF 上传完成 ===');
    console.log('当前 state:', state);
    console.log('analyzeSection display:', elements.analyzeSection?.style.display);
    
  } catch (error) {
    console.error('=== 上传错误 ===');
    console.error('错误信息:', error);
    console.error('错误堆栈:', error.stack);
    showToast('❌ 上传失败: ' + error.message);
  }
}

async function startAnalysis() {
  const modules = getSelectedModules();
  const apiKey = elements.apiKey.value.trim();
  
  if (!state.pdfUploaded) {
    showToast('请先上传 PDF');
    return;
  }
  
  if (!apiKey) {
    showToast('请输入 API Key');
    return;
  }
  
  if (modules.length === 0) {
    showToast('请至少选择一个分析模块');
    return;
  }
  
  state.analyzing = true;
  state.analyses = {};
  elements.startAnalyzeBtn.disabled = true;
  elements.progressContainer.style.display = 'block';
  elements.analysisResults.innerHTML = '';
  
  try {
    // 构建 SSE 连接
    const params = new URLSearchParams({
      modules: modules.join(','),
      api_key: apiKey,
      base_url: elements.baseUrl.value || API_PRESETS[elements.apiProvider.value].baseUrl,
      model: elements.modelSelect.value,
      temperature: elements.temperature.value,
      max_tokens: elements.maxTokens.value,
      research_direction: elements.researchDirection.value
    });
    
    const eventSource = new EventSource(`${API_BASE}/api/analyze?${params}`);
    
    let currentModule = null;
    let currentResult = '';
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'progress':
          currentModule = data.module;
          updateProgress(data.progress, `正在分析: ${data.module}`);
          createResultBlock(data.module);
          break;
          
        case 'chunk':
          currentResult += data.chunk;
          updateResultBlock(data.module, currentResult);
          break;
          
        case 'completed':
          state.analyses[data.module] = {
            result: currentResult,
            status: 'success'
          };
          currentResult = '';
          break;
          
        case 'error':
          showToast(`❌ ${data.module || '分析'}: ${data.error}`);
          if (currentModule) {
            markResultError(currentModule, data.error);
          }
          currentResult = '';
          break;
          
        case 'done':
          eventSource.close();
          finishAnalysis();
          break;
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
      showToast('❌ 连接中断');
      finishAnalysis();
    };
    
  } catch (error) {
    console.error('Analysis error:', error);
    showToast('❌ 分析失败: ' + error.message);
    finishAnalysis();
  }
}

function finishAnalysis() {
  state.analyzing = false;
  elements.startAnalyzeBtn.disabled = false;
  updateProgress(1.0, '✅ 所有模块分析完成');
  elements.exportSection.style.display = 'block';
}

function updateProgress(progress, text) {
  elements.progressFill.style.width = `${progress * 100}%`;
  elements.progressText.textContent = text;
}

function createResultBlock(module) {
  const existing = document.getElementById(`result-${module}`);
  if (existing) return;
  
  const block = document.createElement('div');
  block.id = `result-${module}`;
  block.className = 'result-block';
  block.innerHTML = `
    <div class="result-header">
      <h3>${module}</h3>
      <span class="result-meta">分析中...</span>
    </div>
    <div class="result-body">正在加载...</div>
  `;
  
  elements.analysisResults.appendChild(block);
}

function updateResultBlock(module, result) {
  const block = document.getElementById(`result-${module}`);
  if (!block) return;
  
  const body = block.querySelector('.result-body');
  
  // 渲染 Markdown
  body.innerHTML = marked.parse(result);
  
  // 渲染 Mermaid 图表
  renderMermaidInBlock(body);
}

function renderMermaidInBlock(container) {
  const mermaidBlocks = container.querySelectorAll('code.language-mermaid');
  
  mermaidBlocks.forEach((block, idx) => {
    const code = block.textContent;
    const wrap = document.createElement('div');
    wrap.className = 'mermaid-wrap';
    
    mermaid.render(`mermaid-${Date.now()}-${idx}`, code).then((result) => {
      wrap.innerHTML = result.svg;
      block.parentNode.replaceWith(wrap);
    }).catch((error) => {
      console.error('Mermaid render error:', error);
      wrap.innerHTML = `<p class="error">图表渲染失败</p>`;
      block.parentNode.replaceWith(wrap);
    });
  });
}

function markResultError(module, error) {
  const block = document.getElementById(`result-${module}`);
  if (!block) return;
  
  block.querySelector('.result-meta').textContent = '分析失败';
  block.querySelector('.result-body').innerHTML = `<p class="error">${error}</p>`;
}

function getSelectedModules() {
  const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
  return Array.from(checkboxes).map(cb => cb.value);
}

// ─── 导出功能 ─────────────────────────────────────────

async function exportMarkdown() {
  try {
    const response = await fetch(`${API_BASE}/api/export/markdown`);
    const data = await response.json();
    
    downloadFile(data.content, data.filename, 'text/markdown');
    showToast('✅ Markdown 报告已导出');
  } catch (error) {
    showToast('❌ 导出失败: ' + error.message);
  }
}

async function exportHTML() {
  try {
    const response = await fetch(`${API_BASE}/api/export/html`);
    const data = await response.json();
    
    downloadFile(data.content, data.filename, 'text/html');
    showToast('✅ HTML 报告已导出');
  } catch (error) {
    showToast('❌ 导出失败: ' + error.message);
  }
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── 工具函数 ─────────────────────────────────────────

function showToast(message, duration = 3000) {
  elements.toast.textContent = message;
  elements.toast.classList.add('show');
  
  setTimeout(() => {
    elements.toast.classList.remove('show');
  }, duration);
}
