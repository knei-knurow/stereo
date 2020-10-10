import cv2 as cv

def to_csi_device(id):
    return (
            "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                id, # camera id
                3, # mode
                1280, # width
                720, # height
                60, # frame rate
                0, # flip method
                1280, # display width
                720, # display height
            )
        )


camL = cv.VideoCapture(to_csi_device(0))
camR = cv.VideoCapture(to_csi_device(1))

fourccL = cv.VideoWriter_fourcc(*'HEVC')
fourccR = cv.VideoWriter_fourcc(*'HEVC')

writerL = cv.VideoWriter("left.mp4", fourccL, 60, (1280, 720))
writerR = cv.VideoWriter("right.mp4", fourccR, 60, (1280, 720))

if not camL.isOpened() or not camR.isOpened():
    raise Exception("Camera not found.")

length = 60 * 5
frames_cnt = 0
while True:
    retR, frameR = camR.read()
    retL, frameL = camL.read()
    
    if not retR or not retL:
        camL.release()
        camR.release()
    
        writerR.release()
        writerL.release()
        
        cv.destroyAllWindows()
        raise Exception("Can't recieve frame.")

    frames_cnt += 1

    writerR.write(frameR)
    writerL.write(frameL)

    if cv.waitKey(1000 / 60) == ord("q"):
        break

    if frames_cnt > length:
        break

print("Closing.")
camL.release()
camR.release()
writerL.release()
writerR.release()
cv.destroyAllWindows()