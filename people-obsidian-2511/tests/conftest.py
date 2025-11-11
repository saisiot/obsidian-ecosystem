"""
pytest 설정 및 공통 픽스처
"""
import pytest
import json
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_contacts():
    """샘플 연락처 데이터"""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_contacts.json"
    with open(fixture_path, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def temp_vault(tmp_path):
    """임시 Obsidian vault 디렉토리"""
    people_folder = tmp_path / "07 people"
    people_folder.mkdir(parents=True)
    return people_folder


@pytest.fixture
def temp_db(tmp_path):
    """임시 SQLite 데이터베이스 경로"""
    return tmp_path / ".contacts.db"


@pytest.fixture
def sample_memo_simple():
    """간단한 샘플 메모"""
    return "250115 점심 미팅"


@pytest.fixture
def sample_memo_multiline():
    """여러 줄이 있는 샘플 메모"""
    return """250115 점심 미팅. 새 프로젝트 논의
250110 전화 통화
241220 연말 인사"""


@pytest.fixture
def sample_memo_with_content_newlines():
    """내용에 줄바꿈이 포함된 샘플 메모"""
    return """251110 생일날만남
같이 카페에가서 커피 한잔하고 선물받음

251101 전화로 연락함. 요즘 많이 바쁜듯."""


@pytest.fixture
def sample_memo_natural_language():
    """자연어 날짜가 포함된 샘플 메모"""
    return """오늘 커피 미팅
어제 전화함"""


@pytest.fixture
def sample_contact_dict():
    """단일 연락처 딕셔너리"""
    return {
        'contact_id': 'ABC-123-DEF-456-789',
        'name': '홍길동',
        'phone': '010-1234-5678',
        'email': 'hong@example.com'
    }


@pytest.fixture
def sample_interactions():
    """샘플 interaction 리스트"""
    from datetime import date
    return [
        {'date': date(2025, 1, 15), 'content': '점심 미팅'},
        {'date': date(2025, 1, 10), 'content': '전화 통화'},
        {'date': date(2024, 12, 20), 'content': '연말 인사'}
    ]


@pytest.fixture
def sample_stats():
    """샘플 통계 데이터"""
    from datetime import date
    return {
        'last_contact': date(2025, 1, 15),
        'contact_count': 3,
        'last_6month_contacts': 2
    }
