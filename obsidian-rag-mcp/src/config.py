import os
from pathlib import Path

# Vault 설정 - 환경 변수 우선, 없으면 기본값
VAULT_PATH = Path(os.getenv('OBSIDIAN_VAULT_PATH', Path.home() / "Desktop" / "SecondBrain"))

# 제외 패턴 (vault 전체를 스캔하되, 아래 패턴은 제외)
EXCLUDE_PATTERNS = [
    ".*",  # 숨김 폴더/파일 (., .obsidian, .trash 등)
    "99 Fleet",
    "Excalidraw",
    "_attachments",
    "templates",
    "linked_notes",
    "언젠간 쓸일이 있을 것들",
    ".SynologyWorkingDirectory",  # Synology 작업 디렉토리
]

# 임베딩 모델 (한글 성능 우수)
EMBEDDING_MODEL = "BAAI/bge-m3"

# ChromaDB 설정
PROJECT_ROOT = Path(__file__).parent.parent
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "secondbrain"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 메타데이터 파일
METADATA_FILE = PROJECT_ROOT / "data" / "index_metadata.json"

# 백업 설정
BACKUP_DIR = PROJECT_ROOT / "data" / "backup"
MAX_BACKUPS = 5
