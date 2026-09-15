from ultralytics import YOLO
import time

# Export the nano model to OpenVINO format (creates yolov8n_openvino_model/)
YOLO("yolov8n.pt").export(format="openvino")
ov_model = YOLO("yolov8n_openvino_model/")

for dev in ["intel:cpu", "intel:gpu"]:
    ov_model.predict("bus.jpg", device=dev, verbose=False)  # warm-up
    t = time.time()
    for _ in range(20):
        ov_model.predict("bus.jpg", device=dev, verbose=False)
    print(f"{dev}: {20/(time.time()-t):.1f} FPS")
