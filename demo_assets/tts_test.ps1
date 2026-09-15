New-Item -ItemType Directory -Force -Path "$PSScriptRoot" | Out-Null
Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synthesizer.Rate = -1
$synthesizer.SetOutputToWaveFile("$PSScriptRoot\test_voice.wav")
$synthesizer.Speak("Sentinel. Gujarat Police integrated video management and analytics platform.")
$synthesizer.Dispose()
Get-Item "$PSScriptRoot\test_voice.wav" | Select-Object Name, Length
