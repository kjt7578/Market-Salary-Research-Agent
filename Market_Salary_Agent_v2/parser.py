# parser.py
import json
from datetime import datetime
from typing import Dict, Any
from config import TRUSTED_SOURCES

def parse_and_flatten_perplexity_response(response: str, query) -> dict:
    def get_source_info(source_summary, key):
        if key in source_summary:
            info = source_summary[key]
            if isinstance(info, dict):
                return info.get('url', 'N/A'), info.get('summary', 'N/A')
            elif isinstance(info, str):
                return 'N/A', info
        return 'N/A', 'N/A'

    def round_salary(val):
        try:
            if val is None or val == 'N/A':
                return 'N/A'
            v = int(float(val))
            return int(v // 1000 * 1000)
        except Exception:
            return 'N/A'

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
        source_summary = content_data.get('source_summary', {})
        percentile_25 = content_data.get('percentile_25')
        percentile_75 = content_data.get('percentile_75')
        # 각 소스별 URL/컨텍스트
        zip_url, zip_ctx = get_source_info(source_summary, 'ZipRecruiter')
        sal_url, sal_ctx = get_source_info(source_summary, 'Salary.com')
        ind_url, ind_ctx = get_source_info(source_summary, 'Indeed')
        lev_url, lev_ctx = get_source_info(source_summary, 'Levels.fyi')
        # 실제 사용된 소스만 sources_used에 포함
        sources_used = []
        for name, url in zip([
            'ZipRecruiter', 'Salary.com', 'Indeed', 'Levels.fyi'
        ], [zip_url, sal_url, ind_url, lev_url]):
            if url != 'N/A':
                sources_used.append(name)
        # updated date (YYYY-MM-DD)
        updated = datetime.now().strftime('%Y-%m-%d')
        summary = content_data.get('text_summary', str(content_data))
        return {
            'role': getattr(query, 'role', ''),
            'level': getattr(query, 'experience_level', ''),
            'location': getattr(query, 'location', ''),
            'sources_used': ', '.join(sources_used) if sources_used else 'N/A',
            'salary_range': round_salary(content_data.get('salary_range')),
            'min': round_salary(content_data.get('min')),
            'max': round_salary(content_data.get('max')),
            'average': round_salary(content_data.get('average')),
            'percentile_25': round_salary(percentile_25) if percentile_25 is not None else 'N/A',
            'percentile_75': round_salary(percentile_75) if percentile_75 is not None else 'N/A',
            'ZipRecruiter URL': zip_url,
            'ZipRecruiter context': zip_ctx,
            'Salary.com URL': sal_url,
            'Salary.com context': sal_ctx,
            'Indeed URL': ind_url,
            'Indeed context': ind_ctx,
            'Levels.fyi URL': lev_url,
            'Levels.fyi context': lev_ctx,
            'summary': summary,
            'updated_date': updated
        }
    except Exception as e:
        return {
            'role': getattr(query, 'role', ''),
            'level': getattr(query, 'experience_level', ''),
            'location': getattr(query, 'location', ''),
            'sources_used': 'N/A',
            'salary_range': 'N/A',
            'min': 'N/A',
            'max': 'N/A',
            'average': 'N/A',
            'percentile_25': 'N/A',
            'percentile_75': 'N/A',
            'ZipRecruiter URL': 'N/A',
            'ZipRecruiter context': 'N/A',
            'Salary.com URL': 'N/A',
            'Salary.com context': 'N/A',
            'Indeed URL': 'N/A',
            'Indeed context': 'N/A',
            'Levels.fyi URL': 'N/A',
            'Levels.fyi context': 'N/A',
            'summary': f'[파싱실패] {str(e)}',
            'updated_date': datetime.now().strftime('%Y-%m-%d')
        } 