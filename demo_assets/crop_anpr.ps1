$env:PATH += ";C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
ffmpeg -y -i demo_assets\anpr_raw2.mp4 -vf "crop=1104:880:4:4,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=30" -c:v libx264 -pix_fmt yuv420p -crf 18 demo_assets\anpr_clean.mp4
