"""Enroll a wanted person's face into the mock eGujCop gallery.

Usage:
  python enroll_face.py "Name" "Reason" "Source" [image_path]

If image_path is omitted, captures a frame from the laptop webcam (device 0) -
look at the camera when running it this way.
"""
import sys, os, uuid
import cv2
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from face_embed import get_faces

if len(sys.argv) < 2:
    print('Usage: python enroll_face.py "Name" "Reason" "Source" [image_path]')
    sys.exit(1)

name = sys.argv[1]
reason = sys.argv[2] if len(sys.argv) > 2 else "Wanted person"
source = sys.argv[3] if len(sys.argv) > 3 else "eGujCop"
image_path = sys.argv[4] if len(sys.argv) > 4 else None

if image_path:
    frame = cv2.imread(image_path)
    if frame is None:
        print("Could not read image:", image_path)
        sys.exit(1)
else:
    print("Opening webcam, look at the camera...")
    cap = cv2.VideoCapture(0)
    frame = None
    for _ in range(30):
        ok, f = cap.read()
        if ok:
            frame = f
        cv2.waitKey(30)
    cap.release()
    if frame is None:
        print("Could not read from webcam. Pass an image path instead.")
        sys.exit(1)

faces = get_faces(frame)
if not faces:
    print("No face detected. Try again with better lighting, or pass an image path.")
    sys.exit(1)

face = max(faces, key=lambda f: f.det_score)
x1, y1, x2, y2 = [int(v) for v in face.bbox]
crop = frame[max(0, y1):y2, max(0, x1):x2]

THUMBS_DIR = "static/faces"
os.makedirs(THUMBS_DIR, exist_ok=True)
point_id = str(uuid.uuid4())
thumb_path = os.path.join(THUMBS_DIR, f"{point_id}.jpg")
cv2.imwrite(thumb_path, crop if crop.size else frame)

qdrant = QdrantClient(host="localhost", port=6333)
qdrant.upsert(collection_name="wanted_faces", points=[PointStruct(
    id=point_id,
    vector=face.normed_embedding.tolist(),
    payload={"name": name, "reason": reason, "source": source, "thumb": f"/faces/{point_id}.jpg"},
)])
print(f"Enrolled '{name}' (det_score={face.det_score:.2f}) -> {thumb_path}")
