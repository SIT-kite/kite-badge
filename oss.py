import qiniu
from web_config import *

qiniu_auth = qiniu.Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)


def upload_file(key: str, filename: str):
    token = qiniu_auth.upload_token(
        bucket=QINIU_BUCKET_NAME,
        key=key,
    )
    print(token)
    ret, info = qiniu.put_file(
        up_token=token,
        key=key,
        file_path=filename,
        version='v2',
    )
