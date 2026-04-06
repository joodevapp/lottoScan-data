import json
import os
import re
from playwright.sync_api import sync_playwright

def get_lotto_data(draw_no):
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
        
        try:
            numbers = page.query_selector_all('.num.win .ball_645')
            bonus = page.query_selector('.num.bonus .ball_645')
            date_el = page.query_selector('.desc')

            print(f"URL: {page.url}")
            print(f"페이지 텍스트: {page.inner_text('body')[:300]}")
            
            if not numbers or len(numbers) < 6:
                browser.close()
                return None
                
            nums = [int(n.inner_text()) for n in numbers]
            bonus_no = int(bonus.inner_text())
            date_text = date_el.inner_text()
            date_match = re.search(r'(\d{4})년\s*(\d{2})월\s*(\d{2})일', date_text)
            date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}T00:00:00Z"
            
            rows = page.query_selector_all('.tbl_data tbody tr')
            divisions = []
            for row in rows[:5]:
                cols = row.query_selector_all('td')
                if len(cols) >= 3:
                    prize_text = cols[1].inner_text().replace(',','').replace('원','').strip()
                    winners_text = cols[2].inner_text().replace(',','').strip()
                    try:
                        prize = int(prize_text)
                        winners = int(winners_text)
                        divisions.append({"prize": prize, "winners": winners})
                    except:
                        pass
            
            total_text = page.inner_text('body')
            total_match = re.search(r'총판매금액\s*:\s*([\d,]+)원', total_text)
            total = int(total_match.group(1).replace(',','')) if total_match else 0
            
            browser.close()
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
            browser.close()
            return None

all_json_path = "results/all.json"
if os.path.exists(all_json_path):
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = []

last_draw_no = all_data[-1]['draw_no'] if all_data else 0
print(f"마지막 회차: {last_draw_no}")

new_data = []
draw_no = last_draw_no + 1
while True:
    print(f"{draw_no}회차 시도중...")
    result = get_lotto_data(draw_no)
    if result is None:
        print(f"{draw_no}회차 데이터 없음, 종료")
        break
    new_data.append(result)
    print(f"{draw_no}회차 추가됨: {result['numbers']}")
    draw_no += 1

if new_data:
    all_data.extend(new_data)
    os.makedirs("results", exist_ok=True)
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"총 {len(new_data)}개 업데이트 완료!")
else:
    print("새 데이터 없음")
