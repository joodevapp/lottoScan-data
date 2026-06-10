import json
import os
from collections import Counter

def generate_stats_for_group(data):
    if not data:
        return None
    all_numbers = []
    odd_counts = []
    range_counts = []
    sums = []
    for item in data:
        nums = item['numbers']
        all_numbers.extend(nums)
        odd = sum(1 for n in nums if n % 2 != 0)
        even = 6 - odd
        odd_counts.append(f"{odd}:{even}")
        ranges = [0] * 5
        for n in nums:
            ranges[(n - 1) // 9] += 1
        range_counts.append(tuple(ranges))
        sums.append(sum(nums))
    number_counter = Counter(all_numbers)
    total_draws = len(data)
    number_stats = []
    for n in range(1, 46):
        count = number_counter.get(n, 0)
        number_stats.append({
            "number": n,
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })
    top6 = sorted(number_stats, key=lambda x: x['count'], reverse=True)[:6]
    bottom6 = sorted(number_stats, key=lambda x: x['count'])[:6]
    odd_counter = Counter(odd_counts)
    odd_stats = []
    for pattern, count in sorted(odd_counter.items(), key=lambda x: -x[1]):
        parts = pattern.split(':')
        odd_stats.append({
            "odd": int(parts[0]),
            "even": int(parts[1]),
            "pattern": pattern,
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })
    range_labels = ["1~9", "10~19", "20~29", "30~39", "40~45"]
    range_total = [0] * 5
    for r in range_counts:
        for i in range(5):
            range_total[i] += r[i]
    range_stats_raw = []
    for i, label in enumerate(range_labels):
        range_stats_raw.append({
            "range": label,
            "count": range_total[i],
            "pct": round(range_total[i] / (total_draws * 6) * 100, 1)
        })
    min_pct = min(r["pct"] for r in range_stats_raw)
    max_pct = max(r["pct"] for r in range_stats_raw)
    pct_range = max_pct - min_pct
    range_stats = []
    for r in range_stats_raw:
        if pct_range == 0:
            r["value"] = 1.0
        else:
            r["value"] = round(0.5 + (r["pct"] - min_pct) / pct_range * 0.5, 3)
        range_stats.append(r)
    avg_sum = round(sum(sums) / len(sums), 1)
    sum_counter = Counter()
    for s in sums:
        if s <= 80:
            sum_counter["~80"] += 1
        elif s <= 100:
            sum_counter["81~100"] += 1
        elif s <= 120:
            sum_counter["101~120"] += 1
        elif s <= 140:
            sum_counter["121~140"] += 1
        elif s <= 160:
            sum_counter["141~160"] += 1
        else:
            sum_counter["161~"] += 1
    sum_ranges = ["~80", "81~100", "101~120", "121~140", "141~160", "161~"]
    sum_stats = []
    for label in sum_ranges:
        count = sum_counter.get(label, 0)
        sum_stats.append({
            "range": label,
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })
    recent = []
    for item in data[-10:][::-1]:
        recent.append({
            "draw_no": item['draw_no'],
            "date": item['date'].split('T')[0],
            "numbers": item['numbers'],
            "bonus_no": item['bonus_no']
        })
    return {
        "total_draws": total_draws,
        "top6": top6,
        "bottom6": bottom6,
        "number_stats": number_stats,
        "odd_stats": odd_stats,
        "range_stats": range_stats,
        "avg_sum": avg_sum,
        "sum_stats": sum_stats,
        "recent_10": recent
    }

def main():
    all_json_path = "results/All_Lotto_Data.json"
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    groups = {
        "all": [item for item in all_data if item.get('machine_no') in [1, 2, 3, "1", "2", "3"]],
        "1": [item for item in all_data if str(item.get('machine_no')) == "1"],
        "2": [item for item in all_data if str(item.get('machine_no')) == "2"],
        "3": [item for item in all_data if str(item.get('machine_no')) == "3"],
    }
    summary = {
        "machine1": {"count": len(groups["1"]), "pct": 0},
        "machine2": {"count": len(groups["2"]), "pct": 0},
        "machine3": {"count": len(groups["3"]), "pct": 0},
    }
    total = len(groups["all"])
    if total > 0:
        summary["machine1"]["pct"] = round(summary["machine1"]["count"] / total * 100, 1)
        summary["machine2"]["pct"] = round(summary["machine2"]["count"] / total * 100, 1)
        summary["machine3"]["pct"] = round(summary["machine3"]["count"] / total * 100, 1)
    all_stats = generate_stats_for_group(groups["all"])
    all_avg_sum = all_stats["avg_sum"] if all_stats else 0
    def add_diff(stats):
        if stats is None:
            return None
        diff = round(stats["avg_sum"] - all_avg_sum, 1)
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        stats["avg_sum_diff"] = diff_str
        stats["avg_sum_compare"] = f"전체 평균 {all_avg_sum} 대비 {diff_str}"
        return stats
    result = {
        "summary": summary,
        "all": all_stats,
        "machine1": add_diff(generate_stats_for_group(groups["1"])),
        "machine2": add_diff(generate_stats_for_group(groups["2"])),
        "machine3": add_diff(generate_stats_for_group(groups["3"])),
    }
    os.makedirs("results/stats", exist_ok=True)
    output_path = "results/stats/machine_stats.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"완료! 전체: {len(groups['all'])}회 | 1호기: {len(groups['1'])}회 | 2호기: {len(groups['2'])}회 | 3호기: {len(groups['3'])}회")

main()
