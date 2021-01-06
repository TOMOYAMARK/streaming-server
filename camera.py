import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self):
        super().__init__()

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(1)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            #resize
            img = cv2.resize(img, dsize=(640, 360))

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
