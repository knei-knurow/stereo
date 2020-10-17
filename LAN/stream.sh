gst-launch-1.0  nvarguscamerasrc sensor-id=0 sensor-mode=3 ! 'video/x-raw(memory:NVMM), width=1280, height=720, format=(string)I420, framerate=30/1' !  omxh264enc bitrate=1000000 insert-aud=false ! video/x-h264, profile=baseline ! hlssink playlist-root=http://192.168.1.9:8080 location=segment_%05d.ts target-duration=5 max-files=5

