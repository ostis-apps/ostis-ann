import cv2

from neuromodules.recognition_module.marking_recognition.recognition.recognizer import Recognizer
from neuromodules.ann_app_base import AnnAppBase
# from sctp.marking_sender import MarkingSender


class AnnApp(AnnAppBase):
    recognizer = Recognizer()
    # sender = MarkingSender("control_point_1")

    def process(self, path):
        video_capture = cv2.VideoCapture(path)
        _, frame = video_capture.read()
        markings = []
        while frame is not None and not (cv2.waitKey(1) & 0xFF == ord('q')):
            marking_model = self.recognizer.recognize_on_frame(frame)
            if marking_model.cap_detected:
                markings.append("".join(marking_model.marking))
                # self.sender.send_marking(marking_model)
            _, frame = video_capture.read()
        return markings


if __name__ == '__main__':
    app = AnnApp()
    # fetched_markings = app.process('./neuromodules/recognition_module/marking_recognition/test_video/result.avi')
    fetched_markings = app.process('./test_video/result.avi')
    print(fetched_markings)
