from playwright.async_api import async_playwright

_playwright = None
_browser = None


async def start_browser():
    global _playwright, _browser
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()


async def stop_browser():
    global _playwright, _browser
    if _browser is not None:
        await _browser.close()
        _browser = None
    if _playwright is not None:
        await _playwright.stop()
        _playwright = None


async def render_pdf(html: str) -> bytes:
    page = await _browser.new_page()
    try:
        await page.set_content(html, wait_until="networkidle")
        await page.emulate_media(media="print")
        return await page.pdf(
            format="A4",
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            print_background=True,
        )
    finally:
        await page.close()
