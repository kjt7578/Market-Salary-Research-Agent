# parser.py
import json
import re
from datetime import datetime
from typing import Dict, Any
from config import TRUSTED_SOURCES

def parse_and_flatten_perplexity_response(response: str, query) -> dict:
    def get_source_info(source_summary, key, url_map):
        ctx = 'N/A'
        url = 'N/A'
        if key in source_summary:
            info = source_summary[key]
            if isinstance(info, dict):
                ctx = info.get('summary', 'N/A')
            elif isinstance(info, str):
                ctx = info
        # url_map에서 해당 소스명에 맞는 url 추출
        for u in url_map:
            if key.lower().replace('.', '').replace(' ', '') in u.lower().replace('.', '').replace(' ', ''):
                url = url_map[u]
                break
        return url, ctx

    def round_salary(val):
        try:
            if val is None or val == 'N/A':
                return 'N/A'
            v = int(float(val))
            return int(v // 1000 * 1000)
        except Exception:
            return 'N/A'

    def extract_salary_numbers(text):
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
                # sources_used: context가 N/A가 아닌 소스만
                sources_used = []
                for name in TRUSTED_SOURCES:
                    if name.lower() in content.lower():
                        sources_used.append(name)
                salary_range = f"{round_salary(minv)} - {round_salary(maxv)}" if minv != 'N/A' and maxv != 'N/A' else 'N/A'
                return {
                    'role': getattr(query, 'role', ''),
                    'level': getattr(query, 'experience_level', ''),
                    'location': getattr(query, 'location', ''),
                    'sources_used': ', '.join(sources_used) if sources_used else 'N/A',
                    'salary_range': salary_range,
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
        # citations/search_results에서 url map 생성
        url_map = {}
        if 'citations' in data:
            for u in data['citations']:
                url_map[u] = u
        if 'search_results' in data:
            for s in data['search_results']:
                url_map[s.get('title', '')] = s.get('url', '')
        source_summary = content_data.get('source_summary', {})
        percentile_25 = content_data.get('percentile_25')
        percentile_75 = content_data.get('percentile_75')
        # 각 소스별 URL/컨텍스트
        zip_url, zip_ctx = get_source_info(source_summary, 'ZipRecruiter', url_map)
        sal_url, sal_ctx = get_source_info(source_summary, 'Salary.com', url_map)
        ind_url, ind_ctx = get_source_info(source_summary, 'Indeed', url_map)
        lev_url, lev_ctx = get_source_info(source_summary, 'Levels.fyi', url_map)
        # sources_used: context가 N/A가 아닌 소스만
        sources_used = []
        for name, ctx in zip([
            'ZipRecruiter', 'Salary.com', 'Indeed', 'Levels.fyi'
        ], [zip_ctx, sal_ctx, ind_ctx, lev_ctx]):
            if ctx != 'N/A':
                sources_used.append(name)
        # salary_range: min/max가 있으면 자동 생성
        minv = round_salary(content_data.get('min'))
        maxv = round_salary(content_data.get('max'))
        salary_range = f"{minv} - {maxv}" if minv != 'N/A' and maxv != 'N/A' else 'N/A'
        updated = datetime.now().strftime('%Y-%m-%d')
        summary = content_data.get('text_summary', str(content_data))
        print(f"[DEBUG] Perplexity content 원문: {summary}")
        return {
            'role': getattr(query, 'role', ''),
            'level': getattr(query, 'experience_level', ''),
            'location': getattr(query, 'location', ''),
            'sources_used': ', '.join(sources_used) if sources_used else 'N/A',
            'salary_range': salary_range,
            'min': minv,
            'max': maxv,
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