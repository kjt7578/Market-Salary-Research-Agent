# models.py
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SalaryQuery:
    role: str
    experience_level: str
    location: str
    query: Optional[str] = None

@dataclass
class SalaryResult:
    role: str
    experience_level: str
    location: str
    query: str
    sources_used: List[str]
    salary_range: Optional[str]
    min: Optional[int]
    max: Optional[int]
    median: Optional[int]
    average: Optional[int]
    percentile_75: Optional[int]
    total_compensation: Optional[int]
    source_summary: Dict[str, str]
    text_summary: str
    retrieved_at: str  # ISO8601 