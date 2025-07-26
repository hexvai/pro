import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import datetime
import json

MIRRORS = [
    "https://fstv.space",
    "https://fstv.online",
    "https://fstv.us",
]

def get_live_match_links():
    matches = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for base_url in MIRRORS:
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️ Could not fetch from mirror {base_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        fixture_wrapper = soup.find("div", class_="fixtures-live-wrapper")
        if not fixture_wrapper:
            print(f"⚠️ No fixtures found in mirror {base_url}")
            continue

        for league in fixture_wrapper.find_all("div", class_="match-table-item"):
            league_name_tag = league.find("a", class_="league-name")
            league_name = league_name_tag.get_text(strip=True) if league_name_tag else "Unknown League"

            for row in league.find_all("div", class_="common-table-row"):
                onclick = row.get("onclick")
                if onclick and "window.location.href=" in onclick:
                    relative_link = onclick.split("'")[1]

                    domain = base_url.split("/live-tv.html")[0]
                    full_url = f"{domain}{relative_link}"

                    title_tag = row.find("a", class_="right-row")
                    event = title_tag.get_text(strip=True) if title_tag else "Unknown Event"
                    time_tag = row.find("span", class_="match-time")
                    time = time_tag.get_text(strip=True) if time_tag else "00:00"

                    matches.append({
                        "league": league_name,
                        "url": full_url,
                        "event": event,
                        "time": time
                    })
    return matches

async def extract_m3u8_from_match(page, url):
    try:
        await page.goto(url, timeout=20000)
        await page.wait_for_selector("button.btn-server", timeout=10000)
        buttons = await page.query_selector_all('button.btn-server')
        streams = []
        for btn in buttons:
            name = (await btn.text_content()).strip()
            link = await btn.get_attribute('data-link')
            if link and link.endswith(".m3u8"):
                streams.append({
                    "name": name,
                    "link": link,
                    "api": "",
                    "scheme": "0"
                })
        return streams
    except PlaywrightTimeoutError:
        return []
    except Exception:
        print(f"⚠️ Skipping URL due to error or navigation failure: {url}")
        return []

async def main():
    matches = get_live_match_links()
    if not matches:
        print("❌ No matches found across mirrors.")
        return

    output = {}
    today = datetime.datetime.now().strftime("%A %dth %B %Y - Schedule Time UK GMT")
    output[today] = {"Soccer": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for match in matches:
            print(f"🎯 Checking: {match['event']}")
            streams = await extract_m3u8_from_match(page, match["url"])
            if streams:
                output[today]["Soccer"].append({
                    "time": match["time"],
                    "event": match["event"],
                    "channels": streams,
                    "channels2": []
                })
                print(f"✅ Found {len(streams)} stream(s).")
            else:
                print("❌ No .m3u8 streams found.")

        await browser.close()

    # POST data to your server (no file saving)
    post_data = {
        "f_path": "fstv.json",
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
