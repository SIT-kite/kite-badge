#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import sys
from typing import List

from loguru import logger
import cv2
import torch

from yolox.data.data_augment import ValTransform
from yolox.exp import get_exp
from yolox.utils import get_model_info, postprocess


# YOLOX项目路径
yolox_path = r'/root/YOLOX'
sys.path.append(yolox_path)


def init(ckpt_path):
    global model, exp

    # 模型的配置参数信息
    exp = get_exp(yolox_path + '/exps/example/custom/nano.py', None)
    model = exp.get_model()

    logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))

    # 评估模式
    model.eval()

    # 加载模型
    logger.info("loading yolox_nano model")
    ckpt = torch.load(ckpt_path, map_location="cpu")
    # load the model state dict
    model.load_state_dict(ckpt["model"])
    logger.info("loaded yolox_nano model done.")


def inference(img) -> List[float]:
    """
    执行推理
    """
    preproc = ValTransform()
    img, _ = preproc(img, None, exp.test_size)
    img = torch.from_numpy(img).unsqueeze(0)
    img = img.float()

    with torch.no_grad():
        t0 = time.time()
        outputs = model(img)
        outputs = postprocess(
            outputs, exp.num_classes, exp.test_conf,
            exp.nmsthre, class_agnostic=True
        )
        logger.info("Infer time: {:.4f}s".format(time.time() - t0))

    result = []
    if not outputs or not outputs[0]:
        return [0.0]

    for output in outputs[0]:
        scores = output[4] * output[5]
        result.append(scores)

    return sorted(result, reverse=True)


def detect(path: str) -> List[float]:
    # 图片
    img = cv2.imread(path)
    # 模型地址
    result = inference(img)

    return result


init('./sit-badge.pth')
