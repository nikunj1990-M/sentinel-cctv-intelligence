import openvino as ov

core = ov.Core()
print("OpenVINO devices:", core.available_devices)
for d in core.available_devices:
    print(f"  {d}: {core.get_property(d, 'FULL_DEVICE_NAME')}")
