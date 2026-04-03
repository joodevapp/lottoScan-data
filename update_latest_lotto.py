import requests
import json
import os

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
