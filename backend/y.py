import subprocess
import numpy as np
import cv2

WIDTH = 640
HEIGHT = 480

cmd = [
    "ffmpeg",
    "-f", "v4l2",
    "-video_size", f"{WIDTH}x{HEIGHT}",
    "-i", "/dev/video1",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-"
]

pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)

raw_image = pipe.stdout.read(WIDTH * HEIGHT * 3)

frame = np.frombuffer(raw_image, dtype=np.uint8)
frame = frame.reshape((HEIGHT, WIDTH, 3))

cv2.imwrite("pipe_test.jpg", frame)

pipe.terminate()

print("Saved pipe_test.jpg")