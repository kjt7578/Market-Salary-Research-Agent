# perplexity_api.py
import json
import os
from datetime import datetime
from typing import Dict, Any
from config import TRUSTED_SOURCES, PROMPT_TEMPLATE
from models import SalaryQuery

import requests
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api.perplexity.ai/chat/completions"  # 공식 문서 기준 최신 엔드포인트

# 실제 API 호출 함수

def call_perplexity_api(prompt: str, model: str = "sonar") -> str:
    """
    Perplexity API에 프롬프트를 보내고 응답을 반환한다.
    공식 문서: https://docs.perplexity.ai/getting-started/quickstart#heres-an-example-response-raw-response-at-the-end
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY 환경변수가 설정되어 있지 않습니다.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.2
    }
    print(f"[DEBUG] Perplexity API 요청: {API_URL}")
    print(f"[DEBUG] payload: {json.dumps(payload, ensure_ascii=False)}")
    response = requests.post(API_URL, headers=headers, json=payload)
    print(f"[DEBUG] status: {response.status_code}, response: {response.text[:300]}")
    if response.status_code == 200:
        return response.text
    else:
        raise RuntimeError(f"Perplexity API 호출 실패: {response.status_code} {response.text}")

# mock 함수 (API Key 없이 개발/테스트용)
def mock_perplexity_api(prompt: str) -> str:
    """
    Perplexity API 응답을 흉내내는 mock 함수 (JSON 포맷)
    """
    return json.dumps({
        "salary_range": "XXXX",
        "min": "XXXX",
        "max": "XXXX",
        "median": "XXXX",
        "average": "XXXX",
        "percentile_75": "XXXX",
        "total_compensation": "XXXX",
        "source_summary": {
            "ZipRecruiter": "XXXX",
            "Salary.com": "XXXX",
            "Indeed": "XXXX",
            "Levels.fyi": "XXXX"
        },
        "text_summary": "XXXX"
    })

def build_prompt(query: 'SalaryQuery') -> str:
    sources = ", ".join(TRUSTED_SOURCES)
    base = f"I want to know the average salary for a {query.role} with {query.experience_level} in {query.location}"
    if getattr(query, 'query', None):
        base += f" (with the following context: {query.query})"
    base += (
        f". Please answer ONLY based on the following sources: {sources}. "
        "Respond strictly in the following JSON format: {{\n"
        "  \"salary_range\": \"min - max\",\n"
        "  \"min\": int,\n"
        "  \"max\": int,\n"
        "  \"median\": int,\n"
        "  \"average\": int,\n"
        "  \"percentile_75\": int,\n"
        "  \"total_compensation\": int,\n"
        "  \"source_summary\": {{\"ZipRecruiter\": \"...\", ...}},\n"
        "  \"text_summary\": \"...\"\n"
        "}}\n"
        "If you cannot find a value, set it to null."
    )
    return base 