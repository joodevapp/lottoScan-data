import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rounds_for_period(data, months):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff]

def calc_prev_diff(data, months):
    cutoff_now = datetime.now() - timedelta(days=months * 30)
    cutoff_prev = datetime.now() - timedelta(days=months * 60)
    current = [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff_now]
    previous = [item for item in data if cutoff_prev <= datetime.strptime(item['date'][:10], '%Y-%m-%d') < cutoff_now]
    if not current or not previous:
        return {"number": 0, "diff": 0}
    cur_counts = defaultdict(int)
    for item in current:
        for n in item['numbers']:
            cur_counts[n] += 1
    top_num = max(cur_counts, key=cur_counts.get)
    prev_counts = defaultdict(int)
    for item in previous:
        for n in item['numbers']:
            prev_counts[n] += 1
    diff = cur_counts[top_num] - prev_counts[top_num]
    return {"number": top_num, "diff": diff}

def calc_period_stats(data, label, months):
    rounds = get_rounds_for_period(data, months)
    if not rounds:
        return None

    total = len(rounds)
    counts = defaultdict(int)
    for item in rounds:
        for n in item['numbers']:
            counts[n] += 1

    stats = [{"number": i, "count": counts[i]} for i in range(1, 46)]
    sorted_desc = sorted(stats, key=lambda x: x['count'], reverse=True)
    sorted_asc = sorted(stats, key=lambda x: x['count'])

    top6 = [{"number": x['number'], "count": x['count']} for x in sorted_desc[:6]]
    bottom6 = [{"number": x['number'], "count": x['count']} for x in sorted_asc[:6]]
    top_number = sorted_desc[0]['number']
    top_count = sorted_desc[0]['count']
    max_count = sorted_desc[0]['count']

    for s in stats:
        s['value'] = round(s['count'] / max_count, 4) if max_count > 0 else 0

    # 횟수 높은순
    stats_by_count = sorted(
        [{"number": s['number'], "count": s['count'], "value": s['value']} for s in stats],
        key=lambda x: x['count'],
        reverse=True
    )

    return {
        "label": label,
        "round_count": total,
        "top_number": top_number,
        "top_count": top_count,
        "top6": top6,
        "bottom6": bottom6,
        "prev_period_diff": calc_prev_diff(data, months),
        "stats": stats,
        "stats_by_count": stats_by_count
    }

def generate_number_stats():
    data = load_lotto_data()
    total_rounds = len(data)
    latest_date = data[-1]['date'][:10]

    periods = [
        ("2개월", 2),
        ("6개월", 6),
        ("1년", 12),
        ("3년", 36),
        ("10년", 120)
    ]

    result = {
        "generated_at": latest_date,
        "total_rounds": total_rounds,
        "periods": []
    }

    for label, months in periods:
        print(f"{label} 계산중...")
        result["periods"].append(calc_period_stats(data, label, months))

    os.makedirs("results/stats", exist_ok=True)
    with open("results/stats/number_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"number_stats.json 생성완료! (총 {total_rounds}회차)")

generate_number_stats()
