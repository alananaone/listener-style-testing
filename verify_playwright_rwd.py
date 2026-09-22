import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        cwd = os.getcwd()
        file_url = f"file://{cwd}/index.html"

        print("=== 1. 測試手機端 RWD (375 x 812) ===")
        context_mobile = await browser.new_context(
            viewport={"width": 375, "height": 812},
            device_scale_factor=2
        )
        page_m = await context_mobile.new_page()
        await page_m.goto(file_url)
        await page_m.wait_for_timeout(500)

        # 檢查首頁是否出現水平捲動
        scroll_width_m = await page_m.evaluate("document.documentElement.scrollWidth")
        print(f"手機端首頁 scrollWidth: {scroll_width_m}px (螢幕寬度: 375px)")
        assert scroll_width_m <= 375, f"手機端首頁出現水平溢出！scrollWidth = {scroll_width_m}"

        await page_m.screenshot(path="screenshot_mobile_hero_new.png", full_page=False)
        print("已截圖：screenshot_mobile_hero_new.png")

        # 點擊開始測驗滾動至第一題
        start_btn = page_m.locator("#btn-start-quiz-hero")
        await start_btn.click()
        await page_m.wait_for_timeout(600)

        # 檢查 slide-q-0 是否存在且可見
        q0_visible = await page_m.locator("#slide-q-0").is_visible()
        print(f"第一題切片 slide-q-0 顯示狀態: {q0_visible}")
        assert q0_visible, "點擊開始測驗後，第一題切片應存在並顯示"

        await page_m.screenshot(path="screenshot_mobile_q1_new.png", full_page=False)
        print("已截圖：screenshot_mobile_q1_new.png")

        # 作答 8 題
        for idx in range(8):
            slide_loc = page_m.locator(f"#slide-q-{idx}")
            # 選第 5 個選項（這完全就是我）
            opt_btn = slide_loc.locator('.btn-option-card').nth(4)
            await opt_btn.click()
            await page_m.wait_for_timeout(350)

        # 等待加載過渡並揭曉結果
        await page_m.wait_for_selector("#panel-result:not(.hidden)", timeout=4000)
        await page_m.wait_for_timeout(600)

        result_visible = await page_m.locator("#panel-result").is_visible()
        assert result_visible, "完成 8 題後，結果頁應顯示"

        # 檢查手機端結果頁水平溢出
        res_scroll_width_m = await page_m.evaluate("document.documentElement.scrollWidth")
        print(f"手機端結果頁 scrollWidth: {res_scroll_width_m}px (螢幕寬度: 375px)")
        assert res_scroll_width_m <= 375, f"手機端結果頁出現水平溢出！scrollWidth = {res_scroll_width_m}"

        await page_m.screenshot(path="screenshot_mobile_result_new.png", full_page=False)
        print("已截圖：screenshot_mobile_result_new.png")

        # 點擊 3D 翻轉卡片
        flip_card = page_m.locator("#style-flip-card")
        await flip_card.click()
        await page_m.wait_for_timeout(400)
        await page_m.screenshot(path="screenshot_mobile_result_flipped.png", full_page=False)
        print("已截圖：screenshot_mobile_result_flipped.png")

        await context_mobile.close()

        print("\n=== 2. 測試桌面端 RWD (1280 x 800) ===")
        context_desktop = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2
        )
        page_d = await context_desktop.new_page()
        await page_d.goto(file_url)
        await page_d.wait_for_timeout(500)

        await page_d.screenshot(path="screenshot_desktop_hero_new.png", full_page=False)
        print("已截圖：screenshot_desktop_hero_new.png")

        # 開始測驗並作答
        await page_d.locator("#btn-start-quiz-hero").click()
        await page_d.wait_for_timeout(300)

        for idx in range(8):
            slide_loc = page_d.locator(f"#slide-q-{idx}")
            # 依序選擇第 1 個選項或不同選項
            opt_btn = slide_loc.locator('.btn-option-card').nth(idx % 5)
            await opt_btn.click()
            await page_d.wait_for_timeout(300)

        await page_d.wait_for_selector("#panel-result:not(.hidden)", timeout=4000)
        await page_d.wait_for_timeout(600)

        await page_d.screenshot(path="screenshot_desktop_result_new.png", full_page=False)
        print("已截圖：screenshot_desktop_result_new.png")

        # 翻轉卡片
        await page_d.locator("#style-flip-card").click()
        await page_d.wait_for_timeout(400)
        await page_d.screenshot(path="screenshot_desktop_result_flipped.png", full_page=False)
        print("已截圖：screenshot_desktop_result_flipped.png")

        await context_desktop.close()
        await browser.close()
        print("\n所有 Playwright 視覺與 RWD 端到端測試圓滿完成！")

if __name__ == '__main__':
    asyncio.run(run())
