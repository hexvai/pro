import asyncio
import json
import httpx  # Fast async HTTP client
from playwright.async_api import async_playwright

TARGET_COOKIE_NAME = "Edge-Cache-Cookie"
TARGET_URL = "https://toffeelive.com/en/watch/xi6xX5UBv9knK3AH9aMk"
POST_ENDPOINT = "https://tf-hex.bdsajibx.workers.dev/"

async def capture_specific_cookie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        )

        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        target_cookie = None

        def log_request(request):
            nonlocal target_cookie
            if TARGET_COOKIE_NAME in request.headers.get('cookie', ''):
                cookie_header = request.headers['cookie']
                for cookie in cookie_header.split(';'):
                    if cookie.strip().startswith(TARGET_COOKIE_NAME):
                        target_cookie = cookie.strip()
                        break

        page.on('request', log_request)

        try:
            print(f"🌐 Navigating to {TARGET_URL}...")
            await page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")

            if not target_cookie:
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] == TARGET_COOKIE_NAME:
                        target_cookie = f"{cookie['name']}={cookie['value']}"
                        break

            if target_cookie:
                print("\n🎯 Target Cookie Found:")
                print(target_cookie)
                return target_cookie
            else:
                print("❌ Target cookie not found")
                return None

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            return None
        finally:
            await browser.close()

async def send_post_request(cookie_value):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                POST_ENDPOINT,
                headers={"Content-Type": "application/json"},
                json={"cookie": cookie_value}
            )
            print(f"📬 POST response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"⚠️ Failed to POST cookie: {e}")

async def main():
    cookie = await capture_specific_cookie()
    if cookie:
        await send_post_request(cookie)

if __name__ == "__main__":
    asyncio.run(main())
