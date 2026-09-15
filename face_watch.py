import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
import sys, time, json, datetime
import cv2
import paho.mqtt.publish as publish
from qdrant_client import QdrantClient
from face_embed import get_faces

CAMERA = sys.argv[1] if len(sys.argv) > 1 else "webcam"
if len(sys.argv) > 2:
    SOURCE = sys.argv[2]
elif CAMERA in ("webcam", "0"):
    SOURCE = 0
else:
    SOURCE = f"rtsp://localhost:8554/{CAMERA}"

COLLECTION = "wanted_faces"
DETECT_EVERY = 5
HEARTBEAT_EVERY = 30
THRESHOLD = 0.45
COOLDOWN = 15

qdrant = QdrantClient(host="localhost", port=6333)

cap = cv2.VideoCapture(SOURCE)
last_alert = {}; fid = 0
fail_count = 0
RECONNECT_AFTER = 50  # ~15s of failed reads before trying to reopen the stream
print(f"Face watch running on {CAMERA} ({SOURCE}). Press Q in the window to stop.")
while True:
    ok, frame = cap.read()
    if not ok:
        fail_count += 1
        if fail_count >= RECONNECT_AFTER:
            print("Stream unresponsive, reconnecting...")
            cap.release()
            cap = cv2.VideoCapture(SOURCE)
            fail_count = 0
        time.sleep(0.3); continue
    fail_count = 0
    fid += 1
    if fid % HEARTBEAT_EVERY == 0:
        publish.single("sentinel/heartbeat", json.dumps({"camera": CAMERA, "time": datetime.datetime.now().isoformat()}),
                        hostname="localhost", port=1883)
    if fid % DETECT_EVERY == 0:
        for face in get_faces(frame):
            x1, y1, x2, y2 = [int(v) for v in face.bbox]
            hits = qdrant.query_points(collection_name=COLLECTION, query=face.normed_embedding.tolist(), limit=1).points
            match = hits[0] if hits else None
            hit = match is not None and match.score >= THRESHOLD
            color = (0, 0, 255) if hit else (0, 200, 0)
            label = match.payload.get("name") if hit else "unknown"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label + (" HIT" if hit else ""), (x1, max(0, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            if hit and time.time() - last_alert.get(match.payload["name"], 0) > COOLDOWN:
                last_alert[match.payload["name"]] = time.time()
                alert = {"type": "FACE_WATCHLIST_HIT", "matched_name": match.payload["name"],
                          "reason": match.payload.get("reason"), "source": match.payload.get("source"),
                          "score": round(match.score, 3), "camera": CAMERA,
                          "time": datetime.datetime.now().isoformat()}
                publish.single("sentinel/alerts", json.dumps(alert), hostname="localhost", port=1883)
                print("ALERT:", match.payload["name"], "-", match.payload.get("reason"), "score", round(match.score, 3))
    cv2.imshow("Sentinel Face Watch", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release(); cv2.destroyAllWindows()
