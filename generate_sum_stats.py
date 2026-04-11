import json
import os
import statistics
from datetime import datetime, timedelta
from collections import defaultdict

SUM_RANGES = [
    ("21~50", 21, 50),
    ("51~100", 51, 100),
    ("101~150", 101, 150),
    ("151~200", 151, 200),
    ("201~257", 201, 257)
]

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_sum_range(total):
    for label, start, end in SUM_RANGES:
        if start <= total <= end:
            return label
    return ""

def get_rounds_for_period(data, months):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff]

def calc_streak(rounds):
    if not rounds:
        return {"range": "", "count": 0}
    latest_range = get_sum_range(sum(rounds[-1]['numbers']))
    count = 0
    for item in reversed(rounds):
        if get_sum_range(sum(item['numbers'])) == latest_range:
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
        cur_counts[get_sum_range(sum(item['numbers']))] += 1
    top_range = max(cur_counts, key=cur_counts.get)
    prev_counts = defaultdict(int)
    for item in previous:
        prev_counts[get_sum_range(sum(item['numbers']))] += 1
    diff = cur_counts[top_range] - prev_counts[top_range]
    return {"range": top_range, "diff": diff}

def calc_period_stats(data, label, months):
    rounds = get_rounds_for_period(data, months)
    if not rounds:
        return None

    total = len(rounds)
    sums = [sum(item['numbers']) for item in rounds]
    avg_sum = round(sum(sums) / total)

    range_counts = defaultdict(int)
    for s in sums:
        range_counts[get_sum_range(s)] += 1

    top_range = max(range_counts, key=range_counts.get)
    max_count = max(range_counts.values())

    ranges = []
    for label_r, _, _ in SUM_RANGES:
        count = range_counts[label_r]
        pct = round(count / total * 100, 1)
        value = round(count / max_count, 4)
        ranges.append({
            "range": label_r,
            "count": count,
            "pct": pct,
            "value": value
        })

    recent_5 = []
    for item in reversed(rounds[-5:]):
        s = sum(item['numbers'])
        recent_5.append({
            "round": item['draw_no'],
            "sum": s,
            "range": get_sum_range(s)
        })

    return {
        "label": label,
        "round_count": total,
        "avg_sum": avg_sum,
        "top_range": top_range,
        "top_range_count": range_counts[top_range],
        "prev_period_diff": calc_prev_diff(data, months),
        "streak": calc_streak(rounds),
        "ranges": ranges,
        "recent_5": recent_5
    }

def generate_sum_stats():
    data = load_lotto_data()
    total_rounds = len(data)
    latest = data[-1]

    # 전체 기간 통계
    all_sums = [sum(item['numbers']) for item in data]
    min_sum = min(all_sums)
    max_sum = max(all_sums)
    min_round = data[all_sums.index(min_sum)]['draw_no']
    max_round = data[all_sums.index(max_sum)]['draw_no']
    median = round(statistics.median(all_sums))

    latest_sum = sum(latest['numbers'])

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
        "all_time": {
            "min_sum": min_sum,
            "min_sum_round": min_round,
            "max_sum": max_sum,
            "max_sum_round": max_round,
            "median": median
        },
        "latest_round": {
            "draw_no": latest['draw_no'],
            "sum": latest_sum,
            "numbers": latest['numbers'],
            "range": get_sum_range(latest_sum)
        },
        "periods": []
    }

    for label, months in periods:
        print(f"{label} 계산중...")
        result["periods"].append(calc_period_stats(data, label, months))

    os.makedirs("results/stats", exist_ok=True)
    with open("results/stats/sum_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"sum_stats.json 생성완료! (총 {total_rounds}회차)")

generate_sum_stats()
