from ultralytics import YOLO

# Use the OpenVINO model we exported, running on the Iris Xe iGPU
model = YOLO("yolov8n_openvino_model/")

# source=0 = your laptop webcam; show=True opens a live window with boxes
results = model.predict(source=0, device="intel:gpu", show=True, stream=True, verbose=False)

for r in results:
    pass  # the live window updates automatically; press Q in the window (or Ctrl+C here) to stop
