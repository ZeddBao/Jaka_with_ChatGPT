# 基于deepsort的追踪器

from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
import torch
import cv2

# 定义颜色调色板
palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

# 获取 deep_sort 配置
cfg = get_config()
cfg.merge_from_file("deep_sort/configs/deep_sort.yaml")

# 初始化 DeepSort 模型
deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=9999, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=True)


# 绘制 bounding box 的函数
def plot_bboxes(image, bboxes, line_thickness=None):
    # 设置线条粗细，根据图像大小自适应
    tl = line_thickness or round(
        0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness

    # 遍历每个 bounding box
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        # 根据类别设置颜色
        if cls_id in ['person']:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        c1, c2 = (x1, y1), (x2, y2)
        # 在图像上绘制 bounding box
        cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        # 在 bounding box 上方添加类别和 ID
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(cls_id, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image, '{} ID-{}'.format(cls_id, pos_id), (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    return image


# 更新跟踪器的函数
def update_tracker(target_detector, image):
    new_faces = []  # 保存新检测到的人脸
    _, bboxes = target_detector.detect(image)  # 检测图像中的 bounding box

    bbox_xywh = []
    confs = []
    clss = []

    # 将 bounding box 转换为 deep_sort 需要的格式
    for x1, y1, x2, y2, cls_id, conf in bboxes:
        # 计算中心点坐标和边界框宽高
        obj = [
            int((x1 + x2) / 2), int((y1 + y2) / 2),
            x2 - x1, y2 - y1
        ]
        # 将边界框信息存储到列表中
        bbox_xywh.append(obj)
        confs.append(conf)
        clss.append(cls_id)

    # 将边界框信息转换为tensor格式
    xywhs = torch.Tensor(bbox_xywh)
    confss = torch.Tensor(confs)

    # 更新deepsort跟踪器
    outputs = deepsort.update(xywhs, confss, clss, image)

    ####################################################################
    # 存储需要绘制的边界框和人脸边界框
    bboxes2draw = []
    face_bboxes = []
    current_ids = []
    obj_info = []
    for value in list(outputs):
        # 获取跟踪器输出的信息
        x1, y1, x2, y2, cls_, track_id = value
        # 存储需要展示的边界框和跟踪ID
        bboxes2draw.append(
            (x1, y1, x2, y2, cls_, track_id)
        )

        current_ids.append(track_id)

        obj_info.append(
            ((x1 + x2) / 2, (y1 + y2) / 2, (x1 - x2) * (y1 - y2), track_id)
        )
        # 如果是人脸，则将人脸信息存储到列表中
        if cls_ == 'face':
            if not track_id in target_detector.faceTracker:
                target_detector.faceTracker[track_id] = 0
                face = image[y1:y2, x1:x2]
                new_faces.append((face, track_id))
            face_bboxes.append(
                (x1, y1, x2, y2)
            )
    ####################################################################

    # 存储需要删除的跟踪ID
    ids2delete = []
    for history_id in target_detector.faceTracker:
        if not history_id in current_ids:
            target_detector.faceTracker[history_id] -= 1
        if target_detector.faceTracker[history_id] < -9999:
            ids2delete.append(history_id)

    # 删除跟踪ID并输出提示信息
    for ids in ids2delete:
        target_detector.faceTracker.pop(ids)
        print('-[INFO] Delete track id:', ids)

    # 在图像上绘制边界框并返回图像、新的人脸列表和人脸边界框列表
    image = plot_bboxes(image, bboxes2draw)

    return image, new_faces, face_bboxes, obj_info
