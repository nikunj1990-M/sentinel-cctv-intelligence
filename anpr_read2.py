import cv2
from open_image_models import LicensePlateDetector
from fast_plate_ocr import LicensePlateRecognizer

det = LicensePlateDetector(detection_model="yolo-v9-t-384-license-plate-end2end")
ocr = LicensePlateRecognizer("cct-s-v1-global-model")   # larger than cct-xs

img = cv2.imread("car.jpg")
for d in det.predict(img):
    bb = d.bounding_box
    crop = img[int(bb.y1):int(bb.y2), int(bb.x1):int(bb.x2)]
    crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    preds = ocr.run(crop)
    print("PLATE:", preds[0].plate if preds else None)
