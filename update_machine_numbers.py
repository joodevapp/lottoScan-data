import json
import os
import re
import time
from playwright.sync_api import sync_playwright

def get_machine_numbers_from_lottotapa(start_round, end_round):
    machine_dict = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR'
        )
        page = context.new_page()
        
        print(f"{start_round}~{end_round}회차 크롤링중...")
        
        try:
            page.goto('https://lottotapa.com/stat/result_hogi.php', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(2)
            
            # 시작회차 드롭다운 선택
            page.select_option('select[name="s_draw"]', str(start_round))
            time.sleep(1)
            
            # 마지막회차 드롭다운 선택
            page.select_option('select[name="e_draw"]', str(end_round))
            time.sleep(1)
            
            # 검색 버튼 클릭
            page.click('input[type="submit"], button[type="submit"]')
            time.sleep(3)
            
            text = page.inner_text('body')
            
            matches = re.findall(r'(\d+)회 로또 당첨번호 \((\d+)호기\)', text)
            for draw_no, machine_no in matches:
                machine_dict[int(draw_no)] = int(machine_no)
            
            print(f"  → {len(matches)}개 호기 정보 수집")
            
        except Exception as e:
            print(f"  → 에러: {e}")
        
        browser.close()
    
    return machine_dict

def update_machine_numbers():
    all_json_path = "results/All_Lotto_Data.json"
    
    if not os.path.exists(all_json_path):
        print("All_Lotto_Data.json 없음")
        return
    
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    
    needs_update = [item for item in all_data if 'machine_no' not in item or item['machine_no'] == "미정"]
    
    if not needs_update:
        print("모든 회차에 machine_no 있음")
        return
    
    print(f"machine_no 업데이트 필요: {len(needs_update)}회차")
    
    rounds_to_fetch = [item['draw_no'] for item in needs_update if item['draw_no'] >= 262]
    
    if rounds_to_fetch:
        min_round = min(rounds_to_fetch)
        max_round = max(rounds_to_fetch)
        print(f"로또타파 크롤링: {min_round}~{max_round}회차")
        machine_dict = get_machine_numbers_from_lottotapa(min_round, max_round)
        print(f"크롤링 완료: {len(machine_dict)}회차")
    else:
        machine_dict = {}
    
    updated = 0
    for item in all_data:
        if 'machine_no' not in item or item['machine_no'] == "미정":
            draw_no = item['draw_no']
            if draw_no < 262:
                item['machine_no'] = "미정"
            else:
                item['machine_no'] = machine_dict.get(draw_no, "미정")
            updated += 1
    
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"총 {updated}회차 업데이트 완료!")

update_machine_numbers()
