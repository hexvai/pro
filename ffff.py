import subprocess

HLS_URL = "https://futbollive.online/T-Sports/index.m3u8?token=dfa2a85f5675477f79842dd6b0debca7d027eea7-689b0299fd6576a10675f61de6e181e2-1756557594-1756553994"

RTMP_URLS = [
    "rtmp://live.restream.io/live/re_9963825_eventb6539cc6563d42c1a983c4c9118051ae",
    "rtmp://live.restream.io/live/re_7638211_event4c220a8725e842108313d235ea41e326"
]

def stream_to_multiple_rtmp():
    processes = []
    for url in RTMP_URLS:
        command = [
            "ffmpeg",
            "-re",
            "-i", HLS_URL,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", "2000k",
            "-c:a", "aac",
            "-b:a", "128k",
            "-f", "flv",
            url
        ]
        print(f"▶️ Starting FFmpeg to {url} ...")
        processes.append(subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))

    for p in processes:
        stdout, stderr = p.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

if __name__ == "__main__":
    stream_to_multiple_rtmp()
