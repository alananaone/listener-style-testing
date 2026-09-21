#!/usr/bin/env python3
"""
test_quiz_logic.py
全面測試計分模型與四象限映射演算法：
1. 8 題答題分數範圍 1~5，總分 2~10
2. 四種極端落點測試 (A, B, C, D)
3. 邊界條件 (E=T, N=C) 平局落點判定
4. 座標計算與 18% ~ 82% 觸壁保護
"""

def calculate_result(answers):
    E = answers.get('Q1', 0) + answers.get('Q2', 0)
    T = answers.get('Q3', 0) + answers.get('Q4', 0)
    N = answers.get('Q5', 0) + answers.get('Q6', 0)
    C = answers.get('Q7', 0) + answers.get('Q8', 0)

    # 風格歸類邏輯 (GEMINI.md)
    if E >= T and N >= C:
        style = 'A' # 陪伴聆聽者
    elif E >= T and C > N:
        style = 'B' # 覺察聆聽者
    elif T > E and N >= C:
        style = 'C' # 探索聆聽者
    else:
        style = 'D' # 行動聆聽者

    deltaX = C - N
    posX = 50 + (deltaX / 8) * 32
    posX = max(18, min(82, posX))

    deltaY = T - E
    posY = 50 + (deltaY / 8) * 32
    posY = max(18, min(82, posY))

    return style, E, T, N, C, posX, posY

def run_tests():
    print("=== 開始進行測驗演算法邊界與極端值單元測試 ===")

    # 測試 1：極端類型 A（情緒 + 培育最高）
    # Q1=5, Q2=5 (E=10), Q3=1, Q4=1 (T=2), Q5=5, Q6=5 (N=10), Q7=1, Q8=1 (C=2)
    s1, e1, t1, n1, c1, x1, y1 = calculate_result({'Q1':5, 'Q2':5, 'Q3':1, 'Q4':1, 'Q5':5, 'Q6':5, 'Q7':1, 'Q8':1})
    assert s1 == 'A', f"預期 A，但得到 {s1}"
    assert x1 == 18, f"X 軸極限應被 clamp 至 18%，但得到 {x1}"
    assert y1 == 18, f"Y 軸極限應被 clamp 至 18%，但得到 {y1}"
    print("[通過] 極端 A（陪伴聆聽者）落點 (18%, 18%) 邊界保護正確")

    # 測試 2：極端類型 B（情緒 + 督促最高）
    # E=10, T=2, N=2, C=10
    s2, e2, t2, n2, c2, x2, y2 = calculate_result({'Q1':5, 'Q2':5, 'Q3':1, 'Q4':1, 'Q5':1, 'Q6':1, 'Q7':5, 'Q8':5})
    assert s2 == 'B', f"預期 B，但得到 {s2}"
    assert x2 == 82, f"X 軸極限應被 clamp 至 82%，但得到 {x2}"
    assert y2 == 18, f"Y 軸極限應被 clamp 至 18%，但得到 {y2}"
    print("[通過] 極端 B（覺察聆聽者）落點 (82%, 18%) 邊界保護正確")

    # 測試 3：極端類型 C（事務 + 培育最高）
    # E=2, T=10, N=10, C=2
    s3, e3, t3, n3, c3, x3, y3 = calculate_result({'Q1':1, 'Q2':1, 'Q3':5, 'Q4':5, 'Q5':5, 'Q6':5, 'Q7':1, 'Q8':1})
    assert s3 == 'C', f"預期 C，但得到 {s3}"
    assert x3 == 18, f"X 軸極限應被 clamp 至 18%，但得到 {x3}"
    assert y3 == 82, f"Y 軸極限應被 clamp 至 82%，但得到 {y3}"
    print("[通過] 極端 C（探索聆聽者）落點 (18%, 82%) 邊界保護正確")

    # 測試 4：極端類型 D（事務 + 督促最高）
    # E=2, T=10, N=2, C=10
    s4, e4, t4, n4, c4, x4, y4 = calculate_result({'Q1':1, 'Q2':1, 'Q3':5, 'Q4':5, 'Q5':1, 'Q6':1, 'Q7':5, 'Q8':5})
    assert s4 == 'D', f"預期 D，但得到 {s4}"
    assert x4 == 82, f"X 軸極限應被 clamp 至 82%，但得到 {x4}"
    assert y4 == 82, f"Y 軸極限應被 clamp 至 82%，但得到 {y4}"
    print("[通過] 極端 D（行動聆聽者）落點 (82%, 82%) 邊界保護正確")

    # 測試 5：平局中心點 (全部選 3)
    # E=6, T=6, N=6, C=6
    s5, e5, t5, n5, c5, x5, y5 = calculate_result({'Q1':3, 'Q2':3, 'Q3':3, 'Q4':3, 'Q5':3, 'Q6':3, 'Q7':3, 'Q8':3})
    assert s5 == 'A', f"平局 E>=T, N>=C 規範應歸類為 A，得到 {s5}"
    assert x5 == 50, f"中心點 X 應為 50%，得到 {x5}"
    assert y5 == 50, f"中心點 Y 應為 50%，得到 {y5}"
    print("[通過] 平局中心點落點 (50%, 50%) 正確歸為類型 A")

    print("\n所有 5 組核心演算法與邊界測試全數 PASS！")

if __name__ == '__main__':
    run_tests()
