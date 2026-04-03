import requests
import json
import os

def get_lotto_number(draw_no):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        if data.get('returnValue') == 'success':
            return {
                "draw_no": data['drwNo'],
                "numbers": [
                    data['drwtNo1'], data['drwtNo2'], data['drwtNo3'],
                    data['drwtNo4'], data['drwtNo5'], data['drwtNo6']
                ],
                "bonus_no": data['bnusNo'],
                "date": data['drwNoDate'] + "T00:00:00Z",
                "total_sales_amount": data['totSellamnt'],
                "divisions": [
                    {"prize": data['firstWinamnt'], "winners": data['firstPrzwnerCo']},
                    {"prize": data['secondWinamnt'], "winners": data['secondPrzwnerCo']},
                    {"prize": data['thirdWinamnt'], "winners": data['thirdPrzwnerCo']},
                    {"prize": data['fourthWinamnt'], "winners": data['fourthPrzwnerCo']},
                    {"prize": data['fifthWinamnt'], "winners": data['fifthPrzwnerCo']},
                ],
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

# 마지막 회차 확인
last_draw_no = all_data[-1]['draw_no'] if all_data else 0

# 새 데이터 가져오기
new_data = []
draw_no = last_draw_no + 1
while True:
    result = get_lotto_number(draw_no)
    if result is None:
        break
    new_data.append(result)
    print(f"{draw_no}회차 추가됨")
    draw_no += 1

# 저장
if new_data:
    all_data.extend(new_data)
    os.makedirs("results", exist_ok=True)
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"총 {len(new_data)}개 업데이트 완료!")
else:
    print("새 데이터 없음")
