Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synthesizer.Rate = -1

$segments = @(
  @{ id = "seg1"; text = "Sentinel is our submission for the Gujarat Police Innovation Hackathon: an integrated video management and analytics platform built to track vehicles, generate real time alerts, and scale to eighty thousand cameras." },
  @{ id = "seg2"; text = "Every camera feed runs automatic number plate recognition at the edge, accelerated by Intel OpenVINO. When a plate matches the VAHAN stolen vehicle watchlist, even with a partial or misread plate, Sentinel flags it instantly." },
  @{ id = "seg3"; text = "That alert appears live on our G I S dashboard. The camera pin turns red, the vehicle's details show in the side panel, and the operator sees exactly where and when the hit occurred." },
  @{ id = "seg4"; text = "As the same vehicle is seen across other cameras, Sentinel stitches those sightings into a movement history, drawing its route across the city so investigators can trace where it has been." },
  @{ id = "seg5"; text = "Our key differentiator is natural language video search. Every detected object is embedded with C L I P and stored in a vector database. An operator can simply type what they are looking for, like car, and get matching clips instantly, with no manual scrubbing." },
  @{ id = "seg6"; text = "We also match faces against a wanted persons list using Insight Face, so a person of interest triggers the exact same real time alert and mapping pipeline as a vehicle hit." },
  @{ id = "seg7"; text = "A camera registry tracks every feed's health status, with bulk onboarding via C S V, so scaling from five cameras to eighty thousand becomes a data problem, not an engineering one." },
  @{ id = "seg8"; text = "Sentinel combines edge A I, M Q T T for low bandwidth scale, and a central intelligence layer, all running on efficient hardware. This is our hybrid architecture for safer, smarter policing across Gujarat." }
)

foreach ($seg in $segments) {
  $path = "$PSScriptRoot\$($seg.id).wav"
  $synthesizer.SetOutputToWaveFile($path)
  $synthesizer.Speak($seg.text)
  $synthesizer.SetOutputToNull()
  Write-Host "$($seg.id) -> $path"
}
$synthesizer.Dispose()
Get-ChildItem "$PSScriptRoot\seg*.wav" | Select-Object Name, Length
