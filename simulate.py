# -*- coding: utf-8 -*-
# @Time    : 2022/1/31 15:43
# @Author  : sunnysab
# @File    : simulate.py


"""
通过模拟用户在 3-5 天下集齐的频率，进而计算得到概率
设福卡有 0、1、2、3、4 共 5 种，概率由 `_PROBABILITY_LIST` 决定
"""
from random import random

_PROBABILITY_LIST = [0.40, 0.30, 0.15, 0.10, 0.05]
_CARD_LIMIT_PER_DAY = 4


def _generate_distribution() -> list[float]:
    """ 根据卡片的概率列表, 得到卡片的分布, 映射到 [0, 1) 空间. """
    ceil: float = _PROBABILITY_LIST[0]
    distribution_list = _PROBABILITY_LIST.copy()
    for i in range(1, len(_PROBABILITY_LIST)):
        ceil += _PROBABILITY_LIST[i]
        distribution_list[i] = ceil

    # 最后一张卡片的上边界应该为 1
    assert abs(distribution_list[-1] - 1.0) < 0.01
    return distribution_list


_DISTRIBUTION = _generate_distribution()


def _get_single_card() -> int:
    """ 根据概率分配一张卡片, 返回卡片 ID """
    real: float = random()
    result = -1  # 初始卡片为第一张
    for card, p in enumerate(_DISTRIBUTION):
        if real > p:
            result = card
    result += 1
    # 得到 "随机数着落的对应卡片"
    return result


def _get_card(count: int) -> list[int]:
    """ 用户抽一天卡的结果, count 为每天抽卡的上限. """
    return [_get_single_card() for _ in range(count)]


def _is_complete(card_list: list[int]) -> bool:
    """ 判断用户是否集齐卡片 """
    card_set = [False for _ in range(len(_PROBABILITY_LIST))]
    for card in card_list:
        card_set[card] = True

    for e in card_set:
        if not e:
            return False
    return True


def _simulate_one(min_day: int, max_day: int) -> list[bool]:
    """ 对 min_day 到 max_day 的集卡情况模拟一次 """
    i = min_day
    cards = _get_card(_CARD_LIMIT_PER_DAY * i)
    result = []
    while i <= max_day:
        # 记录第 i 天的集齐情况.
        result.append(_is_complete(cards))
        # 再集一天的福卡
        cards.extend(_get_card(_CARD_LIMIT_PER_DAY))
        i += 1
    return result


def _simulate(min_day: int, max_day: int, n: int) -> list[float]:
    """ 模拟 n 次 """
    counts = [0 for _ in range(max_day - min_day + 1)]
    for i in range(n):
        result = _simulate_one(min_day, max_day)
        for j in range(max_day - min_day + 1):
            counts[j] += 1 if result[j] else 0

    result = [e / n for e in counts]
    return result


if __name__ == '__main__':
    min_day = 1
    max_day = 7

    r = _simulate(min_day, max_day, 1000000)
    i = min_day
    while i <= max_day:
        print(f'第 {i} 天概率 {r[i - min_day]}')
        i += 1
