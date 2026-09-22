#!/usr/bin/env python3
"""
audit_subagent.py
Sub-Agent 100 分制冷酷審核打分器（門檻 88 分）
維度一：去樣板化與突破框架 (Anti-Templating & De-carding, 25 分)
維度二：材質工藝與排版細節 (Craft, Typography & Material, 25 分)
維度三：情緒共鳴與「我在乎你」體驗 (Emotional Resonance & Care, 25 分)
維度四：代碼健壯性與約束鐵律 (Code Robustness & Iron Rules, 25 分)
"""

import re
import sys
from pathlib import Path

def run_subagent_audit(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"錯誤：找不到檔案 {file_path}")
        return 0, {}

    content = path.read_text(encoding='utf-8')
    scores = {
        'anti_templating': 25,
        'craft_typography': 25,
        'emotional_resonance': 25,
        'code_robustness': 25
    }
    deductions = {
        'anti_templating': [],
        'craft_typography': [],
        'emotional_resonance': [],
        'code_robustness': []
    }

    # -------------------------------------------------------------
    # 維度一：去樣板化與突破框架 (25 分)
    # -------------------------------------------------------------
    # 1. 檢查是否有灰色邊框卡片 (例如 border-gray, border-navy/10, border border-...)
    gray_border_cards = re.findall(r"class=['\"][^'\"]*?\bborder\s+border-(?:gray|navy|slate)[^'\"]*?['\"]", content)
    if gray_border_cards:
        penalty = min(8, len(gray_border_cards) * 2)
        scores['anti_templating'] -= penalty
        deductions['anti_templating'].append(f"發現 {len(gray_border_cards)} 處灰色邊框方塊卡片（扣 {penalty} 分）")

    # 2. 檢查是否有過多膠囊徽章 (badge overload: px-2 py-0.5 rounded-full bg-...)
    badge_patterns = re.findall(r"class=['\"][^'\"]*?rounded-full\s+bg-(?:brand|white|gray)[^'\"]*?text-(?:xs|\[\d+px\])[^'\"]*?['\"]", content)
    # 扣除按鈕本體，只算純文字標籤
    tag_badges = [b for b in badge_patterns if 'button' not in b.lower() and 'btn' not in b.lower()]
    if len(tag_badges) > 4:
        penalty = min(5, (len(tag_badges) - 4) * 2)
        scores['anti_templating'] -= penalty
        deductions['anti_templating'].append(f"偵測到 {len(tag_badges)} 個裝飾性膠囊 Badge，存在徽章氾濫跡象（扣 {penalty} 分）")

    # 3. 檢查是否包含怪異的 AI 手繪裝飾 SVG 圖片 (非 icon)
    weird_svg_art = re.findall(r"<svg[^>]*?viewBox[^>]*?>[\s\S]*?(?:<path[^>]*?d=['\"][MC][^'\"]{60,}['\"][^>]*?>[\s\S]*?){3,}</svg>", content)
    if weird_svg_art:
        scores['anti_templating'] -= 6
        deductions['anti_templating'].append("偵測到複雜手繪裝飾 SVG 插圖，違反不繪製奇怪裝飾圖片要求（扣 6 分）")

    # 4. 檢查是否有開放式呼吸佈局與柔光球背景
    if 'ambient-glow' not in content and 'radial-gradient' not in content:
        scores['anti_templating'] -= 4
        deductions['anti_templating'].append("缺少氛圍感背景光暈或有機過渡，版面可能顯得單調平鋪（扣 4 分）")

    # -------------------------------------------------------------
    # 維度二：材質工藝與排版細節 (25 分)
    # -------------------------------------------------------------
    # 1. 檢查是否有死灰、冷灰色文字 (#6b7280)
    if '#6b7280' in content:
        scores['craft_typography'] -= 4
        deductions['craft_typography'].append("使用預設冷灰色 #6b7280，缺乏溫潤質感（扣 4 分）")

    # 2. 檢查是否有過小字級 (text-[9px] 或 text-[10px])
    tiny_fonts = re.findall(r"text-\[(?:9|10)px\]", content)
    if tiny_fonts:
        penalty = min(4, len(tiny_fonts) * 2)
        scores['craft_typography'] -= penalty
        deductions['craft_typography'].append(f"出現 {len(tiny_fonts)} 處過小字級（<= 10px），影響長輩與手機閱讀易讀性（扣 {penalty} 分）")

    # 3. 檢查排版字型是否依據最新指示精準配置（Nunito + 源泉圓體 / GenSenRounded）
    if 'Nunito' not in content or ('GenSenRounded' not in content and '源泉' not in content):
        scores['craft_typography'] -= 3
        deductions['craft_typography'].append("缺少指定字型（Nunito 或 源泉圓體），字體規範未落實（扣 3 分）")

    # 4. 檢查是否有 hover、active 與 focus-visible 三態覆蓋
    has_hover = ':hover' in content or 'hover:' in content
    has_active = ':active' in content or 'active:' in content
    has_focus = 'focus-visible' in content or ':focus' in content
    if not (has_hover and has_active and has_focus):
        scores['craft_typography'] -= 4
        deductions['craft_typography'].append("互動三態未完全覆蓋（hover, active, focus-visible）（扣 4 分）")

    # 5. 檢查是否有減動支援 prefers-reduced-motion
    if 'prefers-reduced-motion' not in content:
        scores['craft_typography'] -= 2
        deductions['craft_typography'].append("缺少 prefers-reduced-motion 減動媒體查詢（扣 2 分）")

    # -------------------------------------------------------------
    # 維度三：情緒共鳴與「我在乎你」體驗 (25 分)
    # -------------------------------------------------------------
    # 1. 溫柔文案與陪伴感檢查
    care_keywords = ['溫柔', '在場', '陪伴', '心理安全感', '傾聽他人，也照顧自己']
    found_keywords = [k for k in care_keywords if k in content]
    if len(found_keywords) < 3:
        scores['emotional_resonance'] -= 4
        deductions['emotional_resonance'].append("核心溫柔陪伴文案不足，無法充分傳達「我在乎你」的容器感（扣 4 分）")

    # 2. 傾聽者視覺呈現（使用者明確指示：大標題上方使用 1.png 標誌圖片，卡片使用中央雙圓交疊標誌）
    if '1.png' not in content:
        scores['emotional_resonance'] -= 5
        deductions['emotional_resonance'].append("大標題上方缺少指定的 1.png 官方標誌（扣 5 分）")
    if 'svg' not in content.lower():
        scores['emotional_resonance'] -= 4
        deductions['emotional_resonance'].append("缺少純 SVG 視覺化圖騰呈現（扣 4 分）")

    # 3. 象限落點動畫與視覺層次
    if 'pin-ring' not in content and 'pulse' not in content:
        scores['emotional_resonance'] -= 3
        deductions['emotional_resonance'].append("羅盤座標指示點缺少生動的脈衝波紋或動態光暈（扣 3 分）")

    # 4. 流暢沉浸作答體驗（自動推進、上一題、進度條）
    if 'btn-quiz-prev' not in content or 'quiz-progress-bar' not in content:
        scores['emotional_resonance'] -= 5
        deductions['emotional_resonance'].append("測驗作答流程缺少流暢的進度追蹤或上一題回退機制（扣 5 分）")

    # -------------------------------------------------------------
    # 維度四：代碼健壯性與約束鐵律 (25 分)
    # -------------------------------------------------------------
    # 1. 鐵律：絕對禁止使用 Emoji
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
        "]+",
        flags=re.UNICODE,
    )
    emojis = emoji_pattern.findall(content)
    if emojis:
        scores['code_robustness'] -= 10
        deductions['code_robustness'].append(f"【致命違規】發現未授權 Emoji {len(emojis)} 處：{set(emojis)}（扣 10 分）")

    # 2. 鐵律：絕對禁止使用單向邊框 (border-left/top/right/bottom)
    dir_borders = re.findall(r"\bborder-(?:left|top|right|bottom)(?:-[a-z]+)?\s*:", content)
    tw_borders = re.findall(r"\bclass=['\"][^'\"]*\b(border-[trbl](?:-[a-z0-9/]+)?)\b", content)
    if dir_borders or tw_borders:
        scores['code_robustness'] -= 10
        deductions['code_robustness'].append(f"【致命違規】發現單向邊框（CSS: {dir_borders}, Tailwind: {tw_borders}）（扣 10 分）")

    # 3. 鐵律：中文語境（包含括號）嚴格使用全形標點符號
    # 逐行檢查 HTML 文字中的半形括號
    in_script = False
    half_paren_violations = []
    for line in content.splitlines():
        if '<script' in line:
            in_script = True
        if '</script>' in line:
            in_script = False
            continue
        if not in_script:
            clean_line = re.sub(r'<[^>]+>', ' ', line).strip()
            if re.search(r"[\u4e00-\u9fa5]\s*\([^\)]*?\)", clean_line) or re.search(r"\([^\)]*?[\u4e00-\u9fa5]\)", clean_line):
                half_paren_violations.append(clean_line)

    if half_paren_violations:
        scores['code_robustness'] -= 6
        deductions['code_robustness'].append(f"【標點違規】HTML 中文語境發現半形括號：{half_paren_violations[:2]}（扣 6 分）")

    # 4. 核心演算法檢查 (Fisher-Yates, 象限 18%-82% 保護)
    if 'Math.max(18, Math.min(82' not in content:
        scores['code_robustness'] -= 5
        deductions['code_robustness'].append("象限指示點缺少 18%～82% 觸壁邊界保護演算法（扣 5 分）")

    # 5. 圖片 alt 屬性完整性
    img_tags = re.findall(r"<img[^>]*?>", content)
    missing_alt = [img for img in img_tags if 'alt=' not in img]
    if missing_alt:
        scores['code_robustness'] -= 3
        deductions['code_robustness'].append(f"有 {len(missing_alt)} 張圖片缺少 alt 屬性（扣 3 分）")

    # 計算總分
    total_score = sum(scores.values())

    print("================================================================")
    print("      Sub-Agent 冷酷審核 100 分制打分報告（合格門檻：88 分）       ")
    print("================================================================")
    print(f"總分：{total_score} / 100 分（{'審核通過 (PASSED)' if total_score >= 88 else '審核未通過 (FAILED)'}）\n")
    
    dim_names = {
        'anti_templating': '維度一：去樣板化與突破框架 (25 分)',
        'craft_typography': '維度二：材質工藝與排版細節 (25 分)',
        'emotional_resonance': '維度三：情緒共鳴與「我在乎你」體驗 (25 分)',
        'code_robustness': '維度四：代碼健壯性與約束鐵律 (25 分)'
    }

    for k, name in dim_names.items():
        print(f"【{name}】得分：{scores[k]} / 25")
        if deductions[k]:
            for d in deductions[k]:
                print(f"  - 扣分項：{d}")
        else:
            print("  + 項目全數通過，無扣分項！")
        print()

    return total_score, deductions

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    total_score, _ = run_subagent_audit(target)
    sys.exit(0 if total_score >= 88 else 1)
