from datetime import datetime

# Web 服务端密钥
JWT_SECRET = ''

# 数据库配置
DB_HOST = ''
DB_NAME = ''
DB_USER = ''
DB_PASSWD = ''

# 抽中卡片的概率
CARD_PROBABILITY = 0.35
# 活动截止时间
END_TIME = datetime(2022, 2, 10)
# 单日卡片限制
DAY_CARDS_LIMIT = 2
# 校徽置信度限制
THRESHOLD = 0.90
