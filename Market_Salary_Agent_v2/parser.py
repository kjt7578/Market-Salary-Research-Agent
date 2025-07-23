# parser.py
import json
from datetime import datetime
from typing import Dict, Any
from config import TRUSTED_SOURCES

def parse_and_flatten_perplexity_response(response: str, query) -> dict:
    """
    Perplexity API 응답을 파싱하여 사용자가 원하는 평탄화된 dict로 반환
    - 각 소스별 요약/URL이 없으면 'N/A'로 채움
    - percentile_25, percentile_75 지원
    - summary는 text_summary, updated date는 retrieved_at
    """
    def get_source_info(source_summary, key):
        if key in source_summary:
            info = source_summary[key]
            if isinstance(info, dict):
                return info.get('summary', 'N/A'), info.get('url', 'N/A')
            elif isinstance(info, str):
                return info, 'N/A'
        return 'N/A', 'N/A'

    try:
        data = json.loads(response)
        content = None
        if isinstance(data, dict) and 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            try:
                content_data = json.loads(content)
            except Exception:
                content_data = {}
        else:
            content_data = data
        # source_summary 파싱
        source_summary = content_data.get('source_summary', {})
        # percentile_25, percentile_75
        percentile_25 = content_data.get('percentile_25')
        percentile_75 = content_data.get('percentile_75')
        # 각 소스별 요약/URL
        zip_summary, zip_url = get_source_info(source_summary, 'ZipRecruiter')
        sal_summary, sal_url = get_source_info(source_summary, 'Salary.com')
        ind_summary, ind_url = get_source_info(source_summary, 'Indeed')
        lev_summary, lev_url = get_source_info(source_summary, 'Levels.fyi')
        # updated date
        updated = datetime.now().isoformat()
        # summary
        summary = content_data.get('text_summary', str(content_data))
        # 평탄화 dict
        return {
            'role': getattr(query, 'role', ''),
            'level': getattr(query, 'experience_level', ''),
            'location': getattr(query, 'location', ''),
            'sources_used': ', '.join(TRUSTED_SOURCES),
            'salary_range': content_data.get('salary_range', 'N/A'),
            'min': content_data.get('min', 'N/A'),
            'max': content_data.get('max', 'N/A'),
            'average': content_data.get('average', 'N/A'),
            'percentile_25': percentile_25 if percentile_25 is not None else 'N/A',
            'percentile_75': percentile_75 if percentile_75 is not None else 'N/A',
            'ZipRecruiter source': f"{zip_summary} | {zip_url}",
            'Salary.com source': f"{sal_summary} | {sal_url}",
            'Indeed source': f"{ind_summary} | {ind_url}",
            'Levels.fyi source': f"{lev_summary} | {lev_url}",
            'summary': summary,
            'updated_date': updated
        }
    except Exception as e:
        return {
            'role': getattr(query, 'role', ''),
            'level': getattr(query, 'experience_level', ''),
            'location': getattr(query, 'location', ''),
            'sources_used': ', '.join(TRUSTED_SOURCES),
            'salary_range': 'N/A',
            'min': 'N/A',
            'max': 'N/A',
            'average': 'N/A',
            'percentile_25': 'N/A',
            'percentile_75': 'N/A',
            'ZipRecruiter source': 'N/A',
            'Salary.com source': 'N/A',
            'Indeed source': 'N/A',
            'Levels.fyi source': 'N/A',
            'summary': f'[파싱실패] {str(e)}',
            'updated_date': datetime.now().isoformat()
        } 