import base64
import datetime
import os
import random
from typing import Dict, Tuple

import flask
import jwt
import psycopg2

from scan import detect
from web_config import *

app = flask.Flask('kite-fu')


@app.after_request
def after_request(resp: flask.Response):
    resp.headers['Access-Control-Allow-Origin'] = 'cdn.kite.sunnysab.cn'
    return resp


@app.before_request
def auth():
    request: flask.Request = flask.request
    if request.method == 'OPTIONS':
        return '', 200

    try:
        token = request.headers['Authorization']
        token = token[7:].strip()
        flask.g.uid = decode_jwt(token)
    except Exception as _:
        return {'code': 1, 'msg': '凭据无效'}, 200


if not os.path.exists('images/'):
    os.mkdir('images')

db = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWD, sslmode='disable')


def decode_jwt(token: str) -> int:
    """ 根据 JWT Token 解析用户 uid """
    info = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    return info['uid']


def get_card() -> int:
    """ 根据概率分配一张卡片 """
    rand_value = random.randrange(0, 100)

    for i, v in dict(zip(CARDS_PROBABILITY2)):
        if rand_value < v:
            return i


def win_card() -> bool:
    return CARD_PROBABILITY < random.random()


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


def response(uid: int, result: int, card: int = None, status: int = 200) -> Tuple[Dict, int]:
    return {'code': 0, 'data': {'uid': uid, 'result': result, 'card': card}}, status


@app.route("/api/v2/badge/image", methods=['POST', 'OPTIONS'])
def upload_image():
    request: flask.Request = flask.request
    uid = flask.g.uid

    if datetime.now() >= END_TIME:  # 活动已结束
        return response(uid, 5)
    if get_user_today_card_count(uid) >= DAY_CARDS_LIMIT:  # 达到单日最大次数
        return response(uid, 2)

    if request.headers['Content-Type'].startswith('image/'):
        file = request.data
    elif request.headers['Content-Type'] == 'text/plain':
        file = base64.b64decode(request.data)
    else:
        return response(uid, 6, None, 400)
    path = f'./images/{uid}_{datetime.now().timestamp()}.jpg'
    with open(path, 'wb') as f:
        f.write(file)

    # 识别校徽并对置信度降序后返回
    result = detect(path)[0]
    # result = 1.0
    if result < THRESHOLD:  # 没有识别到校徽
        save_result(uid, 1)
        return response(uid, 1)

    if not win_card():  # 没抽中
        save_result(uid, 3)
        return response(uid, 3)

    card = get_card()
    save_result(uid, 4, card)
    return response(uid, 4, card)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
