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
# 活动开始时间
START_TIME = datetime(2022, 2, 1)
# 活动截止时间
END_TIME = datetime(2022, 2, 8)
# 单日卡片限制
DAY_CARDS_LIMIT = 2
# 校徽置信度限制
THRESHOLD = 0.90
