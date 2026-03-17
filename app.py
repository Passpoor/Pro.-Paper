"""
📚 科研论文深度拆解系统 — Streamlit 主界面
"""

import re
import tempfile
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from parser import extract_text, detect_sections, get_analysis_text
from llm import create_client, stream_analysis
from prompts import (
    load_system_prompt,
    MODULE_INSTRUCTIONS,
    API_PRESETS,
)

# ─── 页面配置 ──────────────────────────────────────────────

st.set_page_config(
    page_title="论文深度拆解",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 自定义 CSS ────────────────────────────────────────────

st.markdown("""
<style>
    /* 隐藏 Streamlit 默认 hamburger */
    #MainMenu {visibility: hidden;}
    /* 风险标记样式 */
    .risk-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .risk-high { background: #fee2e2; color: #991b1b; }
    .risk-med  { background: #fef3c7; color: #92400e; }
    .risk-low  { background: #dbeafe; color: #1e40af; }
    /* Mermaid 图容器 */
    .mermaid-container {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 20px;
        margin: 8px 0;
        overflow-x: auto;
        overflow-y: auto;
        max-height: none;
    }
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── 报告生成（提前定义，避免 NameError）───────────────────

def _generate_report() -> str:
    """生成完整的 Markdown 报告"""
    lines = [
        "# 科研论文深度拆解报告",
        "",
        f"**生成时间：** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    if st.session_state.pdf_metadata:
        meta = st.session_state.pdf_metadata
        lines.extend([
            "## 论文信息",
            f"- **标题：** {meta.get('title', '未检测到')}",
            f"- **作者：** {meta.get('author', '未检测到')}",
            f"- **页数：** {meta.get('pages', '?')}",
            f"- **字符数：** {meta.get('char_count', 0):,}",
            "",
        ])
    for module, info in st.session_state.analyses.items():
        lines.extend([
            "---",
            "",
            f"# {module}",
            "",
            f"> 模型: {info['model']} | 时间: {info['timestamp']} | 估算 Tokens: ~{info['tokens_est']:,}",
            "",
            info["result"],
            "",
        ])
    return "\n".join(lines)


def _generate_html_report() -> str:
    """
    生成自包含的 HTML 报告。
    - Markdown 内容通过 marked.js 渲染
    - Mermaid 代码块通过 mermaid.js 渲染为 SVG
    - 每个图表可独立导出为 PNG（参考 WeFlow 的 SVG→Canvas→PNG 方案）
    - Mermaid 渲染完成后可整体导出为 HTML 文件
    """
    meta = st.session_state.pdf_metadata
    
    # 收集所有分析结果的 Markdown
    sections_html = ""
    for module, info in st.session_state.analyses.items():
        # 转义 HTML 特殊字符用于嵌入到 JS 字符串
        result_escaped = info["result"].replace("\\", "\\\\").replace("`", "\\`").replace("</script>", "<\\/script>")
        sections_html += f"""
      <div class="section-block">
        <div class="section-header">
          <h2>{module}</h2>
          <span class="section-meta">模型: {info['model']} | 时间: {info['timestamp']}</span>
        </div>
        <div class="section-body" data-md="{result_escaped}"></div>
      </div>
"""
    
    title = meta.get("title", "未检测到标题") if meta else "论文分析报告"
    author = meta.get("author", "") if meta else ""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>论文深度拆解报告</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      background: #f5f5f5; color: #333; line-height: 1.8; font-size: 16px;
    }}
    
    /* 工具栏 */
    .toolbar {{
      position: sticky; top: 0; z-index: 100;
      background: #fff; border-bottom: 1px solid #e0e0e0;
      padding: 12px 24px; display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 10px;
    }}
    .toolbar h1 {{ font-size: 1.2rem; color: #1e293b; }}
    .toolbar-actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .toolbar-actions button {{
      padding: 8px 16px; border: 1px solid #d0d0d0; border-radius: 6px;
      background: #fff; cursor: pointer; font-size: 13px; color: #333;
    }}
    .toolbar-actions button:hover {{ background: #f0f0f0; }}
    
    /* 论文信息 */
    .paper-info {{
      max-width: 900px; margin: 20px auto; padding: 20px;
      background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
    }}
    .paper-info h2 {{ font-size: 1.1rem; color: #64748b; margin-bottom: 12px; }}
    .paper-info .meta-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px;
    }}
    .paper-info .meta-item {{ font-size: 14px; color: #475569; }}
    .paper-info .meta-item strong {{ color: #1e293b; }}
    
    /* 分析结果 */
    .container {{ max-width: 900px; margin: 0 auto 40px; padding: 0 16px; }}
    .section-block {{
      background: #fff; border-radius: 10px; border: 1px solid #e5e7eb;
      margin-bottom: 16px; overflow: hidden;
    }}
    .section-header {{
      padding: 14px 20px; background: #f8fafc; border-bottom: 1px solid #e5e7eb;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .section-header h2 {{ font-size: 1rem; color: #1e293b; }}
    .section-meta {{ font-size: 12px; color: #94a3b8; }}
    .section-body {{
      padding: 20px 24px;
      font-size: 15px; line-height: 1.8; color: #333;
    }}
    
    /* Markdown 渲染样式 */
    .section-body h1 {{ font-size: 1.4em; margin: 0.8em 0 0.4em; font-weight: 600; color: #0f172a; }}
    .section-body h2 {{ font-size: 1.25em; margin: 1em 0 0.4em; font-weight: 600; color: #1e293b; }}
    .section-body h3 {{ font-size: 1.1em; margin: 1em 0 0.3em; font-weight: 600; color: #334155; }}
    .section-body p {{ margin: 0 0 0.8em; }}
    .section-body ul, .section-body ol {{ margin: 0 0 0.8em; padding-left: 1.5em; }}
    .section-body li {{ margin-bottom: 0.3em; }}
    .section-body blockquote {{
      margin: 0.8em 0; padding: 0.5em 1em; border-left: 4px solid #3b82f6;
      color: #475569; background: #f0f9ff; border-radius: 0 6px 6px 0;
    }}
    .section-body code {{
      padding: 0.15em 0.35em; background: #f1f5f9; border-radius: 4px;
      font-size: 0.9em; font-family: Consolas, Monaco, monospace; color: #7c3aed;
    }}
    .section-body pre {{
      margin: 0.8em 0; padding: 14px; background: #f8fafc; border-radius: 8px;
      overflow-x: auto; font-size: 13px; line-height: 1.5; border: 1px solid #e2e8f0;
    }}
    .section-body pre code {{ padding: 0; background: none; color: #333; }}
    .section-body table {{
      margin: 0.8em 0; border-collapse: collapse; width: 100%; font-size: 14px;
    }}
    .section-body th {{
      padding: 8px 12px; font-weight: 600; text-align: left;
      border-bottom: 2px solid #e2e8f0; background: #f8fafc;
    }}
    .section-body td {{
      padding: 8px 12px; text-align: left; border-bottom: 1px solid #f1f5f9;
    }}
    .section-body hr {{ margin: 1.2em 0; border: none; border-top: 1px solid #e2e8f0; }}
    .section-body strong {{ font-weight: 600; color: #0f172a; }}
    
    /* Mermaid 图表 */
    .mermaid-wrap {{
      margin: 1em 0; padding: 16px; background: #ffffff; border-radius: 8px;
      border: 1px solid #d1d5db; text-align: center; overflow-x: auto;
    }}
    .mermaid-actions {{ margin-top: 10px; }}
    .mermaid-actions button {{
      padding: 6px 14px; font-size: 13px; border: 1px solid #c0c0c0;
      border-radius: 4px; background: #fff; cursor: pointer; color: #333;
    }}
    .mermaid-actions button:hover {{ background: #f0f0f0; }}
    .mermaid-error {{ color: #dc2626; font-size: 14px; padding: 12px; }}
    
    /* Toast */
    .toast {{
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      padding: 10px 20px; background: #1e293b; color: #fff; border-radius: 8px;
      font-size: 14px; z-index: 1000; animation: fadeIn 0.2s ease;
    }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    
    /* 打印样式 */
    @media print {{
      .toolbar {{ display: none; }}
      .mermaid-actions {{ display: none; }}
      body {{ background: #fff; }}
      .section-block {{ border: 1px solid #ddd; break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <h1>📚 科研论文深度拆解报告</h1>
    <div class="toolbar-actions">
      <button onclick="exportAllMermaidPng()">🖼️ 导出所有图表为 PNG</button>
      <button onclick="window.print()">🖨️ 打印</button>
    </div>
  </div>

  <div class="paper-info">
    <h2>📄 论文信息</h2>
    <div class="meta-grid">
      <div class="meta-item"><strong>标题：</strong>{title}</div>
      {"<div class='meta-item'><strong>作者：</strong>" + author + "</div>" if author else ""}
      <div class="meta-item"><strong>页数：</strong>{meta.get('pages', '?') if meta else '?'}</div>
      <div class="meta-item"><strong>字符数：</strong>{f"{meta.get('char_count', 0):,}" if meta else '0'}</div>
    </div>
  </div>

  <div class="container">
{sections_html}
  </div>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
  (function() {{
    // 初始化
    mermaid.initialize({{
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'base',
      themeVariables: {{
        primaryColor: '#3b82f6',
        primaryTextColor: '#fff',
        primaryBorderColor: '#2563eb',
        lineColor: '#64748b',
        fontSize: '14px',
        background: '#ffffff',
        mainBkg: '#ffffff',
      }}
    }});
    if (typeof marked !== 'undefined') {{
      marked.setOptions({{ gfm: true, breaks: true }});
    }}

    // Toast 提示
    function showToast(msg, dur) {{
      var el = document.createElement('div');
      el.className = 'toast'; el.textContent = msg;
      document.body.appendChild(el);
      setTimeout(function() {{ if (el.parentNode) el.remove(); }}, dur || 3000);
    }}

    // SVG 转 PNG 下载
    function svgToPng(svgEl, index) {{
      var box = svgEl.getBoundingClientRect();
      var vb = svgEl.viewBox;
      var w = Math.ceil(vb && vb.baseVal ? vb.baseVal.width : box.width);
      var h = Math.ceil(vb && vb.baseVal ? vb.baseVal.height : box.height);
      var scale = 2;
      var canvas = document.createElement('canvas');
      canvas.width = w * scale; canvas.height = h * scale;
      var ctx = canvas.getContext('2d'); ctx.scale(scale, scale);
      var clone = svgEl.cloneNode(true);
      clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      clone.setAttribute('width', w); clone.setAttribute('height', h);
      var data = new XMLSerializer().serializeToString(clone);
      var b64 = btoa(unescape(encodeURIComponent(data)));
      var img = new Image();
      img.onload = function() {{
        ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        var a = document.createElement('a');
        a.download = 'chart-' + (index+1) + '.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
        showToast('已下载 ' + a.download);
      }};
      img.onerror = function() {{ showToast('导出失败'); }};
      img.src = 'data:image/svg+xml;base64,' + b64;
    }}

    // 导出所有图表
    function exportAllMermaidPng() {{
      var svgs = document.querySelectorAll('.mermaid-wrap svg');
      if (svgs.length === 0) {{ showToast('没有可导出的图表'); return; }}
      svgs.forEach(function(svg, i) {{ svgToPng(svg, i); }});
      showToast('已触发下载 ' + svgs.length + ' 张 PNG');
    }}

    // 分离 mermaid 块和 markdown 块
    function splitBlocks(md) {{
      var blocks = [];
      var re = /^```mermaid\\s*\\n([\\s\\S]*?)```/gm;
      var last = 0, m;
      while ((m = re.exec(md)) !== null) {{
        if (m.index > last) blocks.push({{ type: 'md', content: md.slice(last, m.index) }});
        blocks.push({{ type: 'mm', content: m[1].trim() }});
        last = re.lastIndex;
      }}
      if (last < md.length) blocks.push({{ type: 'md', content: md.slice(last) }});
      return blocks.length ? blocks : [{{ type: 'md', content: md }}];
    }}

    // 渲染一个 Mermaid 块
    function renderMm(code, idx) {{
      var wrap = document.createElement('div');
      wrap.className = 'mermaid-wrap';
      var pre = document.createElement('div');
      pre.id = 'mm-' + idx + '-' + Date.now();
      wrap.appendChild(pre);
      var acts = document.createElement('div');
      acts.className = 'mermaid-actions';
      var btn = document.createElement('button');
      btn.textContent = '导出为 PNG';
      acts.appendChild(btn);
      wrap.appendChild(acts);
      return mermaid.render(pre.id, code).then(function(res) {{
        pre.innerHTML = res.svg;
        if (typeof res.bindFunctions === 'function') res.bindFunctions(pre);
        var svg = pre.querySelector('svg');
        if (svg) btn.onclick = function() {{ svgToPng(svg, idx); }};
        return {{ container: wrap, svgEl: svg }};
      }}).catch(function() {{
        pre.className = 'mermaid-error';
        pre.textContent = 'Mermaid 语法错误';
        return {{ container: wrap, svgEl: null }};
      }});
    }}

    // 渲染所有 section-body
    function renderAll() {{
      var bodies = document.querySelectorAll('.section-body');
      var mmIdx = 0;
      var tasks = [];
      bodies.forEach(function(body) {{
        var md = body.getAttribute('data-md');
        if (!md) return;
        var blocks = splitBlocks(md);
        body.removeAttribute('data-md');
        body.innerHTML = '';
        blocks.forEach(function(b) {{
          if (b.type === 'md') {{
            var div = document.createElement('div');
            div.innerHTML = typeof marked !== 'undefined' ? marked.parse(b.content) : b.content;
            body.appendChild(div);
          }}
        }});
        // 二次处理：找到 mermaid pre 块，替换为渲染的图表
        var pres = body.querySelectorAll('pre code');
        pres.forEach(function(preCode) {{
          var text = preCode.textContent || preCode.innerText;
          if (/^mermaid\\s/i.test(text.trim().split('\\n')[0])) {{
            var code = text.trim().split('\\n').slice(1).join('\\n');
            var parent = preCode.closest('pre');
            if (parent) {{
              var task = renderMm(code, mmIdx).then(function(res) {{
                if (parent.parentNode) parent.parentNode.replaceChild(res.container, parent);
                mmIdx++;
              }});
              tasks.push(task);
            }}
          }}
        }});
      }});
      return Promise.all(tasks);
    }}

    renderAll().then(function() {{
      console.log('All Mermaid charts rendered.');
    }}).catch(function(e) {{
      console.error('Render error:', e);
    }});
  }})();
  </script>
</body>
</html>"""
    return html


# ─── Mermaid 渲染 ─────────────────────────────────────────

def sanitize_mermaid_code(code: str) -> str:
    """清理 Mermaid 代码，修复常见语法问题"""
    # 用引号包裹包含特殊字符的节点标签
    # 匹配 A[内容] 或 B(内容) 或 C((内容)) 等格式
    def fix_label(match):
        node_id = match.group(1)
        shape = match.group(2)  # [, (, ((, 等
        content = match.group(3)
        close = match.group(4)  # ], ), )), 等
        
        # 如果内容包含特殊字符，用引号包裹
        special_chars = ['(', ')', '"', "'", '<', '>', '&', '#']
        if any(char in content for char in special_chars):
            # 转义引号并用引号包裹
            content = content.replace('"', '#quot;')
            content = f'"{content}"'
        
        return f"{node_id}{shape}{content}{close}"
    
    # 处理各种节点形状: A[xxx], B(xxx), C((xxx)), D{{xxx}}, E>xxx]
    patterns = [
        (r'(\w+)\[([^\]]+)\]', '[', ']'),      # A[内容]
        (r'(\w+)\(([^)]+)\)', '(', ')'),       # B(内容)
        (r'(\w+)\(\(([^)]+)\)\)', '((', '))'), # C((内容))
    ]
    
    for pattern, open_bracket, close_bracket in patterns:
        def make_replacer(ob, cb):
            def replacer(m):
                node_id = m.group(1)
                content = m.group(2)
                special_chars = ['(', ')', '"', "'", '<', '>', '&', '#']
                if any(char in content for char in special_chars):
                    content = content.replace('"', '#quot;')
                    content = f'"{content}"'
                return f"{node_id}{ob}{content}{cb}"
            return replacer
        code = re.sub(pattern, make_replacer(open_bracket, close_bracket), code)
    
    return code


def render_mermaid(mermaid_code: str, height: int = 500):
    """在 Streamlit 中渲染 Mermaid 图"""
    # 清理 markdown 代码块标记
    code = re.sub(r"```mermaid\s*", "", mermaid_code)
    code = re.sub(r"```\s*$", "", code)
    code = code.strip()
    
    # 清理语法问题
    code = sanitize_mermaid_code(code)
    
    # 根据代码行数动态计算高度，确保显示完整
    line_count = len(code.split('\n'))
    dynamic_height = max(400, line_count * 28 + 100)
    
    # 使用完整的 HTML 文档结构，确保 Mermaid 正确渲染
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 10px;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
        .mermaid svg {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                fontSize: '14px'
            }}
        }});
    </script>
</body>
</html>
    """
    components.html(html, height=dynamic_height)


# ─── 提取 Mermaid 代码块 ─────────────────────────────────

def extract_mermaid_blocks(text: str) -> list:
    """从分析结果中提取 mermaid 代码块"""
    return re.findall(r"```mermaid\s*(.*?)```", text, re.DOTALL)


# ─── Session State 初始化 ─────────────────────────────────

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "pdf_metadata" not in st.session_state:
    st.session_state.pdf_metadata = {}
if "sections" not in st.session_state:
    st.session_state.sections = {}
if "analyses" not in st.session_state:
    st.session_state.analyses = {}
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


# ─── 侧边栏 ───────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ 配置面板")
    
    # API 配置
    st.subheader("🔑 LLM API")
    preset_name = st.selectbox(
        "API 提供商",
        list(API_PRESETS.keys()),
        index=0,
    )
    preset = API_PRESETS[preset_name]
    
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder=preset["placeholder"],
        key="api_key_input",
    )
    
    if preset_name == "自定义 (OpenAI 兼容)":
        base_url = st.text_input("Base URL", placeholder="https://your-api.com/v1")
        model = st.text_input("Model", placeholder="your-model-name")
    else:
        base_url = preset["base_url"]
        model = preset["model"]
    
    # 高级设置
    with st.expander("🔧 高级设置"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)
        max_tokens = st.number_input(
            "Max Output Tokens",
            min_value=1024,
            max_value=32768,
            value=8192,
            step=1024,
            help="API 单次输出最大 token 数。智谱/GLM 通常上限 8192，GPT-4o 可达 16384。",
        )
    
    st.divider()
    
    # 分析模块选择
    st.subheader("📋 分析模块")
    
    module_names = list(MODULE_INSTRUCTIONS.keys())
    selected_modules = []
    
    # 全选按钮
    select_all = st.checkbox("全选", value=False, key="select_all")
    for mod in module_names:
        checked = st.checkbox(mod, value=select_all, key=f"mod_{mod}")
        if checked:
            selected_modules.append(mod)
    
    st.divider()
    
    # 课题构建额外输入
    if "构建课题" in selected_modules:
        st.subheader("🧬 课题信息")
        research_direction = st.text_area(
            "你的研究方向",
            placeholder="例：肺癌免疫微环境中衰老相关分泌表型（SASP）对 CD8+ T 细胞功能的影响",
            height=100,
        )
    
    st.divider()
    
    # 操作按钮（始终显示）
    st.subheader("📦 导出报告")
    
    if st.session_state.analyses:
        if st.button("🗑️ 清除所有分析结果"):
            st.session_state.analyses = {}
            st.rerun()
        
        col_md, col_html = st.columns(2)
        with col_md:
            st.download_button(
                "📥 导出 Markdown",
                data=_generate_report(),
                file_name="paper_analysis_report.md",
                mime="text/markdown",
            )
        with col_html:
            st.download_button(
                "📥 导出 HTML（含图表）",
                data=_generate_html_report(),
                file_name="paper_analysis_report.html",
                mime="text/html",
            )
    else:
        st.caption("⚠️ 尚未运行分析，导出按钮将在分析完成后可用")
        col_md, col_html = st.columns(2)
        with col_md:
            st.button("📥 导出 Markdown", disabled=True)
        with col_html:
            st.button("📥 导出 HTML（含图表）", disabled=True)


# ─── 主界面 ───────────────────────────────────────────────

st.title("📚 科研论文深度拆解系统")
st.caption("博士级科研认知训练引擎 — 因果推理 × 逻辑断点 × 机制防御 × 课题迁移")

# ── Step 1: 上传 PDF ────────────────────────────────────

st.header("📤 第一步：上传论文 PDF")

uploaded_file = st.file_uploader(
    "拖拽或点击上传 PDF 文件",
    type=["pdf"],
    key="pdf_uploader",
)

if uploaded_file is not None:
    # 保存到临时文件并解析
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    
    try:
        with st.spinner("解析 PDF..."):
            text, metadata = extract_text(tmp_path)
            sections = detect_sections(text)
        
        st.session_state.pdf_text = text
        st.session_state.pdf_metadata = metadata
        st.session_state.sections = sections
        st.success("✅ PDF 解析完成")
    
    except Exception as e:
        st.error(f"❌ PDF 解析失败: {e}")
    
    finally:
        Path(tmp_path).unlink(missing_ok=True)

# ── Step 2: 论文预览 ────────────────────────────────────

if st.session_state.pdf_text:
    st.header("📄 第二步：论文预览")
    meta = st.session_state.pdf_metadata
    secs = st.session_state.sections
    
    # 元信息卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("页数", meta.get("pages", "?"))
    col2.metric("字符数", f"{meta.get('char_count', 0):,}")
    col3.metric("估算 Tokens", f"~{meta.get('est_tokens', 0):,}")
    col4.metric("检测到章节", len(secs))
    
    # 章节导航
    if secs:
        st.subheader("📑 章节导航")
        sec_cols = st.columns(min(len(secs), 6))
        for i, (name, (start, end)) in enumerate(sorted(secs.items(), key=lambda x: x[1][0])):
            with sec_cols[i % len(sec_cols)]:
                sec_len = end - start if end else len(st.session_state.pdf_text) - start
                st.caption(f"**{name}** ({sec_len:,} 字符)")
    
    # 文本预览
    with st.expander("👁️ 查看提取全文（可展开）", expanded=False):
        st.text_area(
            "全文内容",
            st.session_state.pdf_text[:50000],  # 限制预览长度
            height=400,
            key="full_text_preview",
            disabled=True,
        )
        if len(st.session_state.pdf_text) > 50000:
            st.info(f"全文较长，仅显示前 50,000 字符（共 {len(st.session_state.pdf_text):,} 字符）")

# ── Step 3: 开始分析 ────────────────────────────────────

if st.session_state.pdf_text and selected_modules and api_key:
    st.header("🔬 第三步：运行分析")
    
    if not base_url:
        st.error("请配置 Base URL（自定义 API 需要手动填写）")
        st.stop()
    
    # 创建 LLM 客户端
    client = create_client(api_key, base_url)
    system_prompt = load_system_prompt()
    
    # 总 Token 估算
    total_prompt_tokens = (
        len(system_prompt) * 0.25  # system prompt
        + len(st.session_state.pdf_text) * 0.25  # paper text
        + 1000  # module instruction overhead
    )
    
    st.info(f"📊 估算每次分析约消耗 ~{int(total_prompt_tokens + max_tokens):,} tokens（含输入+输出）× {len(selected_modules)} 个模块")
    
    # 逐模块执行分析
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, module in enumerate(selected_modules):
        status_text.info(f"🔄 正在分析：**{module}**...")
        progress_bar.progress((idx) / len(selected_modules))
        
        # 获取模块对应的文本
        module_text = get_analysis_text(
            st.session_state.pdf_text,
            st.session_state.sections,
            module,
        )
        
        # 构建用户提示
        instruction = MODULE_INSTRUCTIONS[module]
        if module == "构建课题":
            direction = st.session_state.get("research_direction", "")
            if direction:
                user_content = f"{instruction}\n\n---\n\n## 我的论文\n\n{module_text[:30000]}\n\n---\n\n## 我的研究方向\n{direction}"
            else:
                user_content = f"{instruction}\n\n---\n\n## 论文内容\n\n{module_text[:30000]}\n\n⚠️ 用户未提供研究方向，请基于论文内容给出通用迁移建议。"
        elif module == "整篇拆解":
            user_content = f"{instruction}\n\n---\n\n## 论文全文\n\n{module_text[:40000]}"
        else:
            user_content = f"{instruction}\n\n---\n\n## 论文内容\n\n{module_text[:35000]}"
        
        # 流式输出
        st.subheader(f"{'━' * 3} {module} {'━' * 3}")
        
        result_container = st.empty()
        full_result = ""
        
        try:
            for chunk in stream_analysis(
                client, model, system_prompt, user_content,
                temperature=temperature, max_tokens=max_tokens,
            ):
                full_result += chunk
                result_container.markdown(full_result)
        except Exception as e:
            st.error(f"分析失败: {e}")
            full_result = f"[分析失败] {e}"
        
        # 保存结果
        st.session_state.analyses[module] = {
            "result": full_result,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "tokens_est": int(total_prompt_tokens + max_tokens),
        }
        
        # 提取并渲染 Mermaid 图
        mermaid_blocks = extract_mermaid_blocks(full_result)
        if mermaid_blocks:
            with st.expander("📊 因果路径图", expanded=True):
                for block in mermaid_blocks:
                    render_mermaid(block, height=500)
        
        st.divider()
    
    progress_bar.progress(1.0)
    status_text.success("✅ 所有模块分析完成！")
    st.balloons()

elif st.session_state.pdf_text and not selected_modules:
    st.header("🔬 第三步：运行分析")
    st.warning("请在左侧面板选择至少一个分析模块")

elif st.session_state.pdf_text and not api_key:
    st.header("🔬 第三步：运行分析")
    st.warning("请在左侧面板配置 API Key")

else:
    # 欢迎页
    st.header("欢迎使用 📚 论文深度拆解系统")
    
    col_welcome, col_info = st.columns([1, 1])
    
    with col_welcome:
        st.markdown("""
        ### 🚀 快速开始
        
        1. **上传 PDF** — 支持任意学术论文 PDF
        2. **选择模块** — 左侧面板勾选分析模块
        3. **配置 API** — 填入你的 LLM API Key
        4. **开始分析** — 自动流式输出结果
        
        ### 📋 可用分析模块
        
        | 模块 | 功能 |
        |------|------|
        | 整篇拆解 | 全流程完整分析 |
        | 引言 | 逻辑断点识别 |
        | 结果 | 因果等级判定 |
        | 方法 | 功能定位与迁移 |
        | 逻辑链 | 因果路径 + Mermaid 图 |
        | 终局 | 认知总结 + 课题迁移 |
        | 风险审查 | 机制谬误防御 |
        | 构建课题 | 反向构建研究路径 |
        """)
    
    with col_info:
        st.markdown("""
        ### 🔑 支持的 LLM
        
        - **智谱 AI (GLM-4-Plus)** — 推荐，中文优秀
        - **DeepSeek** — 性价比高
        - **OpenAI (GPT-4o)** — 英文论文首选
        - **任何 OpenAI 兼容 API**
        
        ### 💡 使用提示
        
        - 建议使用 **GLM-4-Plus** 或 **GPT-4o** 等强推理模型
        - "整篇拆解"模块耗时最长（~3-5分钟）
        - 可分模块逐步分析，结果自动保存
        - 分析完成后可导出 Markdown 报告
        """)


# ─── 已有结果回显 ─────────────────────────────────────────

if st.session_state.analyses:
    st.header("📊 历史分析结果")
    
    for module, info in st.session_state.analyses.items():
        with st.expander(f"📁 {module} — {info['timestamp']}", expanded=False):
            st.caption(f"模型: {info['model']} | 估算 Tokens: ~{info['tokens_est']:,}")
            st.markdown(info["result"])


