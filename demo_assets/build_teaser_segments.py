import subprocess, os
from build_segments import build_segment, DA

TEASER_SEGMENTS = [
    ("teaser1", "card2_1080.png",     "still", None),
    ("teaser2", "card4_1080.png",     "still", None),
    ("teaser3", "anpr_clean2.mp4",    "video", "cap_anpr.png"),
    ("teaser4", "face_clean.mp4",     "video", "cap_face.png"),
    ("teaser5", "card5_1080.png",     "still", None),
    ("teaser6", "card6_1080.png",     "still", None),
]

if __name__ == "__main__":
    for seg in TEASER_SEGMENTS:
        build_segment(*seg)
    print("ALL TEASER SEGMENTS BUILT")
