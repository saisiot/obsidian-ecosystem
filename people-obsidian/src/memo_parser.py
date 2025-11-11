"""
메모 파싱 로직
TDD GREEN 단계: 최소 구현
"""
import re
from datetime import date, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MemoParser:
    """Contacts 메모를 파싱하여 interaction 리스트로 변환하는 클래스"""

    def __init__(self):
        """MemoParser 초기화"""
        # YYMMDD 패턴 (예: 250115)
        self.date_pattern = re.compile(r'^(\d{2})(\d{2})(\d{2})\s+(.+)$')

        # 자연어 날짜 매핑
        self.natural_dates = {
            '오늘': date.today(),
            'today': date.today(),
            '어제': date.today() - timedelta(days=1),
            'yesterday': date.today() - timedelta(days=1)
        }

    def parse(self, memo: Optional[str]) -> List[Dict]:
        """
        메모를 파싱하여 interaction 리스트 반환

        Args:
            memo: Contacts 메모 문자열

        Returns:
            List[Dict]: interaction 리스트
                - date: 날짜 (date 객체)
                - content: 내용
        """
        if not memo or not memo.strip():
            return []

        interactions = []
        current_interaction = None

        for line in memo.split('\n'):
            line = line.strip()
            if not line:
                continue

            # YYMMDD 패턴 체크
            match = self.date_pattern.match(line)
            if match:
                # 이전 interaction 저장
                if current_interaction:
                    interactions.append(current_interaction)

                # 새 interaction 시작
                yy, mm, dd, content = match.groups()
                parsed_date = self._parse_yymmdd(yy, mm, dd)

                if parsed_date:
                    current_interaction = {
                        'date': parsed_date,
                        'content': content
                    }
                else:
                    # 잘못된 날짜는 무시
                    current_interaction = None

            # 자연어 날짜 체크
            elif self._starts_with_natural_date(line):
                if current_interaction:
                    interactions.append(current_interaction)

                natural_date, content = self._parse_natural_date(line)
                current_interaction = {
                    'date': natural_date,
                    'content': content
                }

            # 날짜 없는 줄 (이전 내용에 추가)
            elif current_interaction:
                current_interaction['content'] += '\n' + line

        # 마지막 interaction 저장
        if current_interaction:
            interactions.append(current_interaction)

        return interactions

    def _parse_yymmdd(self, yy: str, mm: str, dd: str) -> Optional[date]:
        """
        YYMMDD를 date 객체로 변환

        Args:
            yy: 연도 (2자리)
            mm: 월 (2자리)
            dd: 일 (2자리)

        Returns:
            date 객체 또는 None (잘못된 날짜인 경우)
        """
        try:
            year = 2000 + int(yy)
            month = int(mm)
            day = int(dd)
            return date(year, month, day)
        except ValueError:
            # 잘못된 날짜 (예: 13월, 32일 등)
            logger.warning(f"잘못된 날짜 형식: {yy}{mm}{dd}")
            return None

    def _starts_with_natural_date(self, line: str) -> bool:
        """
        자연어 날짜로 시작하는지 확인

        Args:
            line: 메모 라인

        Returns:
            bool: 자연어 날짜로 시작하면 True
        """
        for keyword in self.natural_dates.keys():
            if line.startswith(keyword):
                return True
        return False

    def _parse_natural_date(self, line: str):
        """
        자연어 날짜 파싱

        Args:
            line: 메모 라인

        Returns:
            (date, content) 튜플
        """
        for keyword, parsed_date in self.natural_dates.items():
            if line.startswith(keyword):
                content = line[len(keyword):].strip()
                return parsed_date, content
        return None, line
