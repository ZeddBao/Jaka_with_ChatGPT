# 基于yoloV5的AI检测器

import json
import torch
import numpy as np
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.BaseDetector import baseDet
from utils.torch_utils import select_device
from utils.datasets import letterbox

with open('config.json') as f:
    config = json.load(f)
white_list = config["WhiteList"]


class Detector(baseDet):

    def __init__(self):
        super(Detector, self).__init__()
        self.init_model()  # 初始化模型和配置
        self.build_config()

    def init_model(self):

        self.weights = 'weights/yolov5s.pt'  # 模型权重路径
        self.device = '0' if torch.cuda.is_available() else 'cpu'  # 根据GPU是否可用选择设备
        self.device = select_device(self.device)  # 选择设备
        model = attempt_load(self.weights, map_location=self.device)  # 加载模型
        model.to(self.device).eval()  # 将模型加载到设备并设置为评估模式
        model.half()  # 将模型的权重和输入张量转换为半精度
        # torch.save(model, 'test.pt')
        self.m = model
        self.names = model.module.names if hasattr(
            model, 'module') else model.names  # 从模型中提取类别名称

    def preprocess(self, img):

        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half()  # 半精度
        img /= 255.0  # 图像归一化
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return img0, img

    def detect(self, im):
        global white_list
        im0, img = self.preprocess(im)  # 预处理输入图像

        pred = self.m(img, augment=False)[0]  # 进行推理并获得预测框
        pred = pred.float()
        pred = non_max_suppression(pred, self.threshold, 0.4)  # 非极大值抑制，去除冗余框

        pred_boxes = []  # 存储检测到的目标框
        for det in pred:

            if det is not None and len(det):
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()  # 将预测框缩放到原始图像大小

                for *x, conf, cls_id in det:
                    lbl = self.names[int(cls_id)]  # 获取类别名称
                    if lbl not in white_list:
                        continue
                    x1, y1 = int(x[0]), int(x[1])
                    x2, y2 = int(x[2]), int(x[3])
                    pred_boxes.append(
                        (x1, y1, x2, y2, lbl, conf))  # conf是置信度

        # for box in pred_boxes:
        #     x1, y1, x2, y2, lbl, conf = box
        #     print(lbl)
        return im, pred_boxes  # im是原始图像，pred_boxes是检测到的目标框参数
