"""
Mermaid 图表查看器 - 生成独立 HTML 文件
用法：python mermaid_viewer.py "graph TD\n A-->B"
    或：python mermaid_viewer.py input.md  (从文件读取)
"""
import sys
import io
import json
import os
import base64
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_html(mermaid_code: str) -> str:
    """生成包含 mermaid 图表的独立 HTML"""
    
    # 读取本地 mermaid.min.js
    js_path = Path(__file__).parent / "static" / "mermaid.min.js"
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            mermaid_js = f.read()
        js_tag = f"<script>\n{mermaid_js}\n</script>"
    else:
        # 回退到 CDN
        js_tag = '<script src="https://cdn.bootcdn.net/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Mermaid 图表</title>
<style>
body {{
  margin: 0;
  padding: 30px;
  font-family: system-ui, sans-serif;
  background: #f8fafc;
}}
.container {{
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  padding: 30px;
}}
h1 {{
  color: #1e293b;
  margin-bottom: 20px;
}}
#chart {{
  text-align: center;
  padding: 20px;
}}
.error {{
  background: #fef2f2;
  color: #dc2626;
  padding: 16px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
}}
.actions {{
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}}
button {{
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
}}
button:hover {{
  background: #2563eb;
}}
</style>
</head>
<body>
<div class="container">
<h1>📊 Mermaid 图表</h1>
<div id="chart">加载中...</div>
<div class="actions">
  <button onclick="downloadSVG()">📥 下载 SVG</button>
  <button onclick="downloadPNG()">🖼️ 下载 PNG</button>
  <button onclick="window.location.reload()">🔄 刷新</button>
</div>
</div>

{js_tag}

<script>
var code = {json.dumps(mermaid_code)};

function render() {{
  if (typeof mermaid === "undefined") {{
    setTimeout(render, 100);
    return;
  }}
  
  mermaid.initialize({{
    startOnLoad: false,
    securityLevel: "loose",
    theme: "base",
    themeVariables: {{
      primaryColor: "#3b82f6",
      primaryTextColor: "#fff",
      primaryBorderColor: "#2563eb",
      lineColor: "#64748b",
      fontSize: "14px"
    }},
    flowchart: {{ useMaxWidth: true }},
    sequence: {{ useMaxWidth: true }}
  }});
  
  var id = "m" + Date.now();
  mermaid.render(id, code).then(function(result) {{
    document.getElementById("chart").innerHTML = result.svg;
    if (result.bindFunctions) {{
      result.bindFunctions(document.getElementById("chart"));
    }}
  }}).catch(function(error) {{
    document.getElementById("chart").innerHTML = 
      '<div class="error">渲染错误: ' + 
      (error.message || String(error)).replace(/</g, '&lt;') + 
      '\\n\\n--- 代码 ---\\n' +
      code.replace(/</g, '&lt;') + '</div>';
  }});
}}

function downloadSVG() {{
  var svg = document.querySelector("#chart svg");
  if (!svg) {{ alert("没有图表可下载"); return; }}
  
  var data = new XMLSerializer().serializeToString(svg);
  var blob = new Blob([data], {{type: "image/svg+xml"}});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "mermaid-chart.svg";
  a.click();
  URL.revokeObjectURL(url);
}}

function downloadPNG() {{
  var svg = document.querySelector("#chart svg");
  if (!svg) {{ alert("没有图表可下载"); return; }}
  
  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext("2d");
  var data = new XMLSerializer().serializeToString(svg);
  var img = new Image();
  
  img.onload = function() {{
    canvas.width = img.width * 2;
    canvas.height = img.height * 2;
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    var a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = "mermaid-chart.png";
    a.click();
  }};
  
  img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(data)));
}}

render();
</script>
</body>
</html>'''
    
    return html


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n示例:")
        print('  python mermaid_viewer.py "graph TD\\n A-->B"')
        print('  python mermaid_viewer.py diagram.md')
        return
    
    # 获取输入
    arg = sys.argv[1]
    
    if os.path.exists(arg):
        # 从文件读取
        with open(arg, 'r', encoding='utf-8') as f:
            content = f.read()
        # 提取 mermaid 代码块
        import re
        blocks = re.findall(r'```mermaid\s*(.*?)```', content, re.DOTALL)
        if blocks:
            mermaid_code = blocks[0].strip()
        else:
            mermaid_code = content.strip()
    else:
        # 直接使用参数
        mermaid_code = arg.replace('\\n', '\n')
    
    # 生成 HTML
    html = create_html(mermaid_code)
    
    # 保存到文件
    output_path = Path(__file__).parent / "mermaid_output.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 已生成: {output_path}")
    print(f"📊 用浏览器打开查看图表")
    
    # 尝试自动打开浏览器
    import webbrowser
    webbrowser.open(f"file:///{output_path.absolute().as_posix()}")


if __name__ == "__main__":
    main()
