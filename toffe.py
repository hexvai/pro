import asyncio
from playwright.async_api import async_playwright

TARGET_COOKIE_NAME = "Edge-Cache-Cookie"
TARGET_URL = "https://toffeelive.com/en/watch/xi6xX5UBv9knK3AH9aMk"
POST_URL = "https://tf-hex.bdsajibx.workers.dev/"

async def capture_cookie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        target_cookie = None

        def log_request(request):
            nonlocal target_cookie
            cookies = request.headers.get("cookie", "")
            if TARGET_COOKIE_NAME in cookies:
                for c in cookies.split(";"):
                    if c.strip().startswith(TARGET_COOKIE_NAME):
                        target_cookie = c.strip()

        page.on("request", log_request)

        print(f"🌐 Navigating to {TARGET_URL} ...")
        await page.goto(TARGET_URL, wait_until="networkidle")

        # Fallback if no cookie found from requests
        if not target_cookie:
            cookies = await context.cookies()
            for c in cookies:
                if c["name"] == TARGET_COOKIE_NAME:
                    target_cookie = f'{c["name"]}={c["value"]}'

        await browser.close()
        return target_cookie

async def post_cookie(cookie):
    async with httpx.AsyncClient() as client:
        data = {"cookie": cookie}
        print(f"📤 Sending POST request with data:\n{data}")
        response = await client.post(POST_URL, json=data)
        print(f"📬 POST response status: {response.status_code}")
        print(f"📬 POST response body: {response.text}")

async def main():
    cookie = await capture_cookie()
    if cookie:
        print(f"✅ Captured cookie: {cookie}")
        await post_cookie(cookie)
    else:
        print("❌ No cookie captured")

if __name__ == "__main__":
    asyncio.run(main())
