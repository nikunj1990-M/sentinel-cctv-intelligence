import urllib.request, os
os.makedirs("static/leaflet", exist_ok=True)
sources = [
    "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/",
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/",
]
ok = False
for base in sources:
    try:
        for f in ["leaflet.js", "leaflet.css"]:
            urllib.request.urlretrieve(base + f, "static/leaflet/" + f)
        print("Downloaded Leaflet from", base); ok = True; break
    except Exception as e:
        print("Failed:", base, "->", e)
print("SUCCESS" if ok else "ALL SOURCES BLOCKED - tell me")
