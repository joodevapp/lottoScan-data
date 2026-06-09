import json
import os
import re
import time
from playwright.sync_api import sync_playwright

def get_machine_numbers_from_lottotapa():
    machine_dict = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR'
        )
        page = context.new_page()
        
        print("전체 회차 크롤링중...")
        
        try:
            page.goto('https://lottotapa.com/stat/result_hogi.php', timeout=60000)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(2)
            
            page.select_option('select[name="s_draw"]', '1')
            time.sleep(1)
            
            options = page.query_selector_all('select[name="e_draw"] option')
            last_value = options[-1].get_attribute('value')
            page.select_option('select[name="e_draw"]', last_value)
            time.sleep(1)
            
            page.click('input[type="submit"], button[type="submit"]')
            time.sleep(5)
            
            text = page.inner_text('body')
            
            print(f"텍스트 길이: {len(text)}")
            print(f"샘플:\n{text[:1000]}")
            
            matches = re.findall(r'(\d+)회 로또 당첨번호 \((\d+)호기\)', text)
            print(f"매칭: {len(matches)}개")
            
            for draw_no, machine_no in matches:
                machine_dict[int(draw_no)] = int(machine_no)
            
        except Exception as e:
            print(f"에러: {e}")
        
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
    
    machine_dict = get_machine_numbers_from_lottotapa()
    print(f"크롤링 완료: {len(machine_dict)}회차")
    
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
