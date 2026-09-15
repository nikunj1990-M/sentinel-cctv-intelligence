from ultralytics import YOLO

model = YOLO("yolov8n_openvino_model/")
results = model.predict(
    source="rtsp://localhost:8554/cam1",
    device="intel:gpu",
    show=True, stream=True, verbose=False,
)
for r in results:
    pass  # live window; press Q in the window to stop
