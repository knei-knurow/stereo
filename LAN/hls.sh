GST_DEBUG=2 gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12' !  nvv4l2h264enc ! h264parse ! mpegtsmux ! hlssink playlist-root=http://31.11.196.141:2137 location=segment_%05d.ts target-duration=1 max-files=20

#! videoconvert ! clockoverlay 
