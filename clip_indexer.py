import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
import sys, time, uuid, datetime, json
import cv2
from PIL import Image
from ultralytics import YOLO
import paho.mqtt.publish as publish
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from clip_embed import embed_image, EMBED_DIM

CAMERA = sys.argv[1] if len(sys.argv) > 1 else "cam1"
RTSP_URL = sys.argv[2] if len(sys.argv) > 2 else f"rtsp://localhost:8554/{CAMERA}"
COLLECTION = "detections"
DETECT_EVERY = 10
HEARTBEAT_EVERY = 30
CONF_THRESH = 0.4
CLASSES_OF_INTEREST = {0: "person", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
THUMBS_DIR = "static/thumbs"

os.makedirs(THUMBS_DIR, exist_ok=True)

qdrant = QdrantClient(host="localhost", port=6333)
if not qdrant.collection_exists(COLLECTION):
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

model = YOLO("yolov8n_openvino_model/")

cap = cv2.VideoCapture(RTSP_URL)
fid = 0
fail_count = 0
RECONNECT_AFTER = 50  # ~15s of failed reads before trying to reopen the stream
print(f"CLIP indexer running on {RTSP_URL}. Press Q in the window to stop.")
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
    if fid % DETECT_EVERY == 0:
        result = model.predict(frame, device="intel:gpu", verbose=False)[0]
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in CLASSES_OF_INTEREST:
                continue
            conf = float(box.conf[0])
            if conf < CONF_THRESH:
                continue
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
            crop = frame[max(0, y1):y2, max(0, x1):x2]
            if crop.size == 0:
                continue
            label = CLASSES_OF_INTEREST[cls_id]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 180, 0), 2)
            cv2.putText(frame, label, (x1, max(0, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 180, 0), 2)

            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            vector = embed_image(pil_img)
            point_id = str(uuid.uuid4())
            thumb_name = f"{point_id}.jpg"
            cv2.imwrite(os.path.join(THUMBS_DIR, thumb_name), crop)
            qdrant.upsert(collection_name=COLLECTION, points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "camera": CAMERA,
                    "class": label,
                    "score": round(conf, 3),
                    "time": datetime.datetime.now().isoformat(),
                    "thumb": f"/thumbs/{thumb_name}",
                },
            )])
            print(f"indexed {label} ({conf:.2f}) from {CAMERA} -> {thumb_name}")
    cv2.imshow("Sentinel CLIP Indexer", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release(); cv2.destroyAllWindows()
