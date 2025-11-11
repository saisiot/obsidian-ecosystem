import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.repomix_store import RepomixIndexStore


@pytest.fixture
def temp_index_file():
    """임시 인덱스 파일 생성"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)
    yield temp_path
    # 테스트 후 파일 삭제
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_content():
    """테스트용 샘플 컨텐츠"""
    return """# AI Strategy 2025

This is a comprehensive strategy document for implementing AI initiatives.

## Key Points
- Machine learning adoption
- Data infrastructure
- Ethical AI framework

Tags: #ai #strategy #2025

References:
- [[Project A]]
- [[Roadmap 2025]]
- [[Tech Stack]]
"""


@pytest.fixture
def sample_doc():
    """테스트용 샘플 문서"""
    return {
        "path": "/vault/00 Notes/Work/AI Strategy 2025.md",
        "title": "AI Strategy 2025",
        "content": """# AI Strategy 2025

This is a comprehensive strategy document for implementing AI initiatives.

## Key Points
- Machine learning adoption
- Data infrastructure
- Ethical AI framework

Tags: #ai #strategy #2025

References:
- [[Project A]]
- [[Roadmap 2025]]
- [[Tech Stack]]
""",
        "metadata": {"tags": ["ai", "strategy"]},
        "tags": ["ai", "strategy", "2025"],
        "wiki_links": ["Project A", "Roadmap 2025", "Tech Stack"],
        "backlinks": ["Project A", "Roadmap 2025"],
        "para_folder": "00 Notes",
    }


def test_init_creates_empty_index(temp_index_file):
    """초기화 시 빈 인덱스 생성 테스트"""
    store = RepomixIndexStore(temp_index_file)
    assert store.index["version"] == "1.0.0"
    assert store.index["files"] == {}
    assert store.index["stats"]["total_files"] == 0


def test_calculate_stats(temp_index_file, sample_content):
    """파일 통계 계산 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write(sample_content)
        temp_file = Path(f.name)

    try:
        stats = store.calculate_stats(sample_content, temp_file)

        # 기본 통계 검증
        assert stats["words"] > 0
        assert stats["characters"] > 0
        assert stats["lines"] > 0
        assert stats["estimated_tokens"] > 0

        # 단어 수 검증 (대략적인 범위)
        assert 30 < stats["words"] < 50

        # 토큰 수가 단어 수보다 많아야 함 (영어 기준)
        assert stats["estimated_tokens"] >= stats["words"]

        print("\n📊 통계 계산 결과:")
        print(f"  - 단어: {stats['words']}")
        print(f"  - 문자: {stats['characters']}")
        print(f"  - 줄: {stats['lines']}")
        print(f"  - 토큰: {stats['estimated_tokens']}")
        print(f"  - 토큰/단어 비율: {stats['estimated_tokens']/stats['words']:.2f}")

    finally:
        temp_file.unlink()


def test_update_and_save_index(temp_index_file, sample_doc):
    """인덱스 업데이트 및 저장 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write(sample_doc["content"])
        temp_file = Path(f.name)

    try:
        # 인덱스 업데이트
        store.update_index(sample_doc, temp_file)

        # 파일 정보 확인
        path_str = str(temp_file)
        assert path_str in store.index["files"]

        file_info = store.index["files"][path_str]
        assert file_info["title"] == "AI Strategy 2025"
        assert file_info["para_folder"] == "00 Notes"
        assert "timestamps" in file_info
        assert "size" in file_info
        assert file_info["metadata"]["tags"] == ["ai", "strategy", "2025"]

        # 저장 테스트
        store.save_index()
        assert temp_index_file.exists()

        # 저장된 파일 로드하여 검증
        with open(temp_index_file, "r", encoding="utf-8") as f:
            saved_index = json.load(f)
            assert saved_index["stats"]["total_files"] == 1
            assert saved_index["stats"]["total_words"] > 0

    finally:
        temp_file.unlink()


def test_delete_index(temp_index_file, sample_doc):
    """인덱스 삭제 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 임시 파일 생성 및 인덱스 추가
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write(sample_doc["content"])
        temp_file = Path(f.name)

    try:
        path_str = str(temp_file)
        store.update_index(sample_doc, temp_file)
        assert path_str in store.index["files"]

        # 삭제
        store.delete_index(path_str)
        assert path_str not in store.index["files"]

    finally:
        temp_file.unlink()


def test_query_by_timeframe(temp_index_file):
    """시간 범위 쿼리 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 최근 파일과 오래된 파일 추가
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write("Recent note")
        recent_file = Path(f.name)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write("Old note")
        old_file = Path(f.name)

    try:
        # 최근 파일 추가
        recent_doc = {
            "title": "Recent Note",
            "content": "Recent note",
            "para_folder": "00 Notes",
            "tags": [],
            "wiki_links": [],
            "backlinks": [],
        }
        store.update_index(recent_doc, recent_file)

        # 오래된 파일 추가 (타임스탬프 조작)
        old_doc = {
            "title": "Old Note",
            "content": "Old note",
            "para_folder": "00 Notes",
            "tags": [],
            "wiki_links": [],
            "backlinks": [],
        }
        store.update_index(old_doc, old_file)

        # 오래된 파일의 타임스탬프를 30일 전으로 설정
        old_timestamp = (datetime.now() - timedelta(days=30)).isoformat()
        store.index["files"][str(old_file)]["timestamps"]["modified"] = old_timestamp

        # 최근 7일 이내 파일 쿼리
        results = store.query_by_timeframe(days=7)
        assert len(results) == 1
        assert results[0]["title"] == "Recent Note"

        # 최근 60일 이내 파일 쿼리
        results = store.query_by_timeframe(days=60)
        assert len(results) == 2

    finally:
        recent_file.unlink()
        old_file.unlink()


def test_query_by_tag(temp_index_file, sample_doc):
    """태그 쿼리 테스트"""
    store = RepomixIndexStore(temp_index_file)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write(sample_doc["content"])
        temp_file = Path(f.name)

    try:
        store.update_index(sample_doc, temp_file)

        # 'ai' 태그로 검색
        results = store.query_by_tag("ai")
        assert len(results) == 1
        assert results[0]["title"] == "AI Strategy 2025"

        # 없는 태그로 검색
        results = store.query_by_tag("nonexistent")
        assert len(results) == 0

    finally:
        temp_file.unlink()


def test_get_by_title(temp_index_file, sample_doc):
    """제목으로 검색 테스트"""
    store = RepomixIndexStore(temp_index_file)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".md", encoding="utf-8"
    ) as f:
        f.write(sample_doc["content"])
        temp_file = Path(f.name)

    try:
        store.update_index(sample_doc, temp_file)

        # 제목으로 검색
        result = store.get_by_title("AI Strategy 2025")
        assert result is not None
        assert result["title"] == "AI Strategy 2025"

        # 없는 제목으로 검색
        result = store.get_by_title("Nonexistent Note")
        assert result is None

    finally:
        temp_file.unlink()


def test_get_folder_stats(temp_index_file):
    """폴더 통계 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 여러 폴더의 파일 추가
    docs = [
        {
            "title": "Note 1",
            "content": "Content " * 100,
            "para_folder": "00 Notes",
            "tags": [],
            "wiki_links": [],
            "backlinks": [],
        },
        {
            "title": "Note 2",
            "content": "Content " * 200,
            "para_folder": "00 Notes",
            "tags": [],
            "wiki_links": [],
            "backlinks": [],
        },
        {
            "title": "Ref 1",
            "content": "Content " * 50,
            "para_folder": "01 Reference",
            "tags": [],
            "wiki_links": [],
            "backlinks": [],
        },
    ]

    temp_files = []
    try:
        for doc in docs:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".md", encoding="utf-8"
            ) as f:
                f.write(doc["content"])
                temp_file = Path(f.name)
                temp_files.append(temp_file)
                store.update_index(doc, temp_file)

        # 폴더 통계 확인
        folder_stats = store.get_folder_stats()
        assert "00 Notes" in folder_stats
        assert "01 Reference" in folder_stats

        assert folder_stats["00 Notes"]["files"] == 2
        assert folder_stats["01 Reference"]["files"] == 1

        assert folder_stats["00 Notes"]["words"] > folder_stats["01 Reference"]["words"]

    finally:
        for f in temp_files:
            f.unlink()


def test_get_tag_stats(temp_index_file):
    """태그 통계 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 여러 태그를 가진 파일들 추가
    docs = [
        {
            "title": "Note 1",
            "content": "Content",
            "para_folder": "00 Notes",
            "tags": ["ai", "strategy"],
            "wiki_links": [],
            "backlinks": [],
        },
        {
            "title": "Note 2",
            "content": "Content",
            "para_folder": "00 Notes",
            "tags": ["ai", "machine-learning"],
            "wiki_links": [],
            "backlinks": [],
        },
        {
            "title": "Note 3",
            "content": "Content",
            "para_folder": "00 Notes",
            "tags": ["ai"],
            "wiki_links": [],
            "backlinks": [],
        },
    ]

    temp_files = []
    try:
        for doc in docs:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".md", encoding="utf-8"
            ) as f:
                f.write(doc["content"])
                temp_file = Path(f.name)
                temp_files.append(temp_file)
                store.update_index(doc, temp_file)

        # 태그 통계 확인
        tag_stats = store.get_tag_stats()
        assert tag_stats["ai"] == 3
        assert tag_stats["strategy"] == 1
        assert tag_stats["machine-learning"] == 1

        # 빈도순 정렬 확인
        tags_list = list(tag_stats.keys())
        assert tags_list[0] == "ai"  # 가장 많이 사용된 태그

    finally:
        for f in temp_files:
            f.unlink()


def test_token_estimation_accuracy(temp_index_file):
    """토큰 추정 정확도 테스트"""
    store = RepomixIndexStore(temp_index_file)

    # 다양한 길이의 텍스트로 테스트
    test_cases = [
        ("Short text", 2),  # 짧은 텍스트
        ("Medium " * 50, 50),  # 중간 길이
        ("Long text with many words " * 200, 400),  # 긴 텍스트
    ]

    for content, expected_min_tokens in test_cases:
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md", encoding="utf-8"
        ) as f:
            f.write(content)
            temp_file = Path(f.name)

        try:
            stats = store.calculate_stats(content, temp_file)

            # 토큰 수가 단어 수보다 적지 않아야 함
            assert stats["estimated_tokens"] >= stats["words"] * 0.7

            # 예상 최소 토큰 수 확인
            assert stats["estimated_tokens"] >= expected_min_tokens

            print(
                f"\n🔍 '{content[:30]}...': {stats['words']}단어 → {stats['estimated_tokens']}토큰"
            )

        finally:
            temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
