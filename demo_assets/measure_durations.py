import subprocess, glob, os

ffprobe = r"C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin\ffprobe.exe"
folder = os.path.dirname(os.path.abspath(__file__))

def dur(path):
    out = subprocess.check_output([ffprobe, "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.strip())

main_total = 0
print("--- main ---")
for i in range(1, 13):
    d = dur(os.path.join(folder, f"main{i}.wav"))
    main_total += d
    print(f"main{i}: {d:.2f}s")
print(f"MAIN TOTAL: {main_total:.2f}s ({main_total/60:.2f} min)")

teaser_total = 0
print("--- teaser ---")
for i in range(1, 7):
    d = dur(os.path.join(folder, f"teaser{i}.wav"))
    teaser_total += d
    print(f"teaser{i}: {d:.2f}s")
print(f"TEASER TOTAL: {teaser_total:.2f}s")
