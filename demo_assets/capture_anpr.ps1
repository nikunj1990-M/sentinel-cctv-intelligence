Add-Type -AssemblyName Microsoft.VisualBasic
$activated = [Microsoft.VisualBasic.Interaction]::AppActivate("Sentinel Live ANPR")
Start-Sleep -Milliseconds 500
Write-Output "activated: $activated"
$env:PATH += ";C:\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
ffmpeg -y -f gdigrab -framerate 30 -i title="Sentinel Live ANPR" -t 22 demo_assets\anpr_raw2.mp4
