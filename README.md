# 2022 虎年 "五福" 活动

该活动借鉴支付宝 “扫福赢福卡” 活动, 通过 "扫校徽赢福卡" 的方式展开, 当用户集齐全套福卡后, 可以前往易班工作站领取奖品. 项目于 2021 年底由上海应用技术大学易班工作站发起，技术部分由技术部负责.

技术上, 前端部分由 flutter 和 js 语言混合编写，见 [kite-fu](https://github.com/SIT-kite/kite-fu). 当前仓库为后端仓库, 使用 Python 语言构建 (作者的 python 版本为 3.9), 作为 [kite-server](https://github.com/SIT-kite/kite-server) 的补充发布. 

## 文档

文档参见 [kite-server/docs/APIv2/集五福.md](https://github.com/SIT-kite/kite-server/blob/v2/docs/APIv2/%E9%9B%86%E4%BA%94%E7%A6%8F.md).

## 安装

###  环境准备

在安装 `yolox` 之前，先要安装 `pytorch`。

```bash
pip3 install torch
```

然后再安装 `yolox` 环境. 按照[官方的安装指南](https://github.com/Megvii-BaseDetection/YOLOX#quick-start)：

```bash
git clone https://github.com/Megvii-BaseDetection/YOLOX.git
cd YOLOX
pip3 install -v -e .  # or  python3 setup.py develop
```
注意，请预留至少 5GB 的存储空间。

### 修改参数

由于模型仅包括校徽图样，请在 `/YOLOX/exps/example/custom/nano.py` 中，将：

```python
self.num_classes = 71
```
改为
```python
self.num_classes = 1
```

### 使用

下载项目：
```
git clone https://github.com/SIT-kite/kite-badge.git
cd kite-badge
```

进入目录我们可以看到，`sit-badge.pth` 是训练出的模型，`scan.py` 是识别脚本（由 [@wanfengcxz](https://github.com/wanfengcxz) 友情编写），`main.py` 是服务端主程序。
编辑 `main.py`，以下参数按需配置：

```python
# Web 服务端密钥
JWT_SECRET = ''

# 数据库配置
DB_HOST = ''
DB_NAME = ''
DB_USER = ''
DB_PASSWD = ''

# 福卡的概率列表
CARDS_PROBABILITY = [0.20, 0.20, 0.20, 0.20, 0.20]
# 抽中卡片的概率
CARD_PROBABILITY = 0.8
# 活动截止时间
END_TIME = datetime.date(2022, 2, 10)
# 单日卡片限制
DAY_CARDS_LIMIT = 2
# 校徽置信度限制
THRESHOLD = 0.90
```
> 示例参数不代表真实环境下的参数.

由于本项目作为 [kite-server](https://github.com/SIT-kite/kite-server) 的一部分, `JWT_SECRET` 与其保持一致即可.

最后执行 `python3 ./main.py`. 请预留至少 200MB 内存.
