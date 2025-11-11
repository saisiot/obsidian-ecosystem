"""
설정 파일
Contacts-Obsidian 동기화 시스템의 전역 설정
"""
import os
from pathlib import Path

# Obsidian vault 경로
VAULT_PATH = Path.home() / "Desktop" / "SecondBrain"
PEOPLE_FOLDER = VAULT_PATH / "07 people"
DB_PATH = PEOPLE_FOLDER / ".contacts.db"

# 날짜 포맷
DATE_FORMAT_YYMMDD = r'(\d{2})(\d{2})(\d{2})'  # 250115
DATE_FORMAT_ISO = '%Y-%m-%d'

# 통계 계산 기간
RECENT_MONTHS = 6

# 자동 동기화 마커
AUTO_SYNC_MARKER = "*⚠️ 자동 동기화 섹션 - 이 섹션은 매일 자동으로 업데이트됨*"
MANUAL_MARKER = "*✏️ 자유롭게 작성 - 동기화 시 보존됨*"

# 로깅 설정
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = Path.home() / ".contacts_sync.log"
