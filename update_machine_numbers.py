import json
import os
import re
import requests
import time

def get_machine_numbers_from_lottotapa():
    machine_dict = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://lottotapa.com/stat/result_hogi.php'
    }
    
    for start in range(262, 1300, 50):
        end = start + 49
        print(f"{start}~{end}회차 크롤링중...")
        
        try:
            r = requests.post(
                'https://lottotapa.com/stat/result_hogi.php',
                headers=headers,
                data={'s_draw': str(start), 'e_draw': str(end)},
                timeout=30
            )
            text = r.text
            matches = re.findall(r'(\d+)회 로또 당첨번호 \((\d+)호기\)', text)
            for draw_no, machine_no in matches:
                machine_dict[int(draw_no)] = int(machine_no)
            print(f"  → {len(matches)}개 수집")
            
            if not matches and start > 1250:
                break
                
        except Exception as e:
            print(f"  → 에러: {e}")
        
        time.sleep(1)
    
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
    
    print(f"업데이트 필요: {len(needs_update)}회차")
    
    machine_dict = get_machine_numbers_from_lottotapa()
    print(f"크롤링 완료: {len(machine_dict)}회차")
    
    updated = 0
    for item in all_data:
        if 'machine_no' not in item or item['machine_no'] == "미정":
            draw_no = item['draw_no']
            item['machine_no'] = "미정" if draw_no < 262 else machine_dict.get(draw_no, "미정")
            updated += 1
    
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"총 {updated}회차 업데이트 완료!")

update_machine_numbers()
