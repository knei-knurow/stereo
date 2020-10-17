gst-launch-1.0 v4l2src device=/dev/video0 ~ 'video/x-raw, width=1280, height=720' ! nvvidconv ! 'video/x-raw(mempry:NVMM)' ! nvoverlaysink
