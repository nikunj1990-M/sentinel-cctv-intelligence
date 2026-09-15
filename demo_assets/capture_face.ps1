$env:PATH += ";C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
ffmpeg -y -f gdigrab -framerate 30 -i title="Sentinel Face Watch" -t 18 demo_assets\face_raw.mp4
