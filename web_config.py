# Web 服务端密钥
JWT_SECRET = ''

# 数据库配置
DB_HOST = ''
DB_NAME = ''
DB_USER = ''
DB_PASSWD = ''

# 福卡的概率列表
CARDS_PROBABILITY = [0.3, 0.3, 0.2, 0.15, 0.05]
# 福卡概率分布, 降序排列
CARDS_PROBABILITY2 = sorted([CARDS_PROBABILITY[i-1] + CARDS_PROBABILITY[i] if i > 0 else CARDS_PROBABILITY[i]
    for i in range(len(CARDS_PROBABILITY))], reverse=True)
# 抽中卡片的概率
CARD_PROBABILITY = 0.35
# 活动截止时间
END_TIME = datetime.date(2022, 2, 10)
# 单日卡片限制
DAY_CARDS_LIMIT = 2
# 校徽置信度限制
THRESHOLD = 0.90