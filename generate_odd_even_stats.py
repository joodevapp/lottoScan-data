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

def get_pattern(numbers):
    odd = sum(1 for n in numbers if n % 2 == 1)
    even = 6 - odd
    return f"홀{odd}짝{even}"

def calc_streak(data):
    if not data:
        return {"pattern": "", "count": 0}
    latest_pattern = get_pattern(data[-1]['numbers'])
    count = 0
    for item in reversed(data):
        if get_pattern(item['numbers']) == latest_pattern:
            count += 1
        else:
            break
    return {"pattern": latest_pattern, "count": count}

def calc_prev_diff(data, months):
    cutoff_now = datetime.now() - timedelta(days=months * 30)
    cutoff_prev = datetime.now() - timedelta(days=months * 60)
    
    current = [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff_now]
    previous = [item for item in data if cutoff_prev <= datetime.strptime(item['date'][:10], '%Y-%m-%d') < cutoff_now]
    
    if not current or not previous:
        return {"pattern": "", "diff": 0}
    
    cur_counts = defaultdict(int)
    for item in current:
        cur_counts[get_pattern(item['numbers'])] += 1
    top_pattern = max(cur_counts, key=cur_counts.get)
    
    prev_counts = defaultdict(int)
    for item in previous:
        prev_counts[get_pattern(item['numbers'])] += 1
    
    diff = cur_counts[top_pattern] - prev_counts[top_pattern]
    return {"pattern": top_pattern, "diff": diff}

def calc_period_stats(data, label, months):
    rounds = get_rounds_for_period(data, months)
    if not rounds:
        return None
    
    pattern_counts = defaultdict(int)
    total_odd = 0
    for item in rounds:
        pattern_counts[get_pattern(item['numbers'])] += 1
        total_odd += sum(1 for n in item['numbers'] if n % 2 == 1)
    
    total = len(rounds)
    avg_odd = round(total_odd / total, 1)
    avg_even = round(6 - avg_odd, 1)
    
    most_pattern = max(pattern_counts, key=pattern_counts.get)
    
    all_patterns = []
    max_count = max(pattern_counts.values()) if pattern_counts else 1
    for odd in range(7):
        even = 6 - odd
        pattern = f"홀{odd}짝{even}"
        count = pattern_counts[pattern]
        pct = round(count / total * 100, 1)
        all_patterns.append({
            "pattern": pattern,
            "count": count,
            "pct": pct,
            "value": round(count / max_count, 4)
        })
    
    recent_5 = []
    for item in reversed(rounds[-5:]):
        recent_5.append({
            "round": item['draw_no'],
            "pattern": get_pattern(item['numbers'])
        })
    
    return {
        "label": label,
        "round_count": total,
        "most_pattern": most_pattern,
        "most_pattern_count": pattern_counts[most_pattern],
        "avg_odd": avg_odd,
        "avg_even": avg_even,
        "prev_period_diff": calc_prev_diff(data, months),
        "streak": calc_streak(rounds),
        "patterns": all_patterns,
        "recent_5": recent_5
    }

def generate_odd_even_stats():
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
    with open("results/stats/odd_even_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"odd_even_stats.json 생성완료! (총 {total_rounds}회차)")

generate_odd_even_stats()
