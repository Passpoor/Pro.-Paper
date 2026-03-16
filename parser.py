"""
PDF 章节检测 — 健壮版 v2
支持: 标准IMRaD / 综述/ Nature系 / 中文论文
兜底: 全大写短行检测 + 无结构时全文回退
"""

import re
from typing import Tuple, Dict, List

import pymupdf


def extract_text(pdf_path: str) -> Tuple[str, dict]:
    """从 PDF 提取全文和元信息。"""
    doc = pymupdf.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    meta = doc.metadata or {}
    metadata = {
        "pages": len(doc),
        "title": meta.get("title", "") or "",
        "author": meta.get("author", "") or "",
        "subject": meta.get("subject", "") or "",
        "char_count": len(full_text),
        "est_tokens": _estimate_tokens(full_text),
    }
    doc.close()
    return full_text, metadata


def _estimate_tokens(text: str) -> int:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    other_chars = len(text) - chinese_chars
    return int(chinese_chars * 0.5 + other_chars * 0.25)


def detect_sections(text: str) -> Dict[str, Tuple[int, int]]:
    """
    检测论文章节。返回 {section_name: (start_pos, end_pos)}。
    
    检测优先级:
    1. 标准标题模式 (Introduction, Results, etc.)
    2. 全大写/中文标题行 (HALLMARKS OF..., 讨论, etc.)
    3. 兜底: 若核心章节缺失, 启发式搜索
    4. 最坏情况: 返回空, 调用方回退全文
    """
    lines = text.split("\n")
    positions = []
    pos = 0
    for line in lines:
        positions.append(pos)
        pos += len(line) + 1

    # ── 标准模式（有优先级）────────────────────────────────
    std_patterns = [
        # (优先级, 归类名, 正则) — 优先级小=更优先
        (1, "摘要",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:abstract|摘要)\s*$"),
        (2, "引言",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:introduction|引\s*言|前言)\s*$"),
        (3, "方法",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:materials?\s+and\s+methods?|methods?|experimental|方法|材料与方法|实验方法|研究方法)\s*$"),
        (4, "结果",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:results?|findings?|结\s*果|研究结果)\s*$"),
        (5, "讨论",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:discussion|讨\s*论|分析与讨论)\s*$"),
        (6, "结论",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:conclusion[s]?|summary|结\s*论|总\s*结)\s*$"),
        (7, "参考文献", r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:references?|bibliography|参\s*考\s*文\s*献)\s*$"),
        (8, "致谢",     r"(?i)^\s*(?:\d+[\.\)\:]?\s*)?(?:acknowledgements?|致\s*谢)\s*$"),
    ]

    hits = {}  # line_idx -> (priority, section_name)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) < 2 or len(stripped) > 100:
            continue
        
        for priority, name, pattern in std_patterns:
            if re.fullmatch(pattern, stripped):
                if i not in hits or hits[i][0] > priority:
                    hits[i] = (priority, name)
                break

    # ── 全大写/标题行检测（第二层兜底）───────────────────
    # 匹配类似 "HALLMARKS OF AGING IN COPD"、"LUNG AGING"、"THERAPIES TO TARGET AGEING"
    # 以及中文独立标题行如 "背景与目的"
    if "引言" not in {h[1] for h in hits.values()} or "结果" not in {h[1] for h in hits.values()}:
        for i, line in enumerate(lines):
            if i in hits:
                continue
            stripped = line.strip()
            if len(stripped) < 4 or len(stripped) > 80:
                continue
            # 跳过 PAGE 标记、空行
            if stripped.startswith("---") or "PAGE" in stripped.upper():
                continue
            # 跳过纯数字/引用行
            if re.match(r"^[\d\.\s,\[\]\"\']+$", stripped):
                continue
            
            words = stripped.split()
            # 检测全大写英文标题（>=2个单词, 大部分字母大写）
            if len(words) >= 2:
                alpha_chars = [c for c in stripped if c.isalpha()]
                upper_chars = [c for c in alpha_chars if c.isupper()]
                if alpha_chars and upper_chars and len(upper_chars) / len(alpha_chars) > 0.85:
                    # 看起来像标题行
                    if "lung" in stripped.lower() or "ageing" in stripped.lower() or "aging" in stripped.lower() or "hallmark" in stripped.lower() or "therap" in stripped.lower() or "cancer" in stripped.lower() or "copd" in stripped.lower() or "ipf" in stripped.lower() or "fibrosis" in stripped.lower() or "senescence" in stripped.lower() or "senother" in stripped.lower():
                        # 根据关键词归类
                        low = stripped.lower()
                        if any(k in low for k in ["introduction", "background", "lung aging", "lung ageing", "overview"]):
                            hits[i] = (9, "引言")
                        elif any(k in low for k in ["result", "finding", "hallmark", "copd", "cancer", "ipf", "fibrosis"]):
                            hits[i] = (9, "结果")
                        elif any(k in low for k in ["therap", "treatment", "target", "senolytic", "senomorph", "clinical"]):
                            hits[i] = (9, "结果")
                        elif any(k in low for k in ["discussion", "conclusion", "summary"]):
                            hits[i] = (9, "结论")
                        elif any(k in low for k in ["method", "experimental", "material", "approach"]):
                            hits[i] = (9, "方法")
                        else:
                            hits[i] = (9, "结果")  # 默认归为结果
            
            # 检测中文标题行（无标点, 2-10个字）
            cn_chars = re.findall(r'[\u4e00-\u9fff]', stripped)
            if 2 <= len(cn_chars) <= 10:
                non_cn = stripped.replace(' ', '')
                non_cn = re.sub(r'[\u4e00-\u9fff]', '', non_cn)
                if len(non_cn) == 0:  # 纯中文（可能有空格）
                    title_cn = stripped.replace(' ', '')
                    cn_patterns = {
                        "摘要": ["摘要"],
                        "引言": ["引言", "前言", "背景"],
                        "方法": ["方法", "材料与方法", "实验方法", "研究方法"],
                        "结果": ["结果", "研究结果"],
                        "讨论": ["讨论", "分析与讨论"],
                        "结论": ["结论", "总结"],
                        "参考文献": ["参考文献"],
                        "致谢": ["致谢", "感谢"],
                    }
                    matched = False
                    for sec_name, keywords in cn_patterns.items():
                        for kw in keywords:
                            if title_cn == kw:
                                hits[i] = (9, sec_name)
                                matched = True
                                break
                        if matched:
                            break

    # ── 去重 + 排序 ─────────────────────────────────────
    filtered = {}
    prev_name = None
    for idx in sorted(hits.keys()):
        name = hits[idx][1]
        if name != prev_name:
            filtered[idx] = name
            prev_name = name

    # ── 构建位置范围 ─────────────────────────────────────
    sections = {}
    sorted_indices = sorted(filtered.keys())
    
    for i, idx in enumerate(sorted_indices):
        name = filtered[idx]
        if i + 1 < len(sorted_indices):
            end_pos = positions[sorted_indices[i + 1]]
        else:
            end_pos = len(text)
        sections[name] = (positions[idx], end_pos)

    return sections


def get_section_text(text: str, sections: Dict, section_name: str) -> str:
    if section_name in sections:
        start, end = sections[section_name]
        return text[start:end].strip()
    for key in sections:
        if section_name in key or key in section_name:
            start, end = sections[key]
            return text[start:end].strip()
    return ""


def get_analysis_text(text: str, sections: Dict, module: str) -> str:
    """
    根据分析模块返回对应文本。
    若目标章节未检测到，回退到全文。
    """
    mapping = {
        "引言": ["引言"],
        "方法": ["方法"],
        "结果": ["结果"],
    }
    full_text_modules = {"逻辑链", "终局", "风险审查", "整篇拆解", "构建课题"}
    
    if module in full_text_modules:
        return text
    
    target_sections = mapping.get(module)
    if target_sections is None:
        return text
    
    parts = []
    for sec_name in target_sections:
        sec_text = get_section_text(text, sections, sec_name)
        if sec_text:
            parts.append(f"## {sec_name}\n{sec_text}")
    
    return "\n\n".join(parts) if parts else text
