Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice("Microsoft Hazel Desktop")
$synth.Rate = 1

$main = @(
  @{ id="main1"; text="Sentinel. Unified C C T V intelligence for Gujarat Police. A project by Nikunj Rameshbhai Maheshwari, for the Gujarat Police Innovation Hackathon twenty twenty six." },
  @{ id="main2"; text="Today, Gujarat has more than eighty thousand cameras, across five departments. But all of them work separately, like islands. There is no single system, no automatic alert. If a stolen car or a wanted person passes, we come to know only later, after checking footage manually." },
  @{ id="main3"; text="Gujarat already has A N P R at the borders. But that only reads number plates, at fixed points. Sentinel is much bigger. It works on any existing camera, and detects not only vehicles, but also faces, and full scenes, across the entire network." },
  @{ id="main4"; text="Here is the design. Existing cameras connect to our platform. The A I runs at the edge itself. Only small alerts and data come to the centre, never the full video. This is how we save bandwidth and reach eighty thousand cameras. At the centre we match with government databases like VAHAN and e Guj Cop, and show everything on one live map." },
  @{ id="main5"; text="Let me show you live. A vehicle passes the camera. Sentinel detects the number plate, reads it, and immediately checks the stolen vehicle database. See, the plate matches. Instantly a red alert is raised, even if the plate is slightly unclear, because we use smart fuzzy matching." },
  @{ id="main6"; text="The alert comes on the live map, in real time. And look here, Sentinel joins the same vehicle across many cameras and draws its complete route. Now we know exactly where the vehicle went, and at what time." },
  @{ id="main7"; text="It is not only for vehicles. Watch, Sentinel recognises a face and matches it against the wanted and missing persons list from e Guj Cop. The same instant alert is raised, with the match confidence." },
  @{ id="main8"; text="And this is our special feature. You can search the video in simple language. Just type, red S U V near Sector eighteen, and Sentinel brings all matching clips from across the city. No manual searching, no waiting." },
  @{ id="main9"; text="Sentinel also predicts the next camera the vehicle will reach, so police can intercept in advance. And on any alert, we can dispatch a drone that follows the vehicle's route to the interception point, integration ready for real drones." },
  @{ id="main10"; text="Every camera is on our registry with live health status. The full system is secure, with role based login for officers and a complete audit trail of every action, following the D P D P Act." },
  @{ id="main11"; text="Best of all, no new cameras, no per camera licensing. We use the cameras Gujarat already has, on ordinary hardware. This saves crores of rupees every year, and scales to the full state." },
  @{ id="main12"; text="Sentinel. Protect what matters. Built on the cameras Gujarat already owns. Thank you. Project by Nikunj Rameshbhai Maheshwari." }
)

$teaser = @(
  @{ id="teaser1"; text="Eighty thousand cameras across Gujarat, all working separately. Until now." },
  @{ id="teaser2"; text="Sentinel turns every existing camera into one real-time intelligence network, reading vehicles, faces, and full scenes. No new hardware." },
  @{ id="teaser3"; text="A stolen car passes a camera. Instantly, the plate is read, matched, and a red alert appears on the live map, with the vehicle's full route across the city." },
  @{ id="teaser4"; text="It recognises wanted persons by face. And you can search the video in plain language, just type, red S U V near Sector eighteen, and it finds them across the city." },
  @{ id="teaser5"; text="All on the cameras Gujarat already owns, on ordinary hardware, scaling to eighty thousand cameras and saving crores in licensing every year." },
  @{ id="teaser6"; text="Sentinel. Protect what matters. A project by Nikunj Rameshbhai Maheshwari." }
)

foreach ($seg in ($main + $teaser)) {
  $path = "$PSScriptRoot\$($seg.id).wav"
  $synth.SetOutputToWaveFile($path)
  $synth.Speak($seg.text)
  $synth.SetOutputToNull()
  Write-Host "$($seg.id) -> $path"
}
$synth.Dispose()
