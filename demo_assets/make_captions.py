from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__))

captions = {
    "cap_anpr": "LIVE ANPR DETECTION & WATCHLIST MATCH",
    "cap_route": "CROSS-CAMERA ROUTE TRACKING",
    "cap_face": "FACE WATCHLIST RECOGNITION",
    "cap_search": "NATURAL LANGUAGE VIDEO SEARCH",
    "cap_predict": "PREDICTIVE INTERCEPT + DRONE DISPATCH",
    "cap_registry": "CAMERA REGISTRY & SECURITY (RBAC + AUDIT)",
}

W, H = 1920, 1080
BAR_H = 110

try:
    font = ImageFont.truetype("segoeuib.ttf", 42)
except Exception:
    font = ImageFont.truetype("arial.ttf", 42)

for name, text in captions.items():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bar_top = H - BAR_H - 60
    # semi-transparent dark bar
    d.rectangle([0, bar_top, W, bar_top + BAR_H], fill=(15, 20, 32, 210))
    # accent line
    d.rectangle([0, bar_top, 8, bar_top + BAR_H], fill=(43, 140, 255, 255))
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = 50
    ty = bar_top + (BAR_H - th) // 2 - bbox[1]
    d.text((tx, ty), text, font=font, fill=(232, 238, 245, 255))
    im.save(os.path.join(OUT, f"{name}.png"))
    print("wrote", name)
