# main.py
from dotenv import load_dotenv
load_dotenv()
import os
import sys
import json
from datetime import datetime, timezone
from models import SalaryQuery
from perplexity_api import build_prompt, call_perplexity_api, mock_perplexity_api
from parser import parse_and_flatten_perplexity_response

def main():
    print("=== Market Salary Agent v2 (Perplexity API 기반, CLI MVP) ===")
    role = input("직무명 (예: Software Engineer): ").strip()
    experience_level = input("경력/레벨 (예: 0-3 years, Entry): ").strip()
    location = input("지역 (예: New Jersey): ").strip()

    query = SalaryQuery(role=role, experience_level=experience_level, location=location)
    prompt = build_prompt(query)
    print("\n[DEBUG] Perplexity 프롬프트:")
    print(prompt)

    # 실제 API 호출 시도, 실패 시 mock 사용
    try:
        response = call_perplexity_api(prompt, model="sonar")
        print("[INFO] 실제 Perplexity API 호출 결과를 사용합니다.")
    except Exception as e:
        print(f"[WARN] Perplexity API 호출 실패: {e}\n[INFO] mock 응답을 사용합니다.")
        response = mock_perplexity_api(prompt)

    # 평탄화 파싱
    flat_result = parse_and_flatten_perplexity_response(response, query)

    # 결과 저장
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fname = f"data/{role.replace(' ', '_')}_{location.replace(' ', '_')}_{now}.json"
    os.makedirs("data", exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(flat_result, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] 결과가 {fname}에 저장되었습니다.")

    # 콘솔 출력
    print("\n[RESULT] 파싱된 연봉 정보:")
    for k, v in flat_result.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main() 