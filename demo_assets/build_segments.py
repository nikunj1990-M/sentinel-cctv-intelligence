import subprocess, json, os

FFMPEG = r"C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"
DA = os.path.dirname(__file__)

def dur(path):
    out = subprocess.run([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                           "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out)

SEGMENTS = [
    ("main1",  "card1_1080.png",       "still", None),
    ("main2",  "card2_1080.png",       "still", None),
    ("main3",  "card3_1080.png",       "still", None),
    ("main4",  "card4_1080.png",       "still", None),
    ("main5",  "anpr_clean2.mp4",      "video", "cap_anpr.png"),
    ("main6",  "gis_route_1080.png",   "still", "cap_route.png"),
    ("main7",  "face_clean.mp4",       "video", "cap_face.png"),
    ("main8",  "nl_search_1080.png",   "still", "cap_search.png"),
    ("main9",  "predict_drone_1080.png","still","cap_predict.png"),
    ("main10", "registry_1080.png",    "still", "cap_registry.png"),
    ("main11", "card5_1080.png",       "still", None),
    ("main12", "card6_1080.png",       "still", None),
]

def build_segment(seg_id, asset, kind, caption):
    audio = os.path.join(DA, f"{seg_id}.wav")
    d = dur(audio)
    out = os.path.join(DA, f"seg_{seg_id}.mp4")
    asset_path = os.path.join(DA, asset)
    frames = int(d * 30) + 2

    if kind == "still":
        vf = (f"scale=1920:1080,setsar=1,"
              f"zoompan=z='min(zoom+0.0006,1.12)':d={frames}:s=1920x1080:fps=30")
        if caption:
            cap_path = os.path.join(DA, caption)
            cmd = [FFMPEG, "-y", "-loop", "1", "-i", asset_path,
                   "-loop", "1", "-i", cap_path, "-i", audio,
                   "-filter_complex",
                   f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0:shortest=1[v]",
                   "-map", "[v]", "-map", "2:a",
                   "-t", str(d), "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "160k", out]
        else:
            cmd = [FFMPEG, "-y", "-loop", "1", "-i", asset_path, "-i", audio,
                   "-vf", vf, "-t", str(d), "-r", "30",
                   "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "160k", out]
    else:  # video
        if caption:
            cap_path = os.path.join(DA, caption)
            cmd = [FFMPEG, "-y", "-i", asset_path, "-loop", "1", "-i", cap_path, "-i", audio,
                   "-filter_complex",
                   "[0:v]scale=1920:1080,setsar=1[bg];[bg][1:v]overlay=0:0:shortest=1[v]",
                   "-map", "[v]", "-map", "2:a",
                   "-t", str(d), "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "160k", out]
        else:
            cmd = [FFMPEG, "-y", "-i", asset_path, "-i", audio,
                   "-vf", "scale=1920:1080,setsar=1",
                   "-t", str(d), "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-map", "0:v", "-map", "1:a",
                   "-c:a", "aac", "-b:a", "160k", out]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED", seg_id)
        print(r.stderr[-3000:])
        raise SystemExit(1)
    print(f"{seg_id}: built ({d:.2f}s)")

if __name__ == "__main__":
    for seg in SEGMENTS:
        build_segment(*seg)
    print("ALL SEGMENTS BUILT")
