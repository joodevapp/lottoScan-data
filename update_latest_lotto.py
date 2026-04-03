import requests
import json
import os

def get_lotto_number(draw_no):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dhlottery.co.kr/gameResult.do?method=byWin',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {res.status_code}")
        print(f"Response: {res.text[:200]}")
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
        print(f"Error fetching: {e}")
    return None

# all.json 불러오기
all_json_path = "results/all.json"
if os.path.exists(all_json_path):
    with open(all_json_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"파일 크기: {len(content)} bytes")
    print(f"마지막 50글자: {repr(content[-50:])}")
    try:
        all_data = json.loads(content)
        print(f"파싱 성공! 총 {len(all_data)}개 회차")
    except json.JSONDecodeError as e:
        print(f"파싱 실패: {e}")
        exit(1)
else:
    all_data = []
    print("파일 없음")

# 마지막 회차 확인
last_draw_no = all_data[-1]['draw_no'] if all_data else 0
print(f"마지막 회차: {last_draw_no}")

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
