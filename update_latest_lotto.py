import json
import os
import re
from playwright.sync_api import sync_playwright

def get_latest_draw_no():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR',
            timezone_id='Asia/Seoul'
        )
        page = context.new_page()
        page.goto('https://www.dhlottery.co.kr/lt645/result')
        page.wait_for_load_state('networkidle')
        text = page.inner_text('body')
        browser.close()
        # 최신 회차 찾기
        matches = re.findall(r'제\s*(\d+)회\s*추첨\s*결과', text)
        if matches:
            return max([int(m) for m in matches])
        return None

def get_lotto_data_from_page(draw_no):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR',
            timezone_id='Asia/Seoul'
        )
        page = context.new_page()
        page.goto(f'https://www.dhlottery.co.kr/lt645/result?ltEpsd={draw_no}')
        page.wait_for_load_state('networkidle')
        text = page.inner_text('body')
        browser.close()

        try:
            # 해당 회차 블록 찾기
            pattern = rf'제\s*{draw_no}회\s*추첨\s*결과\s*([\d{{4}}년\s\d{{2}}월\s\d{{2}}일]+)\s*추첨\s*당첨번호\s*([\d\s]+)\s*보너스번호\s*(\d+)'
            
            # 날짜 찾기
            date_pattern = rf'제\s*{draw_no}회\s*추첨\s*결과\s*(\d{{4}}\.\d{{2}}\.\d{{2}})\s*추첨'
            date_match = re.search(date_pattern, text)
            if not date_match:
                return None
            
            date_str = date_match.group(1)
            date = date_str.replace('.', '-') + 'T00:00:00Z'
            
            # 해당 회차 위치 찾기
            pos = text.find(f'제 {draw_no}회 추첨 결과')
            if pos == -1:
                return None
            
            block = text[pos:pos+500]
            
            # 번호들 찾기
            nums_pattern = r'당첨번호\s*([\d\s]+)\s*보너스번호\s*(\d+)'
            nums_match = re.search(nums_pattern, block)
            if not nums_match:
                return None
            
            nums = [int(n) for n in nums_match.group(1).split() if n.isdigit()][:6]
            bonus_no = int(nums_match.group(2))
            
            if len(nums) != 6:
                return None
            
            # 당첨금 정보 찾기
            prize_pattern = r'(\d+)등\s*([\d,]+)원\s*(\d+)\s*([\d,]+)원'
            prize_matches = re.findall(prize_pattern, text[pos:pos+2000])
            
            divisions = []
            for m in prize_matches[:5]:
                try:
                    prize = int(m[3].replace(',', ''))
                    winners = int(m[2].replace(',', ''))
                    divisions.append({"prize": prize, "winners": winners})
                except:
                    pass
            
            # 총판매액
            total_match = re.search(r'총판매금액\s*:\s*([\d,]+)원', text[pos:pos+2000])
            total = int(total_match.group(1).replace(',', '')) if total_match else 0
            
            return {
                "draw_no": draw_no,
                "numbers": nums,
                "bonus_no": bonus_no,
                "date": date,
                "total_sales_amount": total,
                "divisions": divisions,
                "winners_combination": {}
            }
        except Exception as e:
            print(f"Error: {e}")
            return None

# all.json 불러오기
all_json_path = "results/all.json"
if os.path.exists(all_json_path):
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = []

last_draw_no = all_data[-1]['draw_no'] if all_data else 0
print(f"마지막 회차: {last_draw_no}")

# 최신 회차 확인
latest_draw_no = get_latest_draw_no()
print(f"최신 회차: {latest_draw_no}")

if latest_draw_no is None or latest_draw_no <= last_draw_no:
    print("새 데이터 없음")
else:
    new_data = []
    for draw_no in range(last_draw_no + 1, latest_draw_no + 1):
        print(f"{draw_no}회차 시도중...")
        result = get_lotto_data_from_page(draw_no)
        if result is None:
            print(f"{draw_no}회차 파싱 실패")
            continue
        new_data.append(result)
        print(f"{draw_no}회차 추가됨: {result['numbers']}")

    if new_data:
        all_data.extend(new_data)
        os.makedirs("results", exist_ok=True)
        with open(all_json_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"총 {len(new_data)}개 업데이트 완료!")
    else:
        print("새 데이터 없음")
