import requests
import json
import os
import csv

def get_latest_draw_info():
    """All_Lotto_Data.json에서 최신 회차 정보 가져오기"""
    all_json_path = "results/All_Lotto_Data.json"
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    return all_data[-1]['draw_no'], all_data[-1]['date'][:10]

def get_winning_stores(draw_no):
    """동행복권 API에서 1등 당첨 판매점 가져오기"""
    url = f'https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do?srchWnShpRnk=1&srchLtEpsd={draw_no}&srchShpLctn='
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = res.json()
        stores = []
        for item in data['data']['list']:
            stores.append({
                "name": item['shpNm'],
                "address": item['shpAddr'].strip(),
                "combination": item['atmtPsvYnTxt']
            })
        return stores
    except Exception as e:
        print(f"판매점 Error: {e}")
        return []

def update_all_winning_stores(draw_no, date, stores):
    """all_winning_stores.json 업데이트"""
    json_path = "results/all_winning_stores.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            all_stores = json.load(f)
    else:
        all_stores = []

    existing_rounds = [s['round'] for s in all_stores]
    if draw_no in existing_rounds:
        print(f"{draw_no}회차 판매점 데이터 이미 존재")
        return False

    all_stores.insert(0, {
        "round": draw_no,
        "date": date,
        "stores": stores
    })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_stores, f, ensure_ascii=False, indent=2)
    print(f"{draw_no}회차 판매점 {len(stores)}개 추가완료!")
    return True

def update_lotto_db_csv(draw_no, date, stores):
    """lotto_db_final.csv 업데이트"""
    csv_path = "results/lotto_db_final.csv"
    
    rows = {}
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['store_name'], row['address'])
                rows[key] = {
                    'store_name': row['store_name'],
                    'address': row['address'],
                    'sido': row['sido'],
                    'gugun': row['gugun'],
                    'win1': int(row['win1']),
                    'latest_round': int(row['latest_round']),
                    'latest_date': row['latest_date']
                }

    for store in stores:
        name = store['name']
        address = store['address']
        
        addr_parts = address.split(' ')
        sido = addr_parts[0] if len(addr_parts) > 0 else ''
        gugun = addr_parts[1] if len(addr_parts) > 1 else ''

        key = (name, address)
        if key in rows:
            rows[key]['win1'] = rows[key]['win1'] + 1
            rows[key]['latest_round'] = draw_no
            rows[key]['latest_date'] = date
        else:
            rows[key] = {
                'store_name': name,
                'address': address,
                'sido': sido,
                'gugun': gugun,
                'win1': 1,
                'latest_round': draw_no,
                'latest_date': date
            }

    # win1 내림차순 정렬
    sorted_rows = sorted(rows.values(), key=lambda x: x['win1'], reverse=True)
    
    # rank 부여 (동점이면 같은 순위)
    rank = 1
    prev_win1 = None
    for i, row in enumerate(sorted_rows):
        if row['win1'] != prev_win1:
            rank = i + 1
        row['rank'] = rank
        prev_win1 = row['win1']
    
    with open(csv_path, "w", encoding="utf-8-sig", newline='') as f:
        fieldnames = ['rank', 'store_name', 'address', 'sido', 'gugun', 'win1', 'latest_round', 'latest_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    
    print(f"CSV 업데이트 완료! 총 {len(sorted_rows)}개 판매점")

# 메인 실행
draw_no, date = get_latest_draw_info()
print(f"최신 회차: {draw_no}, 날짜: {date}")

stores = get_winning_stores(draw_no)
print(f"판매점 {len(stores)}개 가져옴")

if stores:
    updated = update_all_winning_stores(draw_no, date, stores)
    if updated:
        update_lotto_db_csv(draw_no, date, stores)
else:
    print("판매점 데이터 없음 (아직 업데이트 안됐을 수 있음)")
