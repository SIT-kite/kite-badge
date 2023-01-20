import csv
from typing import Dict

# Dict[uid, Dict[card, count]]
scan_table: Dict[int, Dict[int, int]] = {}

with open('2022_scan.csv') as f:
    csv_reader = csv.reader(f)

    for uid, _, card, _ in csv_reader:
        uid = int(uid)
        card = int(card)
        if card == 0:
            continue

        if uid not in scan_table.keys():
            scan_table[uid] = {}
        if card not in scan_table[uid].keys():
            scan_table[uid][card] = 0
        scan_table[uid][card] += 1


# Dict[uid, (account, name)]
account_table: Dict[int, (str, str)] = {}

with open('account.csv') as f:
    csv_reader = csv.reader(f)

    for uid, account, _, _, _, name in csv_reader:
        uid = int(uid)
        account_table[uid] = (account, name)

output = []
for uid, cards in scan_table.items():
    if len(cards) == 5:
        output.append((uid, cards))

# 按uid排序
output.sort(key=lambda x: x[0])

for i, item in enumerate(output):
    # print(i+1, item[0], account_table[item[0]], item[1])
    print(i+1, ' ', account_table[item[0]])
