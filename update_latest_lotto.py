import requests
import json
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import binascii

def encrypt_password(modulus_hex, exponent_hex, password):
    modulus = int(modulus_hex, 16)
    exponent = int(exponent_hex, 16)
    key = RSA.construct((modulus, exponent))
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(password.encode('utf-8'))
    return binascii.hexlify(encrypted).decode('utf-8')

def login_dhlottery(user_id, user_pw):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 메인 페이지에서 RSA 키 가져오기
    main_page = session.get("https://www.dhlottery.co.kr/common.do?method=main", headers=headers)
    modulus = main_page.text.split("var rsaModulus = '")[1].split("'")[0]
    exponent = "10001"
    print(f"RSA 모듈러스 획득: {modulus[:20]}...")
    
    # 비밀번호 암호화
    encrypted_pw = encrypt_password(modulus, exponent, user_pw)
    print("비밀번호 암호화 완료")
    
    # 로그인
    login_data = {
        'returnUrl': '',
        'userId': user_id,
        'password': encrypted_pw,
        'newsEventYn': '',
        'ssoYn': 'Y',
    }
    
    res = session.post(
        "https://www.dhlottery.co.kr/userSsl.do?method=login",
        data=login_data,
        headers={
            **headers,
            'Referer': 'https://www.dhlottery.co.kr/user.do?method=login',
        }
    )
    print(f"로그인 상태코드: {res.status_code}")
    
    # 로그인 확인
    check = session.get("https://www.dhlottery.co.kr/common.do?method=main", headers=headers)
    if 'j_popup_logout' in check.text:
        print("로그인 성공 확인!")
    else:
        print("로그인 실패 - 세션 없음")
    
    return session

def get_lotto_number(session, draw_no):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    try:
        res = session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.dhlottery.co.kr/gameResult.do?method=byWin',
        })
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
        print(f"Error: {e}")
    return None

# 환경변수에서 아이디/비밀번호 가져오기
user_id = os.environ.get('LOTTO_ID')
user_pw = os.environ.get('LOTTO_PW')
print(f"로그인 시도: {user_id}")

# 로그인
session = login_dhlottery(user_id, user_pw)

# all.json 불러오기
all_json_path = "results/all.json"
if os.path.exists(all_json_path):
    with open(all_json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = []

# 마지막 회차 확인
last_draw_no = all_data[-1]['draw_no'] if all_data else 0
print(f"마지막 회차: {last_draw_no}")

# 새 데이터 가져오기
new_data = []
draw_no = last_draw_no + 1
while True:
    result = get_lotto_number(session, draw_no)
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
