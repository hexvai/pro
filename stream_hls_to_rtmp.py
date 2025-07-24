import subprocess

HLS_URL = "http://kst.moonplex.net:8080/CH2/tracks-v1a1/mono.m3u8"  # replace with your real .m3u8
RTMP_URL = "rtmp://live.restream.io/live/re_7638211_event4c220a8725e842108313d235ea41e326"  # replace with your actual RTMP

def stream_to_rtmp():
    command = [
        "ffmpeg",
        "-re",                     # Read input in real-time
        "-i", HLS_URL,            # HLS input URL
        "-c:v", "copy",           # Copy video codec
        "-c:a", "aac",            # Encode audio to AAC (required by many RTMP servers)
        "-f", "flv",              # Output format for RTMP
        RTMP_URL
    ]

    print("▶️ Starting FFmpeg stream...")
    result = subprocess.run(command, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

if __name__ == "__main__":
    stream_to_rtmp()
