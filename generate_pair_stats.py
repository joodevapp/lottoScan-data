import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import combinations

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rounds_for_period(data, months):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff]

def calc_pair_counts(rounds):
    pair_counts = defaultdict(int)
    for item in rounds:
        for pair in combinations(sorted(item['numbers']), 2):
            pair_counts[pair] += 1
    return pair_counts

def calc_latest_pairs(latest, all_data):
    all_pair_counts = calc_pair_counts(all_data)
    numbers = sorted(latest['numbers'])
    pairs = []
    for pair in combinations(numbers, 2):
        pairs.append({
            "numbers": list(pair),
            "total_count": all_pair_counts[pair]
        })
    pairs.sort(key=lambda x: x['total_count'], reverse=True)
    return pairs[:3]

def calc_recent_5_top_pair(data):
    """역대 기준 최근 5회차 가장 자주 함께 나온 쌍"""
    all_pair_counts = calc_pair_counts(data)
    recent = data[-5:]
    result = []
    for item in reversed(recent):
        pairs = list(combinations(sorted(item['numbers']), 2))
        top_pair = max(pairs, key=lambda p: all_pair_counts[p])
        result.append({
            "round": item['draw_no'],
            "top_pair": list(top_pair)
        })
    return result

def calc_prev_diff(data, months):
    cutoff_now = datetime.now() - timedelta(days=months * 30)
    cutoff_prev = datetime.now() - timedelta(days=months * 60)
    current = [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff_now]
    previous = [item for item in data if cutoff_prev <= datetime.strptime(item['date'][:10], '%Y-%m-%d') < cutoff_now]
    if not current or not previous:
        return {"pair": [], "diff": 0}
    cur_counts = calc_pair_counts(current)
    top_pair = max(cur_counts, key=cur_counts.get)
    prev_counts = calc_pair_counts(previous)
    diff = cur_counts[top_pair] - prev_counts[top_pair]
    return {"pair": list(top_pair), "diff": diff}

def calc_period_stats(data, label, months):
    rounds = get_rounds_for_period(data, months)
    if not rounds:
        return None

    total = len(rounds)
    pair_counts = calc_pair_counts(rounds)

    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
    top_pair = list(sorted_pairs[0][0])
    top_pair_count = sorted_pairs[0][1]

    pairs_3plus = sum(1 for _, count in pair_counts.items() if count >= 3)
    top10 = sorted_pairs[:10]
    top10_avg = round(sum(c for _, c in top10) / len(top10), 1)

    top10_list = []
    for i, (pair, count) in enumerate(top10):
        pct = round(count / total * 100, 1)
        top10_list.append({
            "rank": i + 1,
            "numbers": list(pair),
            "count": count,
            "pct": pct
        })

    return {
        "label": label,
        "round_count": total,
        "top_pair": top_pair,
        "top_pair_count": top_pair_count,
        "pairs_3plus_count": pairs_3plus,
        "top10_avg": top10_avg,
        "prev_period_diff": calc_prev_diff(data, months),
        "top10": top10_list
    }

def generate_pair_stats():
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
            "pairs": calc_latest_pairs(latest, data)
        },
        "recent_5": calc_recent_5_top_pair(data),
        "periods": []
    }

    for label, months in periods:
        print(f"{label} 계산중...")
        result["periods"].append(calc_period_stats(data, label, months))

    os.makedirs("results/stats", exist_ok=True)
    with open("results/stats/pair_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"pair_stats.json 생성완료! (총 {total_rounds}회차)")

generate_pair_stats()
