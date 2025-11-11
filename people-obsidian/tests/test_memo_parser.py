"""
메모 파싱 로직 테스트
TDD RED 단계: 먼저 테스트 작성
"""
import pytest
from datetime import date, timedelta
from src.memo_parser import MemoParser


class TestMemoParser:
    """MemoParser 클래스 테스트"""

    def test_parse_yymmdd_format(self):
        """YYMMDD 형식 날짜를 파싱해야 함"""
        parser = MemoParser()
        memo = "250115 점심 미팅"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date(2025, 1, 15)
        assert interactions[0]['content'] == "점심 미팅"

    def test_parse_multiple_entries(self):
        """여러 개의 날짜 엔트리를 파싱해야 함"""
        parser = MemoParser()
        memo = """250115 점심 미팅
250110 전화 통화
241220 연말 인사"""
        interactions = parser.parse(memo)

        assert len(interactions) == 3
        assert interactions[0]['date'] == date(2025, 1, 15)
        assert interactions[0]['content'] == "점심 미팅"
        assert interactions[1]['date'] == date(2025, 1, 10)
        assert interactions[1]['content'] == "전화 통화"
        assert interactions[2]['date'] == date(2024, 12, 20)
        assert interactions[2]['content'] == "연말 인사"

    def test_parse_with_newlines_in_content(self):
        """날짜 없는 줄은 이전 내용에 줄바꿈으로 추가해야 함"""
        parser = MemoParser()
        memo = """251110 생일날만남
같이 카페에가서 커피 한잔하고 선물받음

251101 전화로 연락함"""
        interactions = parser.parse(memo)

        assert len(interactions) == 2
        assert "생일날만남\n같이 카페에가서 커피 한잔하고 선물받음" in interactions[0]['content']
        assert interactions[1]['content'] == "전화로 연락함"

    def test_parse_natural_language_today(self):
        """'오늘' 키워드를 오늘 날짜로 변환해야 함"""
        parser = MemoParser()
        memo = "오늘 커피 미팅"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date.today()
        assert interactions[0]['content'] == "커피 미팅"

    def test_parse_natural_language_yesterday(self):
        """'어제' 키워드를 어제 날짜로 변환해야 함"""
        parser = MemoParser()
        memo = "어제 전화함"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date.today() - timedelta(days=1)
        assert interactions[0]['content'] == "전화함"

    def test_parse_natural_language_today_english(self):
        """'today' 키워드를 오늘 날짜로 변환해야 함"""
        parser = MemoParser()
        memo = "today coffee meeting"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date.today()
        assert interactions[0]['content'] == "coffee meeting"

    def test_parse_natural_language_yesterday_english(self):
        """'yesterday' 키워드를 어제 날짜로 변환해야 함"""
        parser = MemoParser()
        memo = "yesterday phone call"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date.today() - timedelta(days=1)
        assert interactions[0]['content'] == "phone call"

    def test_parse_no_date_returns_empty(self):
        """날짜가 없는 메모는 빈 리스트 반환"""
        parser = MemoParser()
        memo = "그냥 메모"
        interactions = parser.parse(memo)

        assert len(interactions) == 0

    def test_parse_empty_memo(self):
        """빈 메모는 빈 리스트 반환"""
        parser = MemoParser()
        interactions = parser.parse("")

        assert len(interactions) == 0

    def test_parse_none_memo(self):
        """None 메모는 빈 리스트 반환"""
        parser = MemoParser()
        interactions = parser.parse(None)

        assert len(interactions) == 0

    def test_parse_whitespace_only_memo(self):
        """공백만 있는 메모는 빈 리스트 반환"""
        parser = MemoParser()
        interactions = parser.parse("   \n\n  ")

        assert len(interactions) == 0

    def test_parse_mixed_date_formats(self):
        """YYMMDD와 자연어 날짜가 섞여있어도 파싱해야 함"""
        parser = MemoParser()
        memo = """250115 점심 미팅
오늘 저녁 약속
241220 연말 인사"""
        interactions = parser.parse(memo)

        assert len(interactions) == 3
        assert interactions[0]['date'] == date(2025, 1, 15)
        assert interactions[1]['date'] == date.today()
        assert interactions[2]['date'] == date(2024, 12, 20)

    def test_parse_with_complex_content(self):
        """복잡한 내용도 정확히 파싱해야 함"""
        parser = MemoParser()
        memo = """251110 생일날만남
같이 카페에가서 커피 한잔하고 선물받음
정말 즐거운 시간이었음

251101 전화로 연락함. 요즘 많이 바쁜듯.
다음주에 만나기로 함"""
        interactions = parser.parse(memo)

        assert len(interactions) == 2
        assert "생일날만남" in interactions[0]['content']
        assert "선물받음" in interactions[0]['content']
        assert "즐거운" in interactions[0]['content']
        assert "전화로 연락함" in interactions[1]['content']
        assert "다음주에" in interactions[1]['content']

    def test_parse_invalid_date_format(self):
        """잘못된 날짜 형식은 무시해야 함"""
        parser = MemoParser()
        memo = "999999 이건 날짜가 아님"
        interactions = parser.parse(memo)

        # 잘못된 날짜는 파싱하지 않음
        assert len(interactions) == 0

    def test_parse_date_at_year_boundary(self):
        """연도 경계의 날짜도 정확히 파싱해야 함"""
        parser = MemoParser()
        memo = "241231 작년 마지막 날"
        interactions = parser.parse(memo)

        assert len(interactions) == 1
        assert interactions[0]['date'] == date(2024, 12, 31)

    def test_parse_preserves_order(self):
        """파싱 결과는 원본 순서를 유지해야 함"""
        parser = MemoParser()
        memo = """250115 첫번째
250110 두번째
250120 세번째"""
        interactions = parser.parse(memo)

        assert len(interactions) == 3
        assert interactions[0]['content'] == "첫번째"
        assert interactions[1]['content'] == "두번째"
        assert interactions[2]['content'] == "세번째"
