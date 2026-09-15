$env:PATH += ";C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
ffmpeg -y -i demo_assets\anpr_raw.mp4 -ss 3 -vframes 1 -update 1 demo_assets\anpr_check.png
