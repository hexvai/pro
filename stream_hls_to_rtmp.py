import subprocess

HLS_URL = "https://tvsen6.aynaott.com/tsportsfhd/tracks-v1a1/mono.ts.m3u8"  # replace with your real .m3u8
RTMP_URL = "rtmp://live.restream.io/live/re_9963825_eventb6539cc6563d42c1a983c4c9118051ae"  # replace with your actual RTMP

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
