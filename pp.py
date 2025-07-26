import asyncio
from playwright.async_api import async_playwright
import aiohttp
from datetime import datetime
import json
import requests

API_URL = "https://ppv.to/api/streams"

ALLOWED_CATEGORIES = {
    "Wrestling", "Football", "Basketball", "Baseball", "Boxing"
}

async def get_streams():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            resp.raise_for_status()
            return await resp.json()

async def check_m3u8_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://veplay.top",
            "Origin": "https://veplay.top"
        }
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"❌ Error checking {url}: {e}")
        return False

async def grab_m3u8_from_iframe(page, iframe_url):
    found_streams = set()

    def handle_response(response):
        if ".m3u8" in response.url:
            found_streams.add(response.url)

    page.on("response", handle_response)
    print(f"🌐 Navigating to iframe: {iframe_url}")

    try:
        await page.goto(iframe_url, timeout=15000)
    except Exception as e:
        print(f"❌ Failed to load iframe: {e}")
        page.remove_listener("response", handle_response)
        return set()

    await asyncio.sleep(2)

    try:
        box = page.viewport_size or {"width": 1280, "height": 720}
        cx, cy = box["width"] / 2, box["height"] / 2
        for i in range(4):
            if found_streams:
                break
            print(f"🖱️ Click #{i + 1}")
            try:
                await page.mouse.click(cx, cy)
            except Exception:
                pass
            await asyncio.sleep(0.3)
    except Exception as e:
        print(f"❌ Mouse click error: {e}")

    print("⏳ Waiting 5s for final stream load...")
    await asyncio.sleep(5)
    page.remove_listener("response", handle_response)

    valid_urls = set()
    for url in found_streams:
        if await check_m3u8_url(url):
            valid_urls.add(url)
        else:
            print(f"❌ Invalid or unreachable URL: {url}")
    return valid_urls

async def main():
    data = await get_streams()
    streams = []

    # Filter out "24/7 Streams" and only keep allowed categories
    for category in data.get("streams", []):
        cat = category.get("category", "").strip()
        if cat not in ALLOWED_CATEGORIES:
            continue
        if cat == "24/7 Streams":
            continue  # explicitly exclude this category

        for stream in category.get("streams", []):
            iframe = stream.get("iframe")
            name = stream.get("name", "Unnamed Event")
            # Here we put dummy times/events, can be adapted if available from API
            streams.append({
                "name": name,
                "iframe": iframe,
                "category": cat,
                "time": "00:00",  # default placeholder
                "event": name
            })

    # Deduplicate streams by name (case-insensitive)
    seen_names = set()
    deduped_streams = []
    for s in streams:
        name_key = s["name"].strip().lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            deduped_streams.append(s)
    streams = deduped_streams

    if not streams:
        print("🚫 No valid streams found.")
        return

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        output = {}
        today = datetime.now().strftime("%A %dth %B %Y - Schedule Time UK GMT")
        output[today] = {"Soccer": []}

        for s in streams:
            print(f"\n🔍 Scraping: {s['name']} ({s['category']})")
            urls = await grab_m3u8_from_iframe(page, s["iframe"])
            if urls:
                channels = []
                for i, url in enumerate(urls, 1):
                    channels.append({
                        "name": f"Server-{i}",
                        "link": url,
                        "api": "",
                        "scheme": "0"
                    })
                output[today]["Soccer"].append({
                    "time": s["time"],
                    "event": s["event"],
                    "channels": channels,
                    "channels2": []
                })
                print(f"✅ Found {len(channels)} stream(s) for {s['name']}")
            else:
                print(f"❌ No valid .m3u8 streams found for {s['name']}")

        await browser.close()

    # POST data to your server (no saving)
    post_data = {
        "f_path": "ppv.json",
        "f_data": output
    }

    try:
        response = requests.post(
            "https://git.bdsajibx.workers.dev/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(post_data),
            timeout=15
        )
        if response.ok:
            print("✅ Data successfully posted to server.")
        else:
            print(f"❌ Failed to post data. Status code: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Exception during POST request: {e}")

if __name__ == "__main__":
    asyncio.run(main())
