from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.predict("https://ultralytics.com/images/bus.jpg", save=True)
print("Detections:", len(results[0].boxes))
print("Saved annotated image under runs/detect/predict/")
