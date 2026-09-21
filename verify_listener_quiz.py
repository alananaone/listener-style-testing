#!/usr/bin/env python3
"""
verify_listener_quiz.py
驗證聆聽者風格測驗專案的設計規範、鐵律與功能完整性。
"""

import re
import sys
from pathlib import Path

def test_file(file_path):
    content = Path(file_path).read_text(encoding='utf-8')
    errors = []
    warnings = []

    # 1. 鐵律：絕對禁止使用 Emoji
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
        "\U0001F680-\U0001F6FF"  # Transport and Map
        "\U0001F1E0-\U0001F1FF"  # Regional Indicator Symbols (Flags)
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002600-\U000026FF"  # Misc symbols (like ☀️, ⚡)
        "\U00002700-\U000027BF"  # Dingbats (like ✈️, ✉️)
        "]+",
        flags=re.UNICODE,
    )
    emoji_matches = emoji_pattern.findall(content)
    if emoji_matches:
        errors.append(f"發現未授權 Emoji：{set(emoji_matches)}")

    # 2. 鐵律：絕對禁止使用單向邊框 (border-left/top/right/bottom 與 Tailwind border-l/r/t/b)
    css_dir_border = re.findall(r"\bborder-(?:left|top|right|bottom)(?:-[a-z]+)?\s*:", content)
    if css_dir_border:
        errors.append(f"發現 CSS 單向邊框屬性：{css_dir_border}")

    tw_dir_border = re.findall(r"\bclass=['\"][^'\"]*\b(border-[trbl](?:-[a-z0-9/]+)?)\b", content)
    if tw_dir_border:
        errors.append(f"發現 Tailwind 單向邊框 class：{tw_dir_border}")

    # 3. 鐵律：中文語境（包含括號與標點）嚴格使用全形標點符號
    # 檢查中文相鄰的半形括號 ( )
    half_parens = re.findall(r"(?:[\u4e00-\u9fa5][^<>\n]*?\([^\n]*?[\u4e00-\u9fa5]|[\u4e00-\u9fa5][^\n]*?\))", content)
    # 過濾出明顯是中文標題/內文中的半形括號（排除 JS 程式碼區塊與 HTML 標籤屬性）
    # 分離出 HTML 標籤文字與 JS 逐一檢查
    html_text_lines = []
    in_script = False
    for line in content.splitlines():
        if '<script' in line:
            in_script = True
        if '</script>' in line:
            in_script = False
            continue
        if not in_script:
            # 移除 html tags
            clean_line = re.sub(r'<[^>]+>', ' ', line).strip()
            if clean_line:
                html_text_lines.append(clean_line)

    for line in html_text_lines:
        # 檢查中文旁是否有半形括號
        if re.search(r"[\u4e00-\u9fa5]\s*\([^\)]*?\)", line) or re.search(r"\([^\)]*?[\u4e00-\u9fa5]\)", line) or re.search(r"\([^\)]*?\)\s*[\u4e00-\u9fa5]", line):
            errors.append(f"HTML 內文中發現中文半形括號：{line}")
        # 檢查中文句子結尾或中間的半形驚嘆號、問號、冒號、逗號
        if re.search(r"[\u4e00-\u9fa5][,!?:]", line):
            errors.append(f"HTML 內文中發現半形標點符號：{line}")

    # 4. 題庫與核心邏輯檢查
    required_keys = ['rawQuestions', 'scaleOptions', 'styleProfiles', 'shuffleQuestions', 'deltaX', 'deltaY', 'posX', 'posY', 'html2canvas', 'forms.gle']
    for k in required_keys:
        if k not in content:
            errors.append(f"缺少關鍵功能或演算法標識：{k}")

    # 5. 檢查是否有怪異無質感的灰色文字 (#6b7280)
    if '#6b7280' in content or 'text-brand-muted' in content:
        warnings.append("偵測到舊版可能存在的冷灰色 (#6b7280 或 text-brand-muted)，請確保文字具有良好溫度與對比度")

    print(f"=== 檢驗報告：{file_path} ===")
    if errors:
        print(f"FAILED: 發現 {len(errors)} 個致命違規：")
        for err in errors:
            print(f"  - {err}")
    else:
        print("PASSED: 全域約束審核完全通過！零單向邊框、零 Emoji、全形標點符合標準！")

    if warnings:
        print(f"WARNINGS: {len(warnings)} 項建議優化：")
        for w in warnings:
            print(f"  - {w}")

    return len(errors) == 0

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    success = test_file(target)
    sys.exit(0 if success else 1)
