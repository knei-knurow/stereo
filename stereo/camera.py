import cv2 as cv

def list_cams():
    cams = []
    for i in range(32):
        cam = cv.VideoCapture(i)
        ret, _ = cam.read()
        if not ret:
            continue
        cams.append(i)
    return cams

def get_source():
    pass