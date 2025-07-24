import subprocess

HLS_URL = "https://live.incableinternet.com/v/QCZ86p6-0oo.m3u8"  # replace with your real .m3u8
RTMP_URL = "rtmp://live.restream.io/live/re_7638211_event4c220a8725e842108313d235ea41e326"  # replace with your actual RTMP

def stream_to_rtmp():
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
    RTMP_URL
]

    print("▶️ Starting FFmpeg stream...")
    result = subprocess.run(command, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

if __name__ == "__main__":
    stream_to_rtmp()
