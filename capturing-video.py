camera = cv.VideoCapture(0)
fourcc = cv.VideoWriter_fourcc(*'DIVX')
writer = cv.VideoWriter("savedddd.avi", fourcc, 30, (480, 640))

if not camera.isOpened():
    raise Exception("Camera not found.")

while True:
    ret, frame = camera.read()

    if not ret:
        camera.release()
        writer.release()
        cv.destroyAllWindows()
        raise Exception("Can't recieve frame.")

    frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)

    writer.write(frame)

    cv.imshow("Window", frame)
    if cv.waitKey(1) == ord("q"):
        break
    
camera.release()
writer.release()
cv.destroyAllWindows()