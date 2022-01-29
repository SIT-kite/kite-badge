# -*- coding: utf-8 -*-
# @Time    : 2022/1/29 20:32
# @Author  : sunnysab
# @File    : card.py

import random
from typing import List, Tuple

import psycopg2

from web_config import *

db = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWD, sslmode='disable')


class Card:
    # 卡片编号
    id: int
    # 卡片名称
    name: str
    # 卡片对应的图片（如果无卡片，使用文字）
    image: str
    # 无卡片时的文字
    text: str

    probability: float

    def __init__(self, id, name, image=None, text=None, probability=0.0):
        assert image or text
        self.id, self.name, self.image, self.text = id, name, image, text
        self.probability = probability


_CARD_LIST = [
    Card(0, '无卡片', text='', probability=0.6),
    Card(1, '上应福', image='https://', probability=0.4 * 0.3),
    Card(2, '创新福', image='', probability=0.4 * 0.25),
    Card(3, '博学福', image='', probability=0.4 * 0.20),
    Card(4, '富贵福', image='', probability=0.4 * 0.20),
    Card(5, '康宁福', image='', probability=0.4 * 0.05),
]


def _generate_distribution(card_list: List[Card]) -> List[Tuple[float, Card]]:
    """ 根据卡片的概率列表, 得到卡片的分布, 映射到 [0, 1) 空间.
    返回的列表元素中, 第一个值为其分布的 "顶", 例如, 分布为 [0, 0.5), [0.5, 1) 的两张卡片,
    函数返回为: (0.5, card1), (1, card2) """
    ceil: float = 0.0
    result = []
    for card in card_list:
        ceil += card.probability
        result.append((ceil, card))

    # 最后一张卡片的上边界应该为 1
    assert abs(result[-1][0] - 1.0) < 0.01
    return result


def get_card() -> Card:
    """ 根据概率分配一张卡片 """
    real: float = random.random()
    dist: List = _generate_distribution(_CARD_LIST)
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
