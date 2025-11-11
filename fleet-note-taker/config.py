import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # Claude CLI 설정
    # None으로 두면 자동으로 claude 명령어를 찾습니다
    CLAUDE_CLI_PATH = None  # 또는 '/usr/local/bin/claude' 같은 경로 지정

    # ========================================
    # 폴더 경로 설정 - 환경 변수 우선, 없으면 기본값
    # ========================================

    # 원본 노트 폴더 (처리할 이미지 파일들)
    ORIGINAL_NOTES_DIR = os.getenv('ORIGINAL_NOTES_DIR', os.path.expanduser('~/agents/memo2fleet'))

    # 연결된 노트 폴더 (처리 완료된 이미지들)
    VAULT_PATH = os.getenv('VAULT_PATH', os.path.join(os.path.expanduser('~'), 'Desktop', 'SecondBrain'))
    LINKED_NOTES_DIR = os.getenv('LINKED_NOTES_DIR', os.path.join(VAULT_PATH, '99 Fleet', 'linked_notes'))

    # 생성된 노트 폴더 (마크다운 파일들)
    GENERATED_NOTES_DIR = os.getenv('GENERATED_NOTES_DIR', os.path.join(VAULT_PATH, '99 Fleet'))

    # 예시: 절대 경로로 설정하고 싶다면 주석을 해제하고 수정하세요
    # ORIGINAL_NOTES_DIR = '/Users/username/Documents/my_notes/original'
    # LINKED_NOTES_DIR = '/Users/username/Documents/my_notes/linked'
    # GENERATED_NOTES_DIR = '/Users/username/Documents/my_notes/generated'

    # ========================================

    # 파일 설정
    MAX_TITLE_LENGTH = 40
    SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    SUPPORTED_MARKDOWN_FORMATS = ['md', 'markdown']

    # 노트 템플릿 (이미지용)
    FLEET_TEMPLATE = """---
title: {title}
created: {created_date}
modification date: {created_date}
source:
aliases:
type: fleet
tags: {tags}
---
- [ ] 작업하기

## Notes
{notes}

**원본 이미지**: ![[{image_link}]]

## Quotes



## Source
-


## Links
-

---
"""

    # 노트 템플릿 (마크다운용 - 이미지 링크 없음)
    FLEET_TEMPLATE_MD = """---
title: {title}
created: {created_date}
modification date: {created_date}
source:
aliases:
type: fleet
tags: {tags}
---
- [ ] 작업하기

## Notes
{notes}

## Quotes



## Source
-


## Links
{links}

---
"""

    @classmethod
    def create_directories(cls):
        """필요한 디렉토리 생성"""
        for directory in [cls.ORIGINAL_NOTES_DIR, cls.LINKED_NOTES_DIR, cls.GENERATED_NOTES_DIR]:
            os.makedirs(directory, exist_ok=True)

    @classmethod
    def validate_config(cls):
        """설정 검증"""
        # Claude CLI 경로 확인은 ClaudeCliWrapper에서 처리
        return True

    @classmethod
    def print_directory_info(cls):
        """디렉토리 정보 출력"""
        print("=== 폴더 설정 정보 ===")
        print(f"원본 노트 폴더: {cls.ORIGINAL_NOTES_DIR}")
        print(f"연결된 노트 폴더: {cls.LINKED_NOTES_DIR}")
        print(f"생성된 노트 폴더: {cls.GENERATED_NOTES_DIR}")
        print("=====================")
