import cv2

from neuromodules.ann_app_base import AnnAppBase
from neuromodules.marking_recognition.recognition.recognizer import Recognizer


class AnnApp(AnnAppBase):
    recognizer = Recognizer()

    def process(self, path):
        video_capture = cv2.VideoCapture(path)
        _, frame = video_capture.read()
        markings = []
        while frame is not None and not (cv2.waitKey(1) & 0xFF == ord('q')):
            marking_model = self.recognizer.recognize_on_frame(frame)
            if marking_model.cap_detected:
                markings.append("".join(marking_model.marking))
            _, frame = video_capture.read()
        return markings


if __name__ == '__main__':
    app = AnnApp()
    fetched_markings = app.process('./test_video/result.avi')
    print(fetched_markings)
