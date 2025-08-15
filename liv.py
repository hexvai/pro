import requests
import json
import base64

# === Config: Update these before running ===
GITHUB_TOKEN = "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"
REPO_OWNER = "Daniel-Andress1"
REPO_NAME = "max-x"
FILE_PATH = "liv.json"  # path in repo where you want to save M3U
BRANCH = "main"  # target branch name

# SonyLIV API URL
url = "https://apiv2.sonyliv.com/AGL/4.7/A/ENG/WEB/BD/UNKNOWN/TRAY/EXTCOLLECTION/30188540"

def get_file_sha():
    """Get the SHA of the existing file (needed for update)"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"ref": BRANCH}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["sha"]
    elif response.status_code == 404:
        return None  # file does not exist yet
    else:
        raise Exception(f"Error fetching file info: {response.status_code} {response.text}")

def push_file(content, sha=None):
    """Create or update the file in GitHub repo"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    message = "Update liv.m3u via script"
    encoded_content = base64.b64encode(content.encode("utf-8")).decode()

    data = {
        "message": message,
        "content": encoded_content,
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha

    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print(f"✅ File '{FILE_PATH}' pushed successfully!")
    else:
        print(f"❌ Failed to push file: {response.status_code} {response.text}")

def main():
    try:
        # Fetch JSON data from SonyLIV
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Build M3U lines
        m3u_lines = ["#EXTM3U"]
        
        # Extract containers directly from the response
        containers = data["resultObj"]["containers"]

        for container in containers:
            metadata = container.get("metadata", {})
            emf = metadata.get("emfAttributes", {})

            title = metadata.get("title")
            dai_asset_key = emf.get("dai_asset_key")
            image = emf.get("tv_background_image")

            if not dai_asset_key:
                continue

            stream_link = f"https://dai.google.com/ssai/event/{dai_asset_key}/master.m3u8"

            # Add channel info (if available)
            broadcast_channel = emf.get("broadcast_channel", "")
            if broadcast_channel:
                title = f"{title} - {broadcast_channel}"

            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{image}", {title}')
            m3u_lines.append(stream_link)

        m3u_str = "\n".join(m3u_lines)

        # Optional: print M3U content locally
        print(m3u_str)

        # Get existing file SHA if present (for update)
        sha = get_file_sha()

        # Push the M3U content to GitHub repo
        push_file(m3u_str, sha)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
