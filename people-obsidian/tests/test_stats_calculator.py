"""
통계 계산 로직 테스트
TDD RED 단계: 먼저 테스트 작성
"""
import pytest
from pathlib import Path
from datetime import date, timedelta
from src.stats_calculator import StatsCalculator


class TestStatsCalculator:
    """StatsCalculator 클래스 테스트"""

    def test_calculate_stats_basic(self, temp_db):
        """기본 통계 계산 테스트"""
        from src.db_manager import DatabaseManager

        with DatabaseManager(temp_db) as db:
            db.create_tables()

            # 연락처 추가
            contact = {
                'contact_id': 'ABC-123',
                'name': '홍길동'
            }
            db.insert_contact(contact)

            # Interaction 추가
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': date(2025, 1, 15),
                'content': '점심 미팅'
            })
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': date(2025, 1, 10),
                'content': '전화 통화'
            })

        # 통계 계산
        calculator = StatsCalculator(temp_db)
        stats = calculator.calculate_stats('ABC-123')

        assert stats['contact_count'] == 2
        assert stats['last_contact'] == date(2025, 1, 15)

    def test_calculate_stats_recent_6months(self, temp_db):
        """최근 6개월 연락 횟수 계산"""
        from src.db_manager import DatabaseManager

        today = date.today()
        six_months_ago = today - timedelta(days=180)
        seven_months_ago = today - timedelta(days=210)

        with DatabaseManager(temp_db) as db:
            db.create_tables()

            contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
            db.insert_contact(contact)

            # 최근 6개월 이내 (2개)
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': today - timedelta(days=30),
                'content': '1개월 전'
            })
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': today - timedelta(days=150),
                'content': '5개월 전'
            })

            # 6개월 이전 (1개)
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': seven_months_ago,
                'content': '7개월 전'
            })

        calculator = StatsCalculator(temp_db)
        stats = calculator.calculate_stats('ABC-123')

        assert stats['contact_count'] == 3
        assert stats['last_6month_contacts'] == 2

    def test_calculate_stats_no_interactions(self, temp_db):
        """Interaction이 없는 경우"""
        from src.db_manager import DatabaseManager

        with DatabaseManager(temp_db) as db:
            db.create_tables()

            contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
            db.insert_contact(contact)

        calculator = StatsCalculator(temp_db)
        stats = calculator.calculate_stats('ABC-123')

        assert stats['contact_count'] == 0
        assert stats['last_contact'] is None
        assert stats['last_6month_contacts'] == 0

    def test_calculate_stats_nonexistent_contact(self, temp_db):
        """존재하지 않는 연락처"""
        from src.db_manager import DatabaseManager

        with DatabaseManager(temp_db) as db:
            db.create_tables()

        calculator = StatsCalculator(temp_db)
        stats = calculator.calculate_stats('NONEXISTENT')

        assert stats['contact_count'] == 0
        assert stats['last_contact'] is None
        assert stats['last_6month_contacts'] == 0

    def test_calculate_all_contacts_stats(self, temp_db):
        """모든 연락처의 통계 계산"""
        from src.db_manager import DatabaseManager

        with DatabaseManager(temp_db) as db:
            db.create_tables()

            # 연락처 2개
            db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})
            db.insert_contact({'contact_id': 'DEF-456', 'name': '김철수'})

            # 홍길동 interactions
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': date(2025, 1, 15),
                'content': '점심'
            })

            # 김철수 interactions
            db.insert_interaction({
                'contact_id': 'DEF-456',
                'date': date(2025, 1, 10),
                'content': '전화'
            })
            db.insert_interaction({
                'contact_id': 'DEF-456',
                'date': date(2025, 1, 5),
                'content': '미팅'
            })

        calculator = StatsCalculator(temp_db)
        all_stats = calculator.calculate_all_stats()

        assert len(all_stats) == 2
        assert all_stats['ABC-123']['contact_count'] == 1
        assert all_stats['DEF-456']['contact_count'] == 2

    def test_calculate_stats_edge_case_exactly_6months(self, temp_db):
        """정확히 6개월 경계선 테스트"""
        from src.db_manager import DatabaseManager

        today = date.today()
        exactly_6months_ago = today - timedelta(days=180)

        with DatabaseManager(temp_db) as db:
            db.create_tables()

            contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
            db.insert_contact(contact)

            # 정확히 180일 전
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': exactly_6months_ago,
                'content': '정확히 6개월 전'
            })

        calculator = StatsCalculator(temp_db)
        stats = calculator.calculate_stats('ABC-123')

        # 180일 전도 포함되어야 함 (>= 조건)
        assert stats['last_6month_contacts'] == 1

    def test_context_manager_support(self, temp_db):
        """Context manager 지원 테스트"""
        from src.db_manager import DatabaseManager

        with DatabaseManager(temp_db) as db:
            db.create_tables()
            db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        with StatsCalculator(temp_db) as calculator:
            stats = calculator.calculate_stats('ABC-123')
            assert stats['contact_count'] == 0
