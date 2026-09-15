import fast_plate_ocr, open_image_models
print("FPO:", [x for x in dir(fast_plate_ocr) if not x.startswith("_")])
print("OIM:", [x for x in dir(open_image_models) if not x.startswith("_")])
