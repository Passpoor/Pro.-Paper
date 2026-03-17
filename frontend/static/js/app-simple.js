/**
 * Pro. Paper - 简化版前端
 * 支持直接粘贴文本或上传 PDF
 */

const API_BASE = 'http://localhost:8000';

const API_PRESETS = {
  zhipu: { baseUrl: 'https://open.bigmodel.cn/api/paas/v4/', models: ['glm-4-plus', 'glm-4'] },
  deepseek: { baseUrl: 'https://api.deepseek.com/v1', models: ['deepseek-chat'] },
  openai: { baseUrl: 'https://api.openai.com/v1', models: ['gpt-4o', 'gpt-3.5-turbo'] },
  custom: { baseUrl: '', models: [] }
};

let paperContent = '';
let analyses = {};

// 初始化
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
  document.getElementById('apiProvider').addEventListener('change', (e) => {
    const provider = e.target.value;
    const preset = API_PRESETS[provider];
    
    document.getElementById('baseUrlGroup').style.display = provider === 'custom' ? 'block' : 'none';
    if (provider !== 'custom') {
      document.getElementById('baseUrl').value = preset.baseUrl;
    }
    
    updateModelSelect(preset.models);
  });
  
  // 滑块
  document.getElementById('temperature').addEventListener('input', (e) => {
    document.getElementById('tempValue').textContent = e.target.value;
  });
  
  document.getElementById('maxTokens').addEventListener('input', (e) => {
    document.getElementById('tokensValue').textContent = e.target.value;
  });
  
  // 模块选择
  document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      const modules = getSelectedModules();
      document.getElementById('researchDirectionGroup').style.display = modules.includes('构建课题') ? 'block' : 'none';
    });
  });
  
  // 字符计数
  document.getElementById('paperText').addEventListener('input', (e) => {
    document.getElementById('charCount').textContent = e.target.value.length.toLocaleString();
  });
  
  // PDF 上传
  const uploadArea = document.getElementById('uploadArea');
  const pdfInput = document.getElementById('pdfInput');
  
  uploadArea.addEventListener('click', () => pdfInput.click());
  
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });
  
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
  });
  
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.pdf')) {
      uploadPDF(file);
    } else {
      showToast('请上传 PDF 文件');
    }
  });
  
  pdfInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) uploadPDF(file);
  });
  
  // 开始分析
  document.getElementById('startAnalyzeBtn').addEventListener('click', startAnalysis);
  
  // 导出
  document.getElementById('exportMdBtn').addEventListener('click', exportMarkdown);
  document.getElementById('exportHtmlBtn').addEventListener('click', exportHTML);
}

// 切换标签
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
  
  event.target.classList.add('active');
  document.getElementById(tab + 'Tab').style.display = 'block';
}

function updateModelSelect(models) {
  const select = document.getElementById('modelSelect');
  select.innerHTML = models.map(model => 
    `<option value="${model}">${model}</option>`
  ).join('');
}

// 上传 PDF
async function uploadPDF(file) {
  try {
    showToast('正在解析 PDF...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('上传失败');
    
    const data = await response.json();
    
    paperContent = data.text || '';
    
    // 显示 PDF 信息
    document.getElementById('pdfInfo').style.display = 'block';
    document.getElementById('pdfPages').textContent = data.metadata.pages || '?';
    document.getElementById('pdfChars').textContent = data.char_count.toLocaleString();
    
    showToast('✅ PDF 解析成功');
    
  } catch (error) {
    console.error('Upload error:', error);
    showToast('❌ 上传失败: ' + error.message);
  }
}

// 开始分析
async function startAnalysis() {
  const modules = getSelectedModules();
  const apiKey = document.getElementById('apiKey').value.trim();
  
  // 获取论文内容
  if (!paperContent) {
    paperContent = document.getElementById('paperText').value.trim();
  }
  
  if (!paperContent) {
    showToast('请输入或上传论文内容');
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
  
  const btn = document.getElementById('startAnalyzeBtn');
  btn.disabled = true;
  btn.textContent = '⏳ 分析中...';
  
  document.getElementById('progressContainer').style.display = 'block';
  document.getElementById('resultsSection').style.display = 'none';
  analyses = {};
  
  try {
    const params = new URLSearchParams({
      text: paperContent,
      modules: modules.join(','),
      api_key: apiKey,
      base_url: document.getElementById('baseUrl').value || API_PRESETS[document.getElementById('apiProvider').value].baseUrl,
      model: document.getElementById('modelSelect').value,
      temperature: document.getElementById('temperature').value,
      max_tokens: document.getElementById('maxTokens').value,
      research_direction: document.getElementById('researchDirection').value
    });
    
    const response = await fetch(`${API_BASE}/api/analyze-simple`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: paperContent,
        modules: modules,
        api_key: apiKey,
        base_url: document.getElementById('baseUrl').value || API_PRESETS[document.getElementById('apiProvider').value].baseUrl,
        model: document.getElementById('modelSelect').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        max_tokens: parseInt(document.getElementById('maxTokens').value),
        research_direction: document.getElementById('researchDirection').value
      })
    });
    
    if (!response.ok) throw new Error('分析请求失败');
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          handleStreamEvent(data);
        }
      }
    }
    
    showToast('✅ 分析完成');
    document.getElementById('resultsSection').style.display = 'block';
    
  } catch (error) {
    console.error('Analysis error:', error);
    showToast('❌ 分析失败: ' + error.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '🚀 开始分析';
  }
}

function handleStreamEvent(data) {
  switch (data.type) {
    case 'progress':
      updateProgress(data.progress, `正在分析: ${data.module}`);
      createResultBlock(data.module);
      break;
      
    case 'chunk':
      appendResult(data.module, data.chunk);
      break;
      
    case 'completed':
      analyses[data.module] = document.getElementById(`result-${data.module}`).querySelector('.result-body').textContent;
      break;
      
    case 'error':
      showToast(`❌ ${data.module}: ${data.error}`);
      break;
      
    case 'done':
      updateProgress(1.0, '✅ 完成');
      break;
  }
}

function updateProgress(progress, text) {
  document.getElementById('progressFill').style.width = `${progress * 100}%`;
  document.getElementById('progressText').textContent = text;
}

function createResultBlock(module) {
  const container = document.getElementById('analysisResults');
  const existing = document.getElementById(`result-${module}`);
  if (existing) return;
  
  const block = document.createElement('div');
  block.id = `result-${module}`;
  block.className = 'result-block';
  block.innerHTML = `
    <div class="result-header">
      <h3>${module}</h3>
    </div>
    <div class="result-body"></div>
  `;
  container.appendChild(block);
}

function appendResult(module, chunk) {
  const block = document.getElementById(`result-${module}`);
  if (!block) return;
  
  const body = block.querySelector('.result-body');
  const currentText = body.textContent + chunk;
  
  // 渲染 Markdown
  body.innerHTML = marked.parse(currentText);
  
  // 渲染 Mermaid
  setTimeout(() => renderMermaidInBlock(body), 100);
}

function renderMermaidInBlock(container) {
  const mermaidBlocks = container.querySelectorAll('code.language-mermaid');
  
  mermaidBlocks.forEach((block, idx) => {
    const code = block.textContent;
    const id = `mermaid-${Date.now()}-${idx}`;
    
    mermaid.render(id, code).then((result) => {
      const wrap = document.createElement('div');
      wrap.className = 'mermaid-wrap';
      wrap.innerHTML = result.svg;
      block.parentNode.replaceWith(wrap);
    }).catch(console.error);
  });
}

function getSelectedModules() {
  const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
  return Array.from(checkboxes).map(cb => cb.value);
}

// 导出
async function exportMarkdown() {
  if (Object.keys(analyses).length === 0) {
    showToast('没有可导出的结果');
    return;
  }
  
  let content = '# 论文分析报告\n\n';
  
  for (const [module, result] of Object.entries(analyses)) {
    content += `## ${module}\n\n${result}\n\n---\n\n`;
  }
  
  downloadFile(content, 'paper_analysis.md', 'text/markdown');
  showToast('✅ Markdown 已导出');
}

async function exportHTML() {
  if (Object.keys(analyses).length === 0) {
    showToast('没有可导出的结果');
    return;
  }
  
  let html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>论文分析报告</title>
  <style>
    body { font-family: -apple-system, "Microsoft YaHei", sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.8; }
    h1, h2, h3 { color: #1e293b; }
    .section { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <h1>📚 论文分析报告</h1>
`;
  
  for (const [module, result] of Object.entries(analyses)) {
    html += `<div class="section"><h2>${module}</h2>${marked.parse(result)}</div>`;
  }
  
  html += '</body></html>';
  
  downloadFile(html, 'paper_analysis.html', 'text/html');
  showToast('✅ HTML 已导出');
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

function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}
