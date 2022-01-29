# -*- coding: utf-8 -*-
# @Time    : 2022/1/29 20:32
# @Author  : sunnysab
# @File    : card.py

import random
from typing import List

import psycopg2

from web_config import *

db = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWD, sslmode='disable')

_DEFAULT_PROBABILITY_LIST = [
    0.6,  # 无卡片
    0.4 * 0.3,
    0.4 * 0.25,
    0.4 * 0.20,
    0.4 * 0.20,
    0.4 * 0.05,
]


def _generate_distribution(probability_list: List[float]) -> List[float]:
    """ 根据卡片的概率列表, 得到卡片的分布, 映射到 [0, 1) 空间.
    返回的列表元素中, 第一个值为其分布的 "顶", 例如, 分布为 [0, 0.5), [0.5, 1) 的两张卡片,
    函数返回为: [0.5, 1] """
    ceil: float = 0.0
    distribution_list = probability_list.copy()
    for i in range(len(distribution_list)):
        ceil += probability_list[i]
        distribution_list = ceil

    # 最后一张卡片的上边界应该为 1
    assert abs(distribution_list[-1] - 1.0) < 0.01
    return distribution_list


def generate_probability_list(seed: int) -> List[float]:
    """ 用循环移位的方法, 为每组用户生成不同的概率表. 注意, 列表的第0个元素始终表示 "无卡片" """
    probability_list = _DEFAULT_PROBABILITY_LIST[1:].copy()
    seed %= len(probability_list)

    probability_list = probability_list[seed:] + probability_list[:seed]
    return [_DEFAULT_PROBABILITY_LIST[0]] + probability_list


def get_card(uid: int) -> int:
    """ 根据概率分配一张卡片, 返回卡片 ID """
    real: float = random.random()
    prob: List = generate_probability_list(uid)
    dist: List = _generate_distribution(prob)
    _, result = dist[0]  # 初始卡片为第一张
    for p, card in dist:
        if real < p:
            result = card
        else:
            break
    # 得到 "随机数着落的对应卡片"
    return result


def get_user_today_card_count(uid: int) -> int:
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) FROM fu.scan WHERE uid = %s AND ts >= current_date;', (uid,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def save_result(uid: int, result: int, card: int = None):
    cur = db.cursor()
    cur.execute('INSERT INTO fu.scan (uid, result, card) VALUES (%s, %s, %s)', (uid, result, card))
    cur.close()
