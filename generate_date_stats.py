import json
import os
from collections import Counter

# 소수 목록 (1~45)
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}

def get_day_from_date(date_str):
    try:
        date_part = date_str.split('T')[0]
        day = int(date_part.split('-')[2])
        return day
    except:
        return None

def calc_ac(numbers):
    sorted_nums = sorted(numbers)
    differences = set()
    for i in range(len(sorted_nums)):
        for j in range(i + 1, len(sorted_nums)):
            differences.add(sorted_nums[j] - sorted_nums[i])
    return len(differences) - 5

def calc_stats_for_group(draws):
    if not draws:
        return None

    total_draws = len(draws)
    all_numbers = []

    odd_counts = []
    low_high_counts = []
    range_counts_list = []
    sums = []
    tens_sums = []
    units_sums = []
    ac_values = []
    prime_counts = []
    color_counts_list = []
    max_gaps = []
    consecutive_count = 0
    multiple3_counts = []
    duplicate_units_count = 0
    pair_counter = Counter()

    for item in draws:
        nums = sorted(item['numbers'])
        all_numbers.extend(nums)

        # 홀짝
        odd = sum(1 for n in nums if n % 2 != 0)
        even = 6 - odd
        odd_counts.append(f"{odd}:{even}")

        # 저고 (1~22 저, 23~45 고)
        low = sum(1 for n in nums if n <= 22)
        high = 6 - low
        low_high_counts.append(f"{low}:{high}")

        # 구간 분포
        ranges = [0] * 5
        for n in nums:
            ranges[(n - 1) // 9] += 1
        range_counts_list.append(ranges)

        # 합계
        s = sum(nums)
        sums.append(s)

        # 십의자리 합
        tens_sum = sum(n // 10 for n in nums)
        tens_sums.append(tens_sum)

        # 일의자리 합
        units_sum = sum(n % 10 for n in nums)
        units_sums.append(units_sum)

        # AC값
        ac = calc_ac(nums)
        ac_values.append(ac)

        # 소수 개수
        prime_count = sum(1 for n in nums if n in PRIMES)
        prime_counts.append(prime_count)

        # 색상별 개수 (노랑:1~10, 파랑:11~20, 빨강:21~30, 회색:31~40, 초록:41~45)
        colors = [0] * 5
        for n in nums:
            if n <= 10: colors[0] += 1
            elif n <= 20: colors[1] += 1
            elif n <= 30: colors[2] += 1
            elif n <= 40: colors[3] += 1
            else: colors[4] += 1
        color_counts_list.append(colors)

        # 번호 간 최대 간격
        gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        max_gaps.append(max(gaps))

        # 연속번호 여부
        has_consecutive = any(nums[i+1] - nums[i] == 1 for i in range(len(nums)-1))
        if has_consecutive:
            consecutive_count += 1

        # 3의 배수 개수
        multiple3_count = sum(1 for n in nums if n % 3 == 0)
        multiple3_counts.append(multiple3_count)

        # 끝수 중복 여부
        units_digits = [n % 10 for n in nums]
        if len(units_digits) != len(set(units_digits)):
            duplicate_units_count += 1

        # 페어
        for i in range(len(nums)):
            for j in range(i+1, len(nums)):
                pair = (nums[i], nums[j])
                pair_counter[pair] += 1

    # 번호별 통계
    number_counter = Counter(all_numbers)
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

    # 홀짝 분포
    odd_counter = Counter(odd_counts)
    odd_stats = []
    for pattern, count in sorted(odd_counter.items(), key=lambda x: -x[1]):
        parts = pattern.split(':')
        odd_stats.append({
            "pattern": pattern,
            "odd": int(parts[0]),
            "even": int(parts[1]),
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 저고 분포
    low_high_counter = Counter(low_high_counts)
    low_high_stats = []
    for pattern, count in sorted(low_high_counter.items(), key=lambda x: -x[1]):
        parts = pattern.split(':')
        low_high_stats.append({
            "pattern": pattern,
            "low": int(parts[0]),
            "high": int(parts[1]),
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 구간 분포
    range_labels = ["1~9", "10~19", "20~29", "30~39", "40~45"]
    range_total = [0] * 5
    for r in range_counts_list:
        for i in range(5):
            range_total[i] += r[i]
    range_stats = []
    for i, label in enumerate(range_labels):
        range_stats.append({
            "range": label,
            "count": range_total[i],
            "pct": round(range_total[i] / (total_draws * 6) * 100, 1)
        })

    # 합계 통계
    avg_sum = round(sum(sums) / total_draws, 1)
    sum_counter = Counter()
    for s in sums:
        if s <= 80: sum_counter["~80"] += 1
        elif s <= 100: sum_counter["81~100"] += 1
        elif s <= 120: sum_counter["101~120"] += 1
        elif s <= 140: sum_counter["121~140"] += 1
        elif s <= 160: sum_counter["141~160"] += 1
        else: sum_counter["161~"] += 1
    sum_ranges = ["~80", "81~100", "101~120", "121~140", "141~160", "161~"]
    sum_stats_raw = []
    for label in sum_ranges:
        count = sum_counter.get(label, 0)
        sum_stats_raw.append({
            "range": label,
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })
    max_sum_pct = max(r["pct"] for r in sum_stats_raw) if sum_stats_raw else 1
    min_sum_pct = min(r["pct"] for r in sum_stats_raw) if sum_stats_raw else 0
    sum_pct_range = max_sum_pct - min_sum_pct
    sum_stats = []
    for r in sum_stats_raw:
        if sum_pct_range == 0:
            r["value"] = 1.0
        else:
            r["value"] = round(0.5 + (r["pct"] - min_sum_pct) / sum_pct_range * 0.5, 3)
        sum_stats.append(r)

    # AC값 통계
    avg_ac = round(sum(ac_values) / total_draws, 1)
    ac_counter = Counter(ac_values)
    ac_stats = []
    for ac_val in sorted(ac_counter.keys()):
        count = ac_counter[ac_val]
        ac_stats.append({
            "ac": ac_val,
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 소수 개수 분포
    prime_counter = Counter(prime_counts)
    prime_stats = []
    for prime_count in sorted(prime_counter.keys()):
        count = prime_counter[prime_count]
        prime_stats.append({
            "count": prime_count,
            "draws": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 색상별 통계
    color_labels = ["노랑(1~10)", "파랑(11~20)", "빨강(21~30)", "회색(31~40)", "초록(41~45)"]
    color_totals = [0] * 5
    for c in color_counts_list:
        for i in range(5):
            color_totals[i] += c[i]
    color_stats = []
    for i, label in enumerate(color_labels):
        color_stats.append({
            "color": label,
            "total": color_totals[i],
            "avg": round(color_totals[i] / total_draws, 2)
        })

    # 3의 배수 분포
    multiple3_counter = Counter(multiple3_counts)
    multiple3_stats = []
    for m3_count in sorted(multiple3_counter.keys()):
        count = multiple3_counter[m3_count]
        multiple3_stats.append({
            "count": m3_count,
            "draws": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 페어 top10
    top_pairs = []
    for pair, count in pair_counter.most_common(10):
        top_pairs.append({
            "numbers": list(pair),
            "count": count,
            "pct": round(count / total_draws * 100, 1)
        })

    # 최근 추첨 회차
    latest_draw = max(draws, key=lambda x: x['draw_no'])

    return {
        "has_data": True,
        "total_draws": total_draws,
        "latest_draw_no": latest_draw['draw_no'],
        "top6": top6,
        "bottom6": bottom6,
        "odd_stats": odd_stats,
        "low_high_stats": low_high_stats,
        "range_stats": range_stats,
        "avg_sum": avg_sum,
        "sum_stats": sum_stats,
        "avg_tens_sum": round(sum(tens_sums) / total_draws, 1),
        "avg_units_sum": round(sum(units_sums) / total_draws, 1),
        "avg_ac": avg_ac,
        "ac_stats": ac_stats,
        "prime_stats": prime_stats,
        "color_stats": color_stats,
        "avg_max_gap": round(sum(max_gaps) / total_draws, 1),
        "consecutive_pct": round(consecutive_count / total_draws * 100, 1),
        "multiple3_stats": multiple3_stats,
        "duplicate_units_pct": round(duplicate_units_count / total_draws * 100, 1),
        "top_pairs": top_pairs,
    }

def main():
    all_json_path = "results/All_Lotto_Data.json"

    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    # 날짜별로 그룹화
    date_groups = {}
    for item in all_data:
        day = get_day_from_date(item.get('date', ''))
        if day is None:
            continue
        if day not in date_groups:
            date_groups[day] = []
        date_groups[day].append(item)

    result = {}
    for day in range(1, 32):
        draws = date_groups.get(day, [])
        if not draws:
            result[str(day)] = {"has_data": False}
        else:
            stats = calc_stats_for_group(draws)
            result[str(day)] = stats

    os.makedirs("results/stats", exist_ok=True)
    output_path = "results/stats/date_stats.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("날짜별 통계 생성 완료!")
    for day in range(1, 32):
        draws = date_groups.get(day, [])
        status = f"{len(draws)}회차" if draws else "데이터 없음"
        print(f"{day:2d}일: {status}")

main()
