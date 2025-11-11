"""
통계 계산 로직
TDD GREEN 단계: 테스트를 통과하는 구현
"""
import sqlite3
from pathlib import Path
from typing import Dict, Optional
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class StatsCalculator:
    """연락처 통계 계산 클래스"""

    def __init__(self, db_path: Path):
        """
        StatsCalculator 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        logger.info(f"StatsCalculator 초기화: {db_path}")

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def calculate_stats(self, contact_id: str) -> Dict:
        """
        특정 연락처의 통계 계산

        Args:
            contact_id: 연락처 ID

        Returns:
            통계 딕셔너리
            - contact_count: 총 연락 횟수
            - last_contact: 최근 연락 날짜 (date 객체 또는 None)
            - last_6month_contacts: 최근 6개월 연락 횟수
        """
        cursor = self.conn.cursor()

        # 총 연락 횟수
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM interactions
            WHERE contact_id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        contact_count = row['count']

        # 최근 연락 날짜
        cursor.execute("""
            SELECT MAX(date) as last_date
            FROM interactions
            WHERE contact_id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        last_contact_str = row['last_date']

        # ISO 형식 문자열을 date 객체로 변환
        last_contact = None
        if last_contact_str:
            try:
                last_contact = date.fromisoformat(last_contact_str)
            except ValueError:
                logger.warning(f"날짜 변환 실패: {last_contact_str}")

        # 최근 6개월 연락 횟수
        six_months_ago = date.today() - timedelta(days=180)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM interactions
            WHERE contact_id = ? AND date >= ?
        """, (contact_id, six_months_ago))
        row = cursor.fetchone()
        last_6month_contacts = row['count']

        return {
            'contact_count': contact_count,
            'last_contact': last_contact,
            'last_6month_contacts': last_6month_contacts
        }

    def calculate_all_stats(self) -> Dict[str, Dict]:
        """
        모든 연락처의 통계 계산

        Returns:
            연락처 ID를 키로 하는 통계 딕셔너리
        """
        cursor = self.conn.cursor()

        # 모든 연락처 조회
        cursor.execute("SELECT contact_id FROM contacts")
        contacts = cursor.fetchall()

        all_stats = {}
        for row in contacts:
            contact_id = row['contact_id']
            all_stats[contact_id] = self.calculate_stats(contact_id)

        logger.info(f"전체 통계 계산 완료: {len(all_stats)}개 연락처")
        return all_stats

    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("StatsCalculator 연결 종료")
