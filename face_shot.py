import cv2
import os

name = 'elon' #replace with your name

cam = cv2.VideoCapture(0)

cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
cv2.resizeWindow("press space to take a photo", 500, 300)

img_counter = 0

while True:
    # This line is using the `read()` method of a `cam` object, which is likely an instance of a VideoCapture object from the OpenCV library. The `read()` method is used to grab, decode and return the next video frame from the video file or camera.
    # The `read()` method returns two values:
    # 1. `ret` (short for return value): This is a boolean value. It will be True if the frame was read correctly and False if not (for example, if the video file is over or the camera is not open).
    # 2. `frame`: This is an image array vector captured by the webcam (frame). It represents the next video frame. If the frame is read correctly, it will be a numpy array.
    # The line of code is using Python's multiple assignment feature to assign these two return values to the variables `ret` and `frame` respectively. This is a common pattern when working with OpenCV to capture video frames.
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("press space to take a photo", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = os.path.join("dataset", name, "image_{}.jpg".format(img_counter))
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()