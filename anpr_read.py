import cv2
from open_image_models import LicensePlateDetector
from fast_plate_ocr import LicensePlateRecognizer

det = LicensePlateDetector(detection_model="yolo-v9-t-384-license-plate-end2end")
ocr = LicensePlateRecognizer("cct-xs-v1-global-model")

img = cv2.imread("car.jpg")
for d in det.predict(img):
    bb = d.bounding_box
    crop = img[int(bb.y1):int(bb.y2), int(bb.x1):int(bb.x2)]
    text = ocr.run(crop)
    print("PLATE RESULT:", repr(text))
