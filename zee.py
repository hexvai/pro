import requests
import json
import re

# Fetch the M3U file
m3u_url = "https://raw.githubusercontent.com/alex4528/m3u/refs/heads/main/z5.m3u"
response = requests.get(m3u_url)

if response.status_code == 200:
    original_content = response.text

    # Replace %2f* with %2f%2A
    modified_content = original_content.replace("%2f*", "%2f%2A")

    lines = modified_content.splitlines()
    result = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('#EXTINF:'):
            # Extract channel name
            name_match = re.search(r',(.+)', line)
            name = name_match.group(1).strip() if name_match else ''

            # Extract logo URL
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1).strip() if logo_match else ''

            # Look ahead for user-agent and link
            user_agent = ''
            cookie = ''
            link = ''

            if i + 1 < len(lines) and lines[i+1].startswith('#EXTVLCOPT:http-user-agent='):
                user_agent = lines[i+1].replace('#EXTVLCOPT:http-user-agent=', '').strip()
                i += 1  # Skip user-agent line

            # Next line is the link
            if i + 1 < len(lines):
                link = lines[i+1].strip()
                i += 1

            result.append({
                "logo": logo,
                "name": name,
                "link": link,
                "userAgent": user_agent,
                "cookie": cookie  # Add cookie if you find one
            })

        i += 1

    # Prepare POST data with f_data as a Python list (not JSON string)
    post_data = {
        "f_path": "zee.json",
        "f_data": result
    }

    # POST the data as JSON
    post_response = requests.post(
        "https://git.bdsajibx.workers.dev/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(post_data)
    )

    if post_response.status_code == 200:
        print("POST successful!")
        print(post_response.text)
    else:
        print("POST failed with status:", post_response.status_code)
        print(post_response.text)

else:
    print("Failed to fetch M3U file. Status:", response.status_code)
