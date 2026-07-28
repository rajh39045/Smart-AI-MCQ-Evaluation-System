import cv2


class Webcam:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    # -------------------------
    # Start Webcam
    # -------------------------
    def start(self):

        if self.cap is not None:
            return True

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            self.cap = None
            raise Exception("Unable to open webcam.")

        # Optional camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        return True

    # -------------------------
    # Read Frame
    # -------------------------
    def read(self):

        if self.cap is None:
            return None

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    # -------------------------
    # Capture Image
    # -------------------------
    def capture(self, filename="student.jpg"):

        frame = self.read()

        if frame is None:
            raise Exception("No frame available.")

        success = cv2.imwrite(filename, frame)

        if not success:
            raise Exception("Failed to save image.")

        return filename

    # -------------------------
    # Is Camera Running?
    # -------------------------
    def is_running(self):

        return self.cap is not None

    # -------------------------
    # Stop Webcam
    # -------------------------
    def stop(self):

        if self.cap is not None:
            self.cap.release()
            self.cap = None