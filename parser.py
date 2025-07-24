import json
import urllib.request
import requests

# Step 1: Fetch data
url = "https://dlhd.click/schedule/schedule-generated.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://dlhd.click/"
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())

# Step 2: Extract only "Soccer" events
output = {}
for day_key, categories in data.items():
    output[day_key] = {"Soccer": []}
    for events in categories.values():
        for event in events:
            new_event = {
                "time": event.get("time"),
                "event": event.get("event"),
                "channels": [
                    {
                        "name": ch["channel_name"],
                        "link": f"http://drewlive24.duckdns.org:4123?url=https://ddy6new.newkso.ru/ddy6/premium{ch['channel_id']}/mono.m3u8&data=T3JpZ2luPWh0dHBzOi8vZm9yY2VkdG9wbGF5Lnh5enxSZWZlcmVyPWh0dHBzOi8vZm9yY2VkdG9wbGF5Lnh5ei98VXNlci1hZ2VudD1Nb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0OyBydjoxMzkuMCkgR2Vja28vMjAxMDAxMDEgRmlyZWZveC8xMzkuMHxPcmlnaW49aHR0cHM6Ly9mb3JjZWR0b3BsYXkueHl6fFJlZmVyZXI9aHR0cHM6Ly9mb3JjZWR0b3BsYXkueHl6L3xVc2VyLWFnZW50PU1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEzOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEzOS4w",
                        "api": "",
                        "scheme": "0"
                    }
                    for ch in event.get("channels", [])
                ],
                "channels2": [
                    {
                        "name": ch2["channel_name"],
                        "link": f"http://drewlive24.duckdns.org:4123?url=https://ddy6new.newkso.ru/ddy6/premium{ch2['channel_id']}/mono.m3u8&data=T3JpZ2luPWh0dHBzOi8vZm9yY2VkdG9wbGF5Lnh5enxSZWZlcmVyPWh0dHBzOi8vZm9yY2VkdG9wbGF5Lnh5ei98VXNlci1hZ2VudD1Nb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0OyBydjoxMzkuMCkgR2Vja28vMjAxMDAxMDEgRmlyZWZveC8xMzkuMHxPcmlnaW49aHR0cHM6Ly9mb3JjZWR0b3BsYXkueHl6fFJlZmVyZXI9aHR0cHM6Ly9mb3JjZWR0b3BsYXkueHl6L3xVc2VyLWFnZW50PU1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEzOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEzOS4w",
                        "api": "",
                        "scheme": "0"
                    }
                    for ch2 in event.get("channels2", [])
                ]
            }
            output[day_key]["Soccer"].append(new_event)

# Step 3: Post to your endpoint
post_data = {
    "f_path": "output.json",
    "f_data": output
}

response = requests.post(
    "https://git.bdsajibx.workers.dev/",
    headers={"Content-Type": "application/json"},
    data=json.dumps(post_data)
)

print(f"POST Status: {response.status_code}")
print(response.text)
