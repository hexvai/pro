import asyncio
import json
from playwright.async_api import async_playwright

TARGET_COOKIE_NAME = "Edge-Cache-Cookie"
TARGET_URL = "https://toffeelive.com/en/watch/xi6xX5UBv9knK3AH9aMk"

async def capture_specific_cookie():
    async with async_playwright() as p:
        # Launch browser in headless mode (important for Codespaces)
        browser = await p.chromium.launch(
            headless=True,  # ✅ Set to True for server environments
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        )

        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1366, 'height': 768}
        )

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

            # Fallback: try to get the cookie from browser storage
            if not target_cookie:
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] == TARGET_COOKIE_NAME:
                        target_cookie = f"{cookie['name']}={cookie['value']}"
                        break

            if target_cookie:
                print("\n🎯 Target Cookie Found:")
                print(target_cookie)

                # Parse the cookie parts if it's in delimited format (optional)
                if ":" in target_cookie:
                    try:
                        cookie_value = target_cookie.split("=", 1)[1]
                        cookie_parts = dict(
                            part.split('=', 1) if '=' in part else (part, True)
                            for part in cookie_value.split(':')
                        )
                        print("\n🔍 Decoded Components:")
                        for key, value in cookie_parts.items():
                            print(f"{key.ljust(15)}: {value}")
                    except Exception as parse_err:
                        print(f"⚠️ Error parsing cookie: {parse_err}")

                return target_cookie
            else:
                print("❌ Target cookie not found")
                return None

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            return None
        finally:
            await browser.close()

async def main():
    cookie = await capture_specific_cookie()
    if cookie:
        with open("edge_cache_cookie.txt", "w") as f:
            f.write(cookie)
        print("\n✅ Cookie saved to edge_cache_cookie.txt")

if __name__ == "__main__":
    asyncio.run(main())
