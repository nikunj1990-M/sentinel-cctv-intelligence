import sys, cv2
from open_image_models import LicensePlateDetector
from fast_plate_ocr import LicensePlateRecognizer

# First run downloads the models. If a model NAME errors, the message lists valid names.
plate_detector = LicensePlateDetector(detection_model="yolo-v9-t-384-license-plate-end2end")
plate_reader = LicensePlateRecognizer("cct-xs-v1-global-model")

path = sys.argv[1] if len(sys.argv) > 1 else "car.jpg"
img = cv2.imread(path)
if img is None:
    print("Could not read image:", path); sys.exit(1)

dets = plate_detector.predict(img)
print(f"Found {len(dets)} plate(s)")

for d in dets:
    print("  detection:", repr(d))
    bb = d.bounding_box
    x1, y1, x2, y2 = int(bb.x1), int(bb.y1), int(bb.x2), int(bb.y2)
    crop = img[y1:y2, x1:x2]
    text = plate_reader.run(crop)
    print("  -> plate text:", repr(text), "| type:", type(text)._name_)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, str(text), (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

cv2.imwrite("anpr_out.jpg", img)
print("Saved anpr_out.jpg")
