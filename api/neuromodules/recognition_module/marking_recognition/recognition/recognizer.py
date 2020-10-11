import PIL.Image
import cv2
import os
import numpy as np
import math

import torch
from torchvision import transforms

from neuromodules.recognition_module.marking_recognition.utils.mobilenetv1_ssd import create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor
from neuromodules.recognition_module.marking_recognition.recognition.marking_model import MarkingModel
from neuromodules.recognition_module.marking_recognition.recognition.position_classifier import FastClassifier

class Recognizer:
    classnames = ['BACKGROUND', 'cap', 'label']
    numbers = ['BACKGROUND', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    magic_numbers = [2.4, 1.9, 3.1]

    def __init__(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        self.device = torch.device("cpu")
        self.model = FastClassifier()
        self.model.load_state_dict(
            torch.load('./neuromodules/recognition_module/marking_recognition/models/position_classifier_2_t.pth',
                       map_location='cpu'))
        # self.model = torch.load('./models/position_classifier_2.pth', map_location='cpu')
        self.model.eval()

        caps_detector = create_mobilenetv1_ssd(len(self.classnames), is_test=True)
        caps_detector.load('./neuromodules/recognition_module/marking_recognition/models/caps_detector.pth')
        # caps_detector.load('./models/caps_detector.pth')
        self.caps_predictor = create_mobilenetv1_ssd_predictor(caps_detector, candidate_size=200)

        num_detector = create_mobilenetv1_ssd(len(self.numbers), is_test=True)
        num_detector.load('./neuromodules/recognition_module/marking_recognition/models/numbers_detector_5.pth')
        # num_detector.load('./models/numbers_detector_5.pth')
        self.num_predictor = create_mobilenetv1_ssd_predictor(num_detector, candidate_size=200)

        self.test_transforms = transforms.Compose([
            transforms.Resize((300, 300)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
        ])
        self.counter = 0
        self.prev_class = 1

    def predict_image(self, image):
        image_tensor = self.test_transforms(image).float()
        image_tensor = image_tensor.unsqueeze(0)
        input = image_tensor.to(self.device)
        output = self.model(input)
        index = output.data.cpu().numpy().argmax()
        # print(output)
        return index

    def construct_date(self, boxes_sorted, _begin, code_array, avg_width):
        box0 = boxes_sorted[_begin]
        result_subcode = str(code_array[_begin])
        i = _begin+1
        j = 1
        while j < 6:
            if j % 2 == 0:
                offset = self.magic_numbers[0]*avg_width
            else:
                offset = avg_width
            predict_next_box_x0 = box0[0] + offset
            box_next = boxes_sorted[i]
            if math.fabs(predict_next_box_x0 - box_next[0]) < avg_width:
                result_subcode += str(code_array[i])
                if not j % 2 == 0 and j != 5:
                    result_subcode += '.'
                box0 = box_next
                i += 1
            else:
                result_subcode += "*"
                if not j % 2 == 0 and j != 5:
                    result_subcode += '.'
                box0[0] += offset
            j += 1
        return result_subcode, i, box0[0]

    def construct_number(self, boxes_sorted, _begin, code_array, avg_width, initial_offset, length):
        result_subcode = ""
        i = _begin
        j = 0
        predict_next_box_x0 = initial_offset
        while j < length:
            if i >= len(boxes_sorted):
                result_subcode += "*"*(length-j)
                break
            else:
                box0 = boxes_sorted[i]
                if math.fabs(predict_next_box_x0 - box0[0]) < avg_width:
                    result_subcode += str(code_array[i])
                    predict_next_box_x0 = box0[0] + avg_width
                    i += 1
                else:
                    result_subcode += "*"
                    predict_next_box_x0 += avg_width
                j += 1
        return result_subcode, i

    def get_code(self, boxes, markingList):
        boxes_np = np.array(boxes)
        code = np.array(markingList).reshape((len(markingList), -1)).astype(
            'float32')
        boxes_np = np.hstack((boxes_np, code))
        tmp = boxes_np.ravel().view(
            'float32, float32, float32, float32, float32')
        tmp.sort(order=['f1'])
        next_line_index = np.argmax(boxes_np[1:, 1] - boxes_np[0:-1, 1])
        tmp[0:next_line_index + 1].sort(order=['f0'])
        tmp[next_line_index + 1:].sort(order=['f0'])
        arr = (boxes_np[:, -1] - 1).astype('int32')
        boxes_sorted = (boxes_np[:, 0:-1])
        avg_width = 0
        for box in boxes_sorted:
            avg_width += box[2] - box[0]
        avg_width = avg_width / len(boxes_sorted)
        _begin = 0
        result_str_code = ""
        substr, index, offset = self.construct_date(boxes_sorted, _begin, arr, avg_width)
        result_str_code += substr + "|"
        substr, _ = self.construct_number(boxes_sorted, index, arr, avg_width, offset + self.magic_numbers[1]*avg_width, 5)
        result_str_code += substr + "|"
        _begin = next_line_index + 1
        substr, index, offset = self.construct_date(boxes_sorted, _begin, arr, avg_width)
        result_str_code += substr + "|"
        substr, _ = self.construct_number(boxes_sorted, index, arr, avg_width, offset + self.magic_numbers[2]*avg_width, 2)
        result_str_code += '\u041F' + substr
        return result_str_code

    def recognize_on_frame(self, frame):
        cap_detected, marking_detected = False, False
        marking = []
        marking_img = None

        rot_img = cv2.rotate(frame, cv2.ROTATE_180)
        index = self.predict_image(PIL.Image.fromarray(rot_img))
        if self.prev_class != 0 and index == 0:
            self.counter += 1
            boxes, markingList, probs = self.caps_predictor.predict(frame, 10, 0.4)
            for i in range(0, len(markingList)):
                if self.classnames[markingList[i]] == 'cap':
                    cap_detected = True
                if self.classnames[markingList[i]] == 'label':
                    marking_detected = True
                    num = i
            if cap_detected and marking_detected:
                box = boxes[num]
                marking_img = frame[
                              int(box[1] - 10):int(box[3] + 10),
                              int(box[0] - 10):int(box[2] + 10)]
                if marking_img.size != 0:
                    boxes, markingList, probs = self.num_predictor.predict(marking_img, 10, 0.4)
                    marking = list(self.get_code(boxes, markingList))
                    # print(marking)
        self.prev_class = index
        return MarkingModel(cap_detected=cap_detected,
                            marking_detected=marking_detected,
                            marking=marking,
                            marking_image=marking_img)
