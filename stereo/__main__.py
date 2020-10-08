import stereo as st
import cv2 as cv

while True:
    c = st.Cameras([0, 1], transformations=[], api=cv.CAP_MSMF)
    c.capture()
    cv.imshow("0", c.frames[0])
    if cv.waitKey(0) == ord("q"):
        break
cv.destroyAllWindows()


