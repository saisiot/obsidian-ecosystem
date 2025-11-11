"""
SQLite 데이터베이스 관리
TDD GREEN 단계: 테스트를 통과하는 구현
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""

    def __init__(self, db_path: Path):
        """
        DatabaseManager 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row  # Row 객체로 반환

        # FOREIGN KEY 제약 조건 활성화 (CASCADE 삭제를 위해 필요)
        self.conn.execute("PRAGMA foreign_keys = ON")

        logger.info(f"데이터베이스 연결: {db_path}")

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def create_tables(self):
        """테이블 생성"""
        cursor = self.conn.cursor()

        # contacts 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                contact_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                first_met DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # interactions 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id TEXT NOT NULL,
                date DATE NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts(contact_id) ON DELETE CASCADE,
                UNIQUE(contact_id, date)
            )
        """)

        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_contact
            ON interactions(contact_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_date
            ON interactions(date)
        """)

        self.conn.commit()
        logger.info("테이블 생성 완료")

    def insert_contact(self, contact: Dict):
        """
        연락처 삽입 (REPLACE로 업데이트도 처리)

        Args:
            contact: 연락처 정보 딕셔너리
                - contact_id (필수)
                - name (필수)
                - phone (선택)
                - email (선택)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO contacts (contact_id, name, phone, email)
            VALUES (?, ?, ?, ?)
        """, (
            contact['contact_id'],
            contact['name'],
            contact.get('phone'),
            contact.get('email')
        ))
        self.conn.commit()
        logger.debug(f"연락처 저장: {contact['name']}")

    def update_contact(self, contact: Dict):
        """
        연락처 업데이트

        Args:
            contact: 연락처 정보 딕셔너리
        """
        self.insert_contact(contact)  # REPLACE 사용

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """
        연락처 조회

        Args:
            contact_id: 연락처 ID

        Returns:
            연락처 정보 딕셔너리 또는 None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts WHERE contact_id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_contacts(self) -> List[Dict]:
        """
        모든 연락처 조회

        Returns:
            연락처 정보 딕셔너리 리스트
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def delete_contact(self, contact_id: str):
        """
        연락처 삭제 (CASCADE로 interactions도 삭제)

        Args:
            contact_id: 연락처 ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM contacts WHERE contact_id = ?
        """, (contact_id,))
        self.conn.commit()
        logger.debug(f"연락처 삭제: {contact_id}")

    def insert_interaction(self, interaction: Dict):
        """
        interaction 삽입 (같은 날짜는 덮어쓰기)

        Args:
            interaction: interaction 정보 딕셔너리
                - contact_id (필수)
                - date (필수, date 객체)
                - content (필수)
        """
        cursor = self.conn.cursor()

        # 기존 데이터 삭제 후 삽입 (덮어쓰기)
        cursor.execute("""
            DELETE FROM interactions
            WHERE contact_id = ? AND date = ?
        """, (interaction['contact_id'], interaction['date']))

        cursor.execute("""
            INSERT INTO interactions (contact_id, date, content)
            VALUES (?, ?, ?)
        """, (
            interaction['contact_id'],
            interaction['date'],
            interaction['content']
        ))
        self.conn.commit()
        logger.debug(f"Interaction 저장: {interaction['contact_id']} - {interaction['date']}")

    def get_interactions(self, contact_id: str) -> List[Dict]:
        """
        특정 연락처의 모든 interaction 조회 (날짜 내림차순)

        Args:
            contact_id: 연락처 ID

        Returns:
            interaction 리스트
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM interactions
            WHERE contact_id = ?
            ORDER BY date DESC
        """, (contact_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """
        테이블 목록 조회

        Returns:
            테이블 이름 리스트
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
        """)
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("데이터베이스 연결 종료")
