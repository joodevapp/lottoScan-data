import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rounds_for_period(data, months):
    """기간에 해당하는 회차 필터링"""
    cutoff = datetime.now() - timedelta(days=months * 30)
    filtered = []
    for item in data:
        date = datetime.strptime(item['date'][:10], '%Y-%m-%d')
        if date >= cutoff:
            filtered.append(item)
    return filtered

def calc_stats(rounds):
    """번호별 출현 횟수 계산"""
    counts = defaultdict(int)
    for round_data in rounds:
        for num in round_data['numbers']:
            counts[num] += 1
        # 보너스 번호 제외 (원하면 포함 가능)
    
    stats = [{"number": i, "count": counts[i]} for i in range(1, 46)]
    
    sorted_by_count = sorted(stats, key=lambda x: x['count'], reverse=True)
    top = [x['number'] for x in sorted_by_count[:6]]
    bottom = [x['number'] for x in sorted_by_count[-6:]]
    
    return top, bottom, stats

def generate_number_stats():
    data = load_lotto_data()
    total_rounds = len(data)
    latest_date = data[-1]['date'][:10]
    
    periods = {
        "2개월": 2,
        "6개월": 6,
        "1년": 12,
        "3년": 36,
        "10년": 120
    }
    
    result = {
        "generated_at": latest_date,
        "total_rounds": total_rounds,
    }
    
    # 각 기간별 회차 수 추가
    for name, months in periods.items():
        rounds = get_rounds_for_period(data, months)
        result[name] = len(rounds)
    
    # 기간별 통계
    result["periods"] = {}
    for name, months in periods.items():
        rounds = get_rounds_for_period(data, months)
        top, bottom, stats = calc_stats(rounds)
        result["periods"][name] = {
            "top": top,
            "bottom": bottom,
            "stats": stats
        }
    
    # 저장
    os.makedirs("results/stats", exist_ok=True)
    with open("results/stats/number_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"number_stats.json 생성완료! (총 {total_rounds}회차)")

generate_number_stats()
