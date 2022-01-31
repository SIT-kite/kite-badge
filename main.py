import base64
import datetime
import os
from typing import Dict, Tuple

import flask
import jwt

from card import *
from scan import detect
from web_config import *

app = flask.Flask('kite-fu')


@app.after_request
def after_request(resp: flask.Response):
    resp.headers['Access-Control-Allow-Origin'] = 'https://cdn.kite.sunnysab.cn'
    resp.headers['Access-Control-Allow-Headers'] = 'Authorization'
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


def decode_jwt(token: str) -> int:
    """ 根据 JWT Token 解析用户 uid """
    info = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    return info['uid']


RESULT_NO_BADGE = 1
RESULT_COUNT_LIMIT = 2
RESULT_CARD = 3
RESULT_END = 4


def response(uid: int, result: int, card: int = 0, status: int = 200) -> Tuple[Dict, int]:
    save_result(uid, result, card)
    return {'code': 0, 'data': {'result': result, 'card': card}}, status


@app.route("/api/badge/image", methods=['POST', 'OPTIONS'])
def upload_image():
    request: flask.Request = flask.request
    uid = flask.g.uid

    if datetime.now() >= END_TIME:  # 活动已结束
        return response(uid, RESULT_END)
    if get_user_today_card_count(uid) >= DAY_CARDS_LIMIT:  # 达到单日最大次数
        return response(uid, RESULT_COUNT_LIMIT)

    if request.headers['Content-Type'].startswith('image/'):
        file = request.data
    elif request.headers['Content-Type'] == 'text/plain':
        file = base64.b64decode(request.data)
    else:
        return '', 400
    path = f'./images/{uid}_{datetime.now().timestamp()}.jpg'
    with open(path, 'wb') as f:
        f.write(file)

    # 识别校徽并对置信度降序后返回
    result = detect(path)[0]
    # result = 1.0
    if result < THRESHOLD:  # 没有识别到校徽
        return response(uid, RESULT_NO_BADGE)

    card: int = get_card()
    return response(uid, RESULT_CARD, card)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
