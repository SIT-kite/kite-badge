# -*- coding: utf-8 -*-
# @Time    : 2022/1/29 20:32
# @Author  : sunnysab
# @File    : card.py

import random
from typing import List

import psycopg2

from web_config import *
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

db = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                      user=DB_USER, password=DB_PASSWD, sslmode='disable')

_DEFAULT_PROBABILITY_LIST = [
    0.6,  # 无卡片
    0.4 * 0.05,  # 上应福
    0.4 * 0.40,  # 创新福
    0.4 * 0.30,  # 博学福
    0.4 * 0.15,  # 富贵福
    0.4 * 0.10,  # 康宁福
]


def _generate_distribution(probability_list: List[float]) -> List[float]:
    """ 根据卡片的概率列表, 得到卡片的分布, 映射到 [0, 1) 空间.
    返回的列表元素中, 第一个值为其分布的 "顶", 例如, 分布为 [0, 0.5), [0.5, 1) 的两张卡片,
    函数返回为: [0.5, 1] """
    ceil: float = probability_list[0]
    distribution_list = probability_list.copy()
    for i in range(1, len(distribution_list)):
        ceil += probability_list[i]
        distribution_list[i] = ceil

    # 最后一张卡片的上边界应该为 1
    assert abs(distribution_list[-1] - 1.0) < 0.01
    return distribution_list


_DISTRIBUTION = _generate_distribution(_DEFAULT_PROBABILITY_LIST)


def get_card() -> int:
    """ 根据概率分配一张卡片, 返回卡片 ID """
    real: float = random.random()
    result = -1  # 初始卡片为第一张
    for card, p in enumerate(_DISTRIBUTION):
        if real > p:
            result = card
    result += 1
    # 得到 "随机数着落的对应卡片"
    return result


def get_user_today_remaining_times(uid: int) -> int:
    cur = db.cursor()
    cur.execute(
        '''SELECT %s
                + LEAST((SELECT COUNT(*) FROM fu.share_log WHERE uid = 1 AND ts::date = current_date), 1)
                - (SELECT COUNT(*) FROM fu.scan WHERE uid = %s AND ts >= current_date AND result = 3 AND card != 0);''',
        (DAY_CARDS_LIMIT, uid,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def save_result(uid: int, result: int, card: int = None):
    cur = db.cursor()
    cur.execute(
        'INSERT INTO fu.scan (uid, result, card) VALUES (%s, %s, %s)', (uid, result, card))
    db.commit()
    cur.close()


@dataclass
class Card:
    card: int
    ts: str


def get_card_list(uid: int) -> List[Card]:
    cur = db.cursor()
    cur.execute(
        'SELECT card, ts FROM fu.scan WHERE uid = %s AND result = 3 AND card != 0;', (uid,))
    result = list(map(lambda x: Card(x[0], x[1]), cur.fetchall()))
    db.commit()
    cur.close()
    for e in result:
        ts: datetime = e.ts
        e.ts = ts.isoformat()
    return result


def append_share_log(uid: int):
    cur = db.cursor()
    cur.execute('INSERT INTO fu.share_log (uid) VALUES (%s);', (uid,))
    db.commit()
    cur.close()


def hit_card_number(account: str, card_number: str) -> bool:
    cur = db.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM \"user\".identity WHERE student_id = %s AND id_card = %s LIMIT 1;', (account, card_number))
    cnt = cur.fetchone()[0]
    db.commit()
    cur.close()
    return cnt != 0


@dataclass
class User:
    uid: int
    account: str


def query_user(account: str) -> Optional[User]:
    cur = db.cursor()
    cur.execute(
        'SELECT uid, account FROM \"user\".account WHERE account = %s LIMIT 1;', (account,))
    user = cur.fetchone()
    db.commit()
    cur.close()
    if user is None:
        return None
    return User(uid=user[0], account=user[1])


def create_user(account: str) -> User:
    cur = db.cursor()
    cur.execute(
        'INSERT INTO \"user\".account (account) VALUES(%s) RETURNING (uid, account);', (account,))
    user = cur.fetchone()
    db.commit()
    cur.close()
    return User(uid=user[0], account=user[1])
