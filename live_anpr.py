import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
import sys, time, json, datetime
import cv2, psycopg2
import paho.mqtt.publish as publish
from rapidfuzz import fuzz
from open_image_models import LicensePlateDetector
from fast_plate_ocr import LicensePlateRecognizer

CAMERA = sys.argv[1] if len(sys.argv) > 1 else "cam1"
RTSP_URL = sys.argv[2] if len(sys.argv) > 2 else f"rtsp://localhost:8554/{CAMERA}"
ANPR_EVERY = 10
THRESHOLD = 75
COOLDOWN = 15
HEARTBEAT_EVERY = 30

def normalize(p):
    return "".join(ch for ch in p.upper() if ch.isalnum())

conn = psycopg2.connect(host="localhost", port=5432, dbname="sentinel", user="sentinel", password="sentinel")
cur = conn.cursor(); cur.execute("SELECT plate, reason, source FROM watchlist")
watchlist = cur.fetchall(); cur.close(); conn.close()
print("Loaded", len(watchlist), "watchlist entries")

det = LicensePlateDetector(detection_model="yolo-v9-t-384-license-plate-end2end")
ocr = LicensePlateRecognizer("cct-s-v1-global-model")

def best_match(plate):
    p = normalize(plate); best, score = None, 0
    for row in watchlist:
        s = fuzz.ratio(p, normalize(row[0]))
        if s > score: score, best = s, row
    return best, score

cap = cv2.VideoCapture(RTSP_URL)
last_alert = {}; fid = 0
fail_count = 0
RECONNECT_AFTER = 50  # ~15s of failed reads before trying to reopen the stream
print(f"Live ANPR running on {CAMERA} ({RTSP_URL}). Press Q in the window to stop.")
while True:
    ok, frame = cap.read()
    if not ok:
        fail_count += 1
        if fail_count >= RECONNECT_AFTER:
            print("Stream unresponsive, reconnecting...")
            cap.release()
            cap = cv2.VideoCapture(RTSP_URL)
            fail_count = 0
        time.sleep(0.3); continue
    fail_count = 0
    fid += 1
    if fid % HEARTBEAT_EVERY == 0:
        publish.single("sentinel/heartbeat", json.dumps({"camera": CAMERA, "time": datetime.datetime.now().isoformat()}),
                        hostname="localhost", port=1883)
    if fid % ANPR_EVERY == 0:
        for d in det.predict(frame):
            bb = d.bounding_box
            x1, y1, x2, y2 = int(bb.x1), int(bb.y1), int(bb.x2), int(bb.y2)
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0: continue
            preds = ocr.run(crop)
            plate = preds[0].plate if preds else ""
            if not plate: continue
            row, score = best_match(plate)
            hit = row is not None and score >= THRESHOLD
            color = (0, 0, 255) if hit else (0, 200, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, plate + (" HIT" if hit else ""), (x1, max(0, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            if hit and time.time() - last_alert.get(row[0], 0) > COOLDOWN:
                last_alert[row[0]] = time.time()
                alert = {"type": "WATCHLIST_HIT", "read_plate": plate, "matched_plate": row[0],
                         "reason": row[1], "source": row[2], "score": round(score, 1),
                         "camera": CAMERA, "time": datetime.datetime.now().isoformat()}
                publish.single("sentinel/alerts", json.dumps(alert), hostname="localhost", port=1883)
                print("ALERT:", row[0], "-", row[1], "score", round(score, 1))
    cv2.imshow("Sentinel Live ANPR", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break
cap.release(); cv2.destroyAllWindows()
