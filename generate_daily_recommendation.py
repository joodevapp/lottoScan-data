import json
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict

def load_lotto_data():
    with open("results/All_Lotto_Data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_rounds_for_period(data, months):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return [item for item in data if datetime.strptime(item['date'][:10], '%Y-%m-%d') >= cutoff]

def build_stats_summary(data):
    rounds = get_rounds_for_period(data, 12)
    
    counts = defaultdict(int)
    for item in rounds:
        for n in item['numbers']:
            counts[n] += 1
    top6 = sorted(counts, key=counts.get, reverse=True)[:6]
    
    pattern_counts = defaultdict(int)
    for item in rounds:
        odd = sum(1 for n in item['numbers'] if n % 2 == 1)
        pattern_counts[f"홀{odd}짝{6-odd}"] += 1
    top_pattern = max(pattern_counts, key=pattern_counts.get) if pattern_counts else "홀3짝3"
    
    avg_sum = round(sum(sum(item['numbers']) for item in rounds) / len(rounds)) if rounds else 129
    
    range_counts = defaultdict(int)
    ranges = [("1~10",1,10),("11~20",11,20),("21~30",21,30),("31~40",31,40),("41~45",41,45)]
    for item in rounds:
        for n in item['numbers']:
            for label, s, e in ranges:
                if s <= n <= e:
                    range_counts[label] += 1
    top_range = max(range_counts, key=range_counts.get) if range_counts else "31~40"
    
    return {
        "top6": top6,
        "top_pattern": top_pattern,
        "avg_sum": avg_sum,
        "top_range": top_range,
        "round_count": len(rounds)
    }

def generate_recommendation(stats):
    prompt = f"""당신은 로또 번호 추천 AI입니다. 아래 통계를 바탕으로 번호를 추천해주세요.

최근 1년({stats['round_count']}회차) 통계:
- 자주 나온 번호 TOP 6: {stats['top6']}
- 가장 많은 홀짝 패턴: {stats['top_pattern']}
- 평균 합계: {stats['avg_sum']}
- 가장 많이 나온 구간: {stats['top_range']}

다음 JSON 형식으로만 응답해주세요. 다른 텍스트는 절대 포함하지 마세요:
{{
  "numbers": [번호1, 번호2, 번호3, 번호4, 번호5, 번호6],
  "reason": "추천 이유 (5~6문장)"
}}

조건:
- 번호는 1~45 사이 서로 다른 6개
- 오름차순 정렬
- reason은 한국어로 통계 기반 설명 (5~6문장, 어떤 번호를 왜 선택했는지, 최근 패턴이 어떤지, 합계와 구간 분포도 설명)"""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }
    )
    
    result = response.json()
    text = result['choices'][0]['message']['content']
    text = text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

def generate_daily_recommendation():
    data = load_lotto_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    ai_path = "results/ai/daily_recommendation.json"
    if os.path.exists(ai_path):
        with open(ai_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {"date": "", "numbers": [], "reason": "", "history": []}
    
    if existing.get("date") == today:
        print(f"오늘({today}) 추천 이미 생성됨")
        return
    
    print(f"{today} 추천 번호 생성중...")
    
    stats = build_stats_summary(data)
    recommendation = generate_recommendation(stats)
    
    history = existing.get("history", [])
    if existing.get("date") and existing.get("numbers"):
        history.insert(0, {
            "date": existing["date"],
            "numbers": existing["numbers"],
            "reason": existing["reason"]
        })
    
    history = history[:14]
    
    result = {
        "date": today,
        "numbers": recommendation["numbers"],
        "reason": recommendation["reason"],
        "history": history
    }
    
    os.makedirs("results/ai", exist_ok=True)
    with open(ai_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"추천 완료! {recommendation['numbers']}")

generate_daily_recommendation()
