# parser.py
import json
import re
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

    def extract_salary_numbers(text):
        # $82,000, 82000, 82k 등 다양한 패턴 지원
        numbers = re.findall(r'\$?([0-9]{2,3}[,0-9]{0,3})(?:k)?', text.replace(',', ''))
        nums = [int(n) for n in numbers if n.isdigit()]
        if nums:
            nums = sorted(nums)
            return nums[0], nums[-1], sum(nums)//len(nums) if len(nums) > 0 else 'N/A'
        return 'N/A', 'N/A', 'N/A'

    def extract_urls(text):
        return re.findall(r'https?://\S+', text)

    try:
        data = json.loads(response)
        content = None
        if isinstance(data, dict) and 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            print(f"[DEBUG] Perplexity content 원문: {content}")
            try:
                content_data = json.loads(content)
            except Exception:
                # fallback: 자연어에서 최대한 추출
                minv, maxv, avgv = extract_salary_numbers(content)
                urls = extract_urls(content)
                updated = datetime.now().strftime('%Y-%m-%d')
                return {
                    'role': getattr(query, 'role', ''),
                    'level': getattr(query, 'experience_level', ''),
                    'location': getattr(query, 'location', ''),
                    'sources_used': ', '.join([u for u in TRUSTED_SOURCES if any(u.lower() in url.lower() for url in urls)]) if urls else 'N/A',
                    'salary_range': f"{minv} - {maxv}" if minv != 'N/A' and maxv != 'N/A' else 'N/A',
                    'min': round_salary(minv),
                    'max': round_salary(maxv),
                    'average': round_salary(avgv),
                    'percentile_25': 'N/A',
                    'percentile_75': 'N/A',
                    'ZipRecruiter URL': next((u for u in urls if 'ziprecruiter' in u), 'N/A'),
                    'ZipRecruiter context': 'N/A',
                    'Salary.com URL': next((u for u in urls if 'salary.com' in u), 'N/A'),
                    'Salary.com context': 'N/A',
                    'Indeed URL': next((u for u in urls if 'indeed' in u), 'N/A'),
                    'Indeed context': 'N/A',
                    'Levels.fyi URL': next((u for u in urls if 'levels.fyi' in u), 'N/A'),
                    'Levels.fyi context': 'N/A',
                    'summary': content,
                    'updated_date': updated
                }
        else:
            content_data = data
        source_summary = content_data.get('source_summary', {})
        percentile_25 = content_data.get('percentile_25')
        percentile_75 = content_data.get('percentile_75')
        zip_url, zip_ctx = get_source_info(source_summary, 'ZipRecruiter')
        sal_url, sal_ctx = get_source_info(source_summary, 'Salary.com')
        ind_url, ind_ctx = get_source_info(source_summary, 'Indeed')
        lev_url, lev_ctx = get_source_info(source_summary, 'Levels.fyi')
        sources_used = []
        for name, url in zip([
            'ZipRecruiter', 'Salary.com', 'Indeed', 'Levels.fyi'
        ], [zip_url, sal_url, ind_url, lev_url]):
            if url != 'N/A':
                sources_used.append(name)
        updated = datetime.now().strftime('%Y-%m-%d')
        summary = content_data.get('text_summary', str(content_data))
        print(f"[DEBUG] Perplexity content 원문: {summary}")
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