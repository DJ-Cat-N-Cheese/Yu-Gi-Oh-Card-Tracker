import json

with open('data/db/card_db.json', 'r') as f:
    db = json.load(f)

print("Checking RA03-EN004 in DB")
for card in db:
    for v in card['card_sets']:
        if v['set_code'] == 'RA03-EN004':
            print(f"Card: {card['name']}, Set: {v['set_code']} - {v['set_rarity']}")

print("Checking IOC-EN025 in DB")
for card in db:
    for v in card['card_sets']:
        if v['set_code'] == 'IOC-EN025':
            print(f"Card: {card['name']}, Set: {v['set_code']} - {v['set_rarity']}")
