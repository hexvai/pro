import asyncio
from playwright.async_api import async_playwright
import httpx

TARGET_COOKIE_NAME = "Edge-Cache-Cookie"
TARGET_URL = "https://toffeelive.com/en/watch/xi6xX5UBv9knK3AH9aMk"
POST_URL = "https://tf-hex.bdsajibx.workers.dev/"

async def capture_cookie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        target_cookie = None

        # Intercept requests to check headers
        def log_request(request):
            nonlocal target_cookie
            cookies = request.headers.get("cookie", "")
            if TARGET_COOKIE_NAME in cookies:
                for c in cookies.split(";"):
                    if c.strip().startswith(TARGET_COOKIE_NAME):
                        target_cookie = c.strip()
                        print(f"🔍 Found cookie in request: {target_cookie}")

        page.on("request", log_request)

        try:
            print(f"🌐 Navigating to {TARGET_URL} ...")
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)

            # Fallback: Get cookies directly from context
            if not target_cookie:
                all_cookies = await context.cookies()
                for c in all_cookies:
                    if c["name"] == TARGET_COOKIE_NAME:
                        target_cookie = f'{c["name"]}={c["value"]}'
                        print(f"🔍 Found cookie in context: {target_cookie}")
                        break
        except Exception as e:
            print(f"⚠️ Error while navigating: {e}")
        finally:
            await browser.close()

        return target_cookie

async def post_cookie(cookie):
    try:
        async with httpx.AsyncClient() as client:
            data = {"cookie": cookie}
            print(f"📤 Sending POST request with data:\n{data}")
            response = await client.post(POST_URL, json=data)
            print(f"📬 POST response status: {response.status_code}")
            print(f"📬 POST response body: {response.text}")
    except Exception as e:
        print(f"⚠️ Failed to post cookie: {e}")

async def main():
    cookie = await capture_cookie()
    if cookie:
        print(f"✅ Captured cookie: {cookie}")
        await post_cookie(cookie)
    else:
        print("❌ No cookie captured")

if __name__ == "__main__":
    asyncio.run(main())
