"""
FastAPI 后端 - Pro. Paper 论文深度拆解系统
"""

import os
import json
import time
import tempfile
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入核心模块
from parser import extract_text, detect_sections, get_analysis_text
from llm import create_client, stream_analysis
from prompts import load_system_prompt, MODULE_INSTRUCTIONS

app = FastAPI(
    title="Pro. Paper API",
    description="科研论文深度拆解系统 API",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（前端）
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# 临时存储（生产环境应使用数据库）
temp_storage = {
    "pdf_text": None,
    "pdf_metadata": None,
    "sections": None,
    "analyses": {}
}


# ─── 数据模型 ─────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    modules: List[str]
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    research_direction: Optional[str] = ""


class AnalyzeProgress(BaseModel):
    module: str
    progress: float
    status: str  # "analyzing", "completed", "error"
    result: Optional[str] = None


# ─── API 路由 ─────────────────────────────────────────

@app.get("/")
async def root():
    """返回前端页面"""
    frontend_index = frontend_path / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    return {"status": "ok", "message": "Pro. Paper API v2.0.0"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """上传 PDF 文件"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # 解析 PDF
        pdf_text, metadata = extract_text(tmp_path)
        sections = detect_sections(pdf_text)
        
        # 存储到内存
        temp_storage["pdf_text"] = pdf_text
        temp_storage["pdf_metadata"] = metadata
        temp_storage["sections"] = sections
        temp_storage["analyses"] = {}
        
        # 删除临时文件
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "metadata": metadata,
            "sections": list(sections.keys()) if sections else [],
            "char_count": len(pdf_text),
            "token_estimate": int(len(pdf_text) * 0.25)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")


@app.get("/api/metadata")
async def get_metadata():
    """获取 PDF 元数据"""
    if not temp_storage["pdf_metadata"]:
        raise HTTPException(status_code=404, detail="未上传 PDF")
    
    return {
        "metadata": temp_storage["pdf_metadata"],
        "sections": list(temp_storage["sections"].keys()) if temp_storage["sections"] else [],
        "char_count": len(temp_storage["pdf_text"]) if temp_storage["pdf_text"] else 0
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """流式分析 - Server-Sent Events"""
    if not temp_storage["pdf_text"]:
        raise HTTPException(status_code=404, detail="未上传 PDF")
    
    async def event_stream():
        """SSE 事件流"""
        try:
            # 创建 LLM 客户端
            client = create_client(request.api_key, request.base_url)
            system_prompt = load_system_prompt()
            
            for idx, module in enumerate(request.modules):
                # 发送进度
                progress = idx / len(request.modules)
                yield f"data: {json.dumps({'type': 'progress', 'module': module, 'progress': progress, 'status': 'analyzing'})}\n\n"
                
                try:
                    # 获取模块对应的文本
                    module_text = get_analysis_text(
                        temp_storage["pdf_text"],
                        temp_storage["sections"],
                        module
                    )
                    
                    # 构建用户提示
                    instruction = MODULE_INSTRUCTIONS[module]
                    if module == "构建课题":
                        if request.research_direction:
                            user_content = f"{instruction}\n\n---\n\n## 我的论文\n\n{module_text[:30000]}\n\n---\n\n## 我的研究方向\n{request.research_direction}"
                        else:
                            user_content = f"{instruction}\n\n---\n\n## 论文内容\n\n{module_text[:30000]}\n\n⚠️ 用户未提供研究方向，请基于论文内容给出通用迁移建议。"
                    elif module == "整篇拆解":
                        user_content = f"{instruction}\n\n---\n\n## 论文全文\n\n{module_text[:40000]}"
                    else:
                        user_content = f"{instruction}\n\n---\n\n## 论文内容\n\n{module_text[:35000]}"
                    
                    # 流式分析
                    full_result = ""
                    for chunk in stream_analysis(
                        client, request.model, system_prompt, user_content,
                        temperature=request.temperature, max_tokens=request.max_tokens
                    ):
                        full_result += chunk
                        # 发送分析结果片段
                        yield f"data: {json.dumps({'type': 'chunk', 'module': module, 'chunk': chunk})}\n\n"
                    
                    # 保存结果
                    temp_storage["analyses"][module] = {
                        "result": full_result,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "model": request.model,
                        "tokens_est": int(len(system_prompt) * 0.25 + len(module_text) * 0.25 + request.max_tokens)
                    }
                    
                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'completed', 'module': module, 'status': 'success'})}\n\n"
                    
                except Exception as e:
                    error_msg = f"分析失败: {str(e)}"
                    temp_storage["analyses"][module] = {
                        "result": error_msg,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "model": request.model,
                        "tokens_est": 0
                    }
                    yield f"data: {json.dumps({'type': 'error', 'module': module, 'error': error_msg})}\n\n"
            
            # 全部完成
            yield f"data: {json.dumps({'type': 'done', 'progress': 1.0})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/export/markdown")
async def export_markdown():
    """导出 Markdown 报告"""
    if not temp_storage["analyses"]:
        raise HTTPException(status_code=404, detail="无分析结果")
    
    try:
        report = _generate_markdown_report()
        return {
            "success": True,
            "content": report,
            "filename": f"paper_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.get("/api/export/html")
async def export_html():
    """导出 HTML 报告"""
    if not temp_storage["analyses"]:
        raise HTTPException(status_code=404, detail="无分析结果")
    
    try:
        html = _generate_html_report()
        return {
            "success": True,
            "content": html,
            "filename": f"paper_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


# ─── 辅助函数 ─────────────────────────────────────────

def _generate_markdown_report() -> str:
    """生成 Markdown 报告"""
    lines = ["# 📚 论文深度拆解报告\n"]
    
    meta = temp_storage.get("pdf_metadata")
    if meta:
        lines.append("## 📄 论文信息\n")
        lines.append(f"- **标题**: {meta.get('title', '未检测到标题')}")
        if meta.get('author'):
            lines.append(f"- **作者**: {meta['author']}")
        lines.append(f"- **页数**: {meta.get('pages', '?')}")
        lines.append(f"- **字符数**: {meta.get('char_count', 0):,}")
        lines.append("\n---\n")
    
    for module, info in temp_storage["analyses"].items():
        lines.append(f"## {module}\n")
        lines.append(f"> 模型: {info['model']} | 时间: {info['timestamp']}\n")
        lines.append(info["result"])
        lines.append("\n---\n")
    
    return "\n".join(lines)


def _generate_html_report() -> str:
    """生成 HTML 报告"""
    import base64
    
    meta = temp_storage.get("pdf_metadata")
    
    # 收集分析结果
    sections_data = []
    for module, info in temp_storage["analyses"].items():
        sections_data.append({
            "module": module,
            "model": info["model"],
            "timestamp": info["timestamp"],
            "result": info["result"]
        })
    
    sections_json = json.dumps(sections_data, ensure_ascii=False)
    sections_b64 = base64.b64encode(sections_json.encode('utf-8')).decode('ascii')
    
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
    .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
    .paper-info {{
      background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 20px;
      border: 1px solid #e5e7eb;
    }}
    .section-block {{
      background: #fff; border-radius: 10px; margin-bottom: 16px;
      border: 1px solid #e5e7eb; overflow: hidden;
    }}
    .section-header {{
      padding: 14px 20px; background: #f8fafc; border-bottom: 1px solid #e5e7eb;
    }}
    .section-body {{ padding: 20px 24px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="paper-info">
      <h1>📚 论文深度拆解报告</h1>
      <p><strong>标题：</strong>{title}</p>
      {f'<p><strong>作者：</strong>{author}</p>' if author else ''}
    </div>
    <div id="sections-container"></div>
  </div>
  
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    (function() {{
      var sectionsB64 = "{sections_b64}";
      var sectionsJson = atob(sectionsB64);
      var sectionsData = JSON.parse(decodeURIComponent(escape(sectionsJson)));
      
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: 'loose',
        theme: 'neutral'
      }});
      
      var container = document.getElementById('sections-container');
      sectionsData.forEach(function(section) {{
        var block = document.createElement('div');
        block.className = 'section-block';
        block.innerHTML = '<div class="section-header"><h2>' + section.module + '</h2><span>模型: ' + section.model + ' | 时间: ' + section.timestamp + '</span></div><div class="section-body"></div>';
        var body = block.querySelector('.section-body');
        body.innerHTML = marked.parse(section.result);
        container.appendChild(block);
      }});
    }})();
  </script>
</body>
</html>"""
    return html


# ─── 启动配置 ─────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
