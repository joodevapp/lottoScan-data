import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

RANGES = [
    ("1~10", 1, 10),
    ("11~20", 11, 20),
    ("21~30", 21, 30),
    ("31~40", 31, 40),
    ("41~45", 41, 45)
]

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_range(number):
    for label, start, end in RANGES:
        if start <= number <= end:
            return label
    return ""

def get_top_range(numbers):
    counts = defaultdict(int)
    for n in numbers:
        counts[get_range(n)] += 1
    return max(counts, key=counts.get)

def get_rounds_for_period(data, months):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff]

def calc_latest_distribution(latest):
    distribution = []
    for label, start, end in RANGES:
        nums = [n for n in latest['numbers'] if start <= n <= end]
        distribution.append({
            "range": label,
            "numbers": sorted(nums),
            "count": len(nums)
        })
    return distribution

def calc_cold_range(data):
    """가장 오래 안 나온 구간"""
    cold = {}
    for label, _, _ in RANGES:
        count = 0
        for item in reversed(data):
            has_range = any(get_range(n) == label for n in item['numbers'])
            if has_range:
                break
            count += 1
        if count > 0:
            cold[label] = count
    if cold:
        return max(cold, key=cold.get), cold[max(cold, key=cold.get)]
    return None, 0

def calc_streak(data):
    if not data:
        return {"range": "", "count": 0}
    latest_range = get_top_range(data[-1]['numbers'])
    count = 0
    for item in reversed(data):
        if get_top_range(item['numbers']) == latest_range:
            count += 1
        else:
            break
    return {"range": latest_range, "count": count}

def calc_prev_diff(data, months):
    cutoff_now = datetime.now() - timedelta(days=months * 30)
    cutoff_prev = datetime.now() - timedelta(days=months * 60)
    current = [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff_now]
    previous = [item for item in data if cutoff_prev <= datetime.strptime(item['date'][:10], '%Y-%m-%d') < cutoff_now]
    if not current or not previous:
        return {"range": "", "diff": 0}
    cur_counts = defaultdict(int)
    for item in current:
        cur_counts[get_top_range(item['numbers'])] += 1
    top_range = max(cur_counts, key=cur_counts.get)
    prev_counts = defaultdict(int)
    for item in previous:
        prev_counts[get_top_range(item['numbers'])] += 1
    diff = cur_counts[top_range] - prev_counts[top_range]
    return {"range": top_range, "diff": diff}

def calc_period_stats(data, label, months):
    rounds = get_rounds_for_period(data, months)
    if not rounds:
        return None

    total = len(rounds)
    range_counts = defaultdict(int)
    for item in rounds:
        for n in item['numbers']:
            range_counts[get_range(n)] += 1

    top_range = max(range_counts, key=range_counts.get)
    bottom_range = min(range_counts, key=range_counts.get)
    max_count = max(range_counts.values())

    # avg text
    avg_per_round = round(range_counts[top_range] / total, 1)
    avg_text = f"회차당 평균 {avg_per_round}개 번호가 {top_range} 구간에서 나왔어요"

    # cold range
    cold_range, cold_rounds = calc_cold_range(rounds)

    # ranges
    ranges = []
    for range_label, _, _ in RANGES:
        count = range_counts[range_label]
        pct = round(count / (total * 6) * 100, 1)
        value = round(count / max_count, 4)
        ranges.append({
            "range": range_label,
            "count": count,
            "pct": pct,
            "value": value
        })

    # recent 5
    recent_5 = []
    for item in reversed(rounds[-5:]):
        recent_5.append({
            "round": item['draw_no'],
            "top_range": get_top_range(item['numbers'])
        })

    return {
        "label": label,
        "round_count": total,
        "top_range": top_range,
        "top_range_count": range_counts[top_range],
        "bottom_range": bottom_range,
        "bottom_range_count": range_counts[bottom_range],
        "avg_text": avg_text,
        "cold_range": cold_range,
        "cold_rounds": cold_rounds,
        "prev_period_diff": calc_prev_diff(data, months),
        "streak": calc_streak(rounds),
        "ranges": ranges,
        "recent_5": recent_5
    }

def generate_range_stats():
    data = load_lotto_data()
    total_rounds = len(data)
    latest = data[-1]

    periods = [
        ("2개월", 2),
        ("6개월", 6),
        ("1년", 12),
        ("3년", 36),
        ("10년", 120)
    ]

    result = {
        "generated_at": latest['date'][:10],
        "total_rounds": total_rounds,
        "latest_round": {
            "draw_no": latest['draw_no'],
            "distribution": calc_latest_distribution(latest)
        },
        "periods": []
    }

    for label, months in periods:
        print(f"{label} 계산중...")
        result["periods"].append(calc_period_stats(data, label, months))

    os.makedirs("results/stats", exist_ok=True)
    with open("results/stats/range_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"range_stats.json 생성완료! (총 {total_rounds}회차)")

generate_range_stats()
