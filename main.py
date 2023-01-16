from web_config import *
import base64
import datetime
import os
from typing import Dict, Tuple

import flask
import jwt

from card import *
# from scan import detect


def detect():
    return 1


path_prefix = "/badge"
app = flask.Flask('kite-fu')


# @app.after_request
# def after_request(resp: flask.Response):
#     resp.headers['Access-Control-Allow-Origin'] = 'https://cdn.kite.sunnysab.cn'
#     resp.headers['Access-Control-Allow-Headers'] = 'Authorization'
#     return resp


@app.before_request
def auth():
    request: flask.Request = flask.request
    if request.path == f'{path_prefix}/login':
        return None

    if request.method == 'OPTIONS':
        return '', 200

    try:
        token = request.headers['Authorization']
        token = token[7:].strip()
        flask.g.uid = decode_jwt(token)
    except Exception as _:
        return {'code': 1, 'msg': '凭据无效'}, 200


def decode_jwt(token: str) -> int:
    """ 根据 JWT Token 解析用户 uid """
    info = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    return info['uid']


RESULT_NO_BADGE = 1
RESULT_REACH_LIMIT = 2
RESULT_CARD = 3
RESULT_END = 4
RESULT_START = 5


@app.route(f"{path_prefix}/login", methods=['POST'])
def login():
    request: flask.Request = flask.request
    json = request.get_json()
    account = json['account']
    password = json['password']
    if not hit_card_number(account, password):
        return {'code': 5, 'msg': '凭据认证失败', }

    user = query_user(account)
    if user is None:
        user = create_user(account)

    return {
        'code': 0,
        'data': {
            'token': jwt.encode({'uid': user.uid}, JWT_SECRET, algorithm='HS256'),
            'profile': {
                'uid': user.uid,
                'account': user.account,
            }
        },
    }


@app.route(f"{path_prefix}/image", methods=['POST', 'OPTIONS'])
def upload_image():
    def response(uid: int, result: int, card: int = 0, status: int = 200) -> Tuple[Dict, int]:
        save_result(uid, result, card)
        return {'code': 0, 'data': {'result': result, 'card': card}}, status

    request: flask.Request = flask.request
    uid = flask.g.uid

    if datetime.now() < START_TIME:  # 活动未开始
        return response(uid, RESULT_START)
    if datetime.now() >= END_TIME:  # 活动已结束
        return response(uid, RESULT_END)
    if get_user_today_remaining_times(uid) == 0:  # 达到单日最大次数
        return response(uid, RESULT_REACH_LIMIT)

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


@app.route(f"{path_prefix}/card/", methods=['GET'])
def get_my_cards():
    uid = flask.g.uid
    return {
        'code': 0,
        'data': get_card_list(uid),
    }


@app.route(f"{path_prefix}/result", methods=['GET'])
def get_result():
    return {
        'code': 0,
        'data': {
            'url': None,
        },
    }


@app.route(f"{path_prefix}/share", methods=['POST'])
def share():
    uid = flask.g.uid
    append_share_log(uid)
    return {
        'code': 0,
        'data': {},
    }


if __name__ == '__main__':
    if not os.path.exists('images/'):
        os.mkdir('images')
    app.run(host='0.0.0.0', port=5001, debug=False)
