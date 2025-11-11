# Contacts-Obsidian TDD 작업 계획

## 프로젝트 개요
macOS Contacts를 Obsidian vault와 SQLite DB로 동기화하는 시스템을 TDD 방법론으로 개발

## TDD 개발 원칙
1. **Red**: 실패하는 테스트 먼저 작성
2. **Green**: 테스트를 통과하는 최소한의 코드 작성
3. **Refactor**: 코드 개선 및 리팩토링

---

## Task 1: 프로젝트 환경 설정 및 구조 생성

### 목표
- Python 프로젝트 기본 구조 설정
- 의존성 관리 및 설정 파일 준비

### Subtasks

#### 1.1 프로젝트 디렉토리 구조 생성
```
contacts-obsidian-sync/
├── src/
│   ├── __init__.py
│   ├── contacts_reader.py      # Contacts 데이터 읽기
│   ├── memo_parser.py          # 메모 파싱 로직
│   ├── db_manager.py           # SQLite 관리
│   ├── obsidian_writer.py      # Obsidian 노트 생성/업데이트
│   ├── stats_calculator.py     # 통계 계산
│   └── config.py               # 설정
├── tests/
│   ├── __init__.py
│   ├── test_contacts_reader.py
│   ├── test_memo_parser.py
│   ├── test_db_manager.py
│   ├── test_obsidian_writer.py
│   ├── test_stats_calculator.py
│   └── fixtures/               # 테스트 데이터
│       ├── sample_contacts.json
│       └── sample_notes.md
├── sync.py                     # 메인 실행 파일
├── requirements.txt            # Python 패키지
├── requirements-dev.txt        # 개발용 패키지 (pytest 등)
├── pytest.ini                  # pytest 설정
├── .gitignore
└── README.md
```

#### 1.2 requirements.txt 작성
```txt
pyobjc-framework-Contacts>=9.0
python-dateutil>=2.8.2
pyyaml>=6.0
```

#### 1.3 requirements-dev.txt 작성
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0
```

#### 1.4 pytest.ini 작성
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

#### 1.5 config.py 기본 구조 작성
```python
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
```

---

## Task 2: 테스트 환경 구축

### 목표
- pytest 설정 및 테스트 픽스처 준비
- 목(Mock) 데이터 생성

### Subtasks

#### 2.1 테스트 픽스처 작성
**tests/fixtures/sample_contacts.json**
```json
[
  {
    "contact_id": "ABC-123-DEF-456-789",
    "first_name": "길동",
    "last_name": "홍",
    "phone": "010-1234-5678",
    "email": "hong@example.com",
    "notes": "250115 점심 미팅. 새 프로젝트 논의\n250110 전화 통화\n241220 연말 인사"
  },
  {
    "contact_id": "XYZ-987-UVW-654-321",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "010-9876-5432",
    "email": "john@example.com",
    "notes": "오늘 커피 미팅\n어제 전화함"
  }
]
```

#### 2.2 conftest.py 작성
```python
import pytest
import json
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def sample_contacts():
    """샘플 연락처 데이터"""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_contacts.json"
    with open(fixture_path) as f:
        return json.load(f)

@pytest.fixture
def temp_vault(tmp_path):
    """임시 Obsidian vault 디렉토리"""
    people_folder = tmp_path / "07 people"
    people_folder.mkdir(parents=True)
    return people_folder

@pytest.fixture
def temp_db(tmp_path):
    """임시 SQLite 데이터베이스"""
    return tmp_path / ".contacts.db"
```

---

## Task 3: [TDD] Contacts 데이터 읽기 기능 개발

### 목표
- macOS Contacts에서 연락처 데이터 읽기
- UUID, 이름, 전화번호, 이메일, 메모 추출

### TDD 사이클

#### 3.1 RED: 테스트 작성
**tests/test_contacts_reader.py**
```python
import pytest
from src.contacts_reader import ContactsReader

class TestContactsReader:
    def test_read_all_contacts_returns_list(self):
        """모든 연락처를 읽고 리스트를 반환해야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()
        assert isinstance(contacts, list)

    def test_contact_has_required_fields(self):
        """각 연락처는 필수 필드를 가져야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact = contacts[0]
            assert 'contact_id' in contact
            assert 'name' in contact
            # phone, email, notes는 선택적

    def test_contact_id_is_uuid_format(self):
        """contact_id는 UUID 형식이어야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact_id = contacts[0]['contact_id']
            assert isinstance(contact_id, str)
            assert len(contact_id) > 0

    def test_korean_name_support(self):
        """한글 이름을 정확히 읽을 수 있어야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        # 실제 환경에서 한글 이름 연락처가 있다고 가정
        korean_contacts = [c for c in contacts if any('\uac00' <= ch <= '\ud7a3' for ch in c.get('name', ''))]

        # 한글 연락처가 있으면 이름이 깨지지 않았는지 확인
        for contact in korean_contacts:
            assert contact['name'] is not None
            assert len(contact['name']) > 0
```

#### 3.2 GREEN: 최소 구현
**src/contacts_reader.py**
```python
from typing import List, Dict, Optional
try:
    from Contacts import CNContactStore, CNContactFetchRequest
    from Foundation import NSPredicate
except ImportError:
    # PyObjC 미설치 시 목 데이터 사용
    CNContactStore = None

class ContactsReader:
    def __init__(self):
        if CNContactStore:
            self.store = CNContactStore.alloc().init()
        else:
            self.store = None

    def read_all_contacts(self) -> List[Dict[str, Optional[str]]]:
        """모든 연락처를 읽어 딕셔너리 리스트로 반환"""
        if not self.store:
            return []

        contacts = []
        # TODO: 실제 Contacts Framework 구현
        return contacts

    def _extract_contact_data(self, cn_contact) -> Dict[str, Optional[str]]:
        """CNContact 객체에서 필요한 데이터 추출"""
        return {
            'contact_id': '',  # TODO
            'name': '',        # TODO
            'phone': None,
            'email': None,
            'notes': None
        }
```

#### 3.3 REFACTOR: 실제 구현 완성
```python
from typing import List, Dict, Optional
from Contacts import (
    CNContactStore,
    CNContactFetchRequest,
    CNContactGivenNameKey,
    CNContactFamilyNameKey,
    CNContactPhoneNumbersKey,
    CNContactEmailAddressesKey,
    CNContactNoteKey,
    CNContactIdentifierKey
)

class ContactsReader:
    def __init__(self):
        self.store = CNContactStore.alloc().init()
        self.keys_to_fetch = [
            CNContactIdentifierKey,
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactPhoneNumbersKey,
            CNContactEmailAddressesKey,
            CNContactNoteKey
        ]

    def read_all_contacts(self) -> List[Dict[str, Optional[str]]]:
        """모든 연락처를 읽어 딕셔너리 리스트로 반환"""
        contacts = []
        fetch_request = CNContactFetchRequest.alloc().initWithKeysToFetch_(self.keys_to_fetch)

        error = None
        def handler(cn_contact, stop):
            contact_data = self._extract_contact_data(cn_contact)
            contacts.append(contact_data)
            return True

        self.store.enumerateContactsWithFetchRequest_error_usingBlock_(
            fetch_request, error, handler
        )

        return contacts

    def _extract_contact_data(self, cn_contact) -> Dict[str, Optional[str]]:
        """CNContact 객체에서 필요한 데이터 추출"""
        # 이름 조합
        first_name = cn_contact.givenName() or ''
        last_name = cn_contact.familyName() or ''
        full_name = f"{last_name}{first_name}".strip() if last_name else first_name

        # 전화번호 (첫 번째 것만)
        phone = None
        if cn_contact.phoneNumbers():
            phone_number = cn_contact.phoneNumbers()[0].value()
            phone = phone_number.stringValue()

        # 이메일 (첫 번째 것만)
        email = None
        if cn_contact.emailAddresses():
            email = cn_contact.emailAddresses()[0].value()

        return {
            'contact_id': cn_contact.identifier(),
            'name': full_name,
            'phone': phone,
            'email': email,
            'notes': cn_contact.note() or ''
        }
```

---

## Task 4: [TDD] 메모 파싱 로직 개발 (날짜 인식)

### 목표
- YYMMDD 형식 날짜 파싱
- 자연어 날짜("오늘", "어제") 처리
- 줄바꿈 처리 (같은 날짜 내용 연결)

### TDD 사이클

#### 4.1 RED: 테스트 작성
**tests/test_memo_parser.py**
```python
import pytest
from datetime import date, timedelta
from src.memo_parser import MemoParser

class TestMemoParser:
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
        assert interactions[1]['date'] == date(2025, 1, 10)
        assert interactions[2]['date'] == date(2024, 12, 20)

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
```

#### 4.2 GREEN: 최소 구현
**src/memo_parser.py**
```python
import re
from datetime import date, timedelta
from typing import List, Dict

class MemoParser:
    def __init__(self):
        # YYMMDD 패턴 (예: 250115)
        self.date_pattern = re.compile(r'^(\d{2})(\d{2})(\d{2})\s+(.+)$')

        # 자연어 날짜 매핑
        self.natural_dates = {
            '오늘': date.today(),
            'today': date.today(),
            '어제': date.today() - timedelta(days=1),
            'yesterday': date.today() - timedelta(days=1)
        }

    def parse(self, memo: str) -> List[Dict]:
        """메모를 파싱하여 interaction 리스트 반환"""
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
                current_interaction = {
                    'date': parsed_date,
                    'content': content
                }
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

    def _parse_yymmdd(self, yy: str, mm: str, dd: str) -> date:
        """YYMMDD를 date 객체로 변환"""
        year = 2000 + int(yy)
        month = int(mm)
        day = int(dd)
        return date(year, month, day)

    def _starts_with_natural_date(self, line: str) -> bool:
        """자연어 날짜로 시작하는지 확인"""
        for keyword in self.natural_dates.keys():
            if line.startswith(keyword):
                return True
        return False

    def _parse_natural_date(self, line: str):
        """자연어 날짜 파싱"""
        for keyword, parsed_date in self.natural_dates.items():
            if line.startswith(keyword):
                content = line[len(keyword):].strip()
                return parsed_date, content
        return None, line
```

#### 4.3 REFACTOR: 에러 처리 추가
```python
def _parse_yymmdd(self, yy: str, mm: str, dd: str) -> date:
    """YYMMDD를 date 객체로 변환"""
    try:
        year = 2000 + int(yy)
        month = int(mm)
        day = int(dd)
        return date(year, month, day)
    except ValueError:
        # 잘못된 날짜는 오늘로 대체
        return date.today()
```

---

## Task 5: [TDD] SQLite 데이터베이스 관리 기능 개발

### 목표
- SQLite 스키마 생성
- contacts 테이블 CRUD
- interactions 테이블 CRUD (UNIQUE 제약 처리)

### TDD 사이클

#### 5.1 RED: 테스트 작성
**tests/test_db_manager.py**
```python
import pytest
from datetime import date
from src.db_manager import DatabaseManager

class TestDatabaseManager:
    def test_create_tables(self, temp_db):
        """테이블을 정상적으로 생성해야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        # 테이블 존재 확인
        tables = db.get_table_names()
        assert 'contacts' in tables
        assert 'interactions' in tables

    def test_insert_contact(self, temp_db):
        """연락처를 삽입할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'email': 'hong@example.com'
        }
        db.insert_contact(contact)

        # 삽입 확인
        result = db.get_contact('ABC-123')
        assert result['name'] == '홍길동'
        assert result['phone'] == '010-1234-5678'

    def test_update_contact(self, temp_db):
        """연락처를 업데이트할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678'
        }
        db.insert_contact(contact)

        # 업데이트
        updated = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-9999-9999'  # 변경
        }
        db.update_contact(updated)

        result = db.get_contact('ABC-123')
        assert result['phone'] == '010-9999-9999'

    def test_insert_interaction(self, temp_db):
        """interaction을 삽입할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        # 먼저 contact 삽입
        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        interaction = {
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '점심 미팅'
        }
        db.insert_interaction(interaction)

        # 삽입 확인
        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 1
        assert interactions[0]['content'] == '점심 미팅'

    def test_unique_constraint_same_date(self, temp_db):
        """같은 날짜 interaction은 덮어쓰기 되어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        # 첫 번째 삽입
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '점심 미팅'
        })

        # 같은 날짜 다시 삽입 (덮어쓰기)
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '저녁 미팅'  # 변경됨
        })

        # 하나만 있어야 하고, 최신 내용이어야 함
        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 1
        assert interactions[0]['content'] == '저녁 미팅'

    def test_get_all_contacts(self, temp_db):
        """모든 연락처를 조회할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})
        db.insert_contact({'contact_id': 'XYZ-789', 'name': 'John'})

        contacts = db.get_all_contacts()
        assert len(contacts) == 2
```

#### 5.2 GREEN: 최소 구현
**src/db_manager.py**
```python
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row

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
                FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
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

    def insert_contact(self, contact: Dict):
        """연락처 삽입 (REPLACE로 업데이트도 처리)"""
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

    def update_contact(self, contact: Dict):
        """연락처 업데이트"""
        self.insert_contact(contact)  # REPLACE 사용

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """연락처 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts WHERE contact_id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_contacts(self) -> List[Dict]:
        """모든 연락처 조회"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contacts")
        return [dict(row) for row in cursor.fetchall()]

    def insert_interaction(self, interaction: Dict):
        """interaction 삽입 (같은 날짜는 덮어쓰기)"""
        cursor = self.conn.cursor()

        # 기존 데이터 삭제 후 삽입
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

    def get_interactions(self, contact_id: str) -> List[Dict]:
        """특정 연락처의 모든 interaction 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM interactions
            WHERE contact_id = ?
            ORDER BY date DESC
        """, (contact_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_table_names(self) -> List[str]:
        """테이블 목록 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
        """)
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """연결 종료"""
        self.conn.close()
```

---

## Task 6: [TDD] Obsidian 노트 생성/업데이트 기능 개발

### 목표
- YAML frontmatter 생성
- Markdown 노트 생성
- UUID 기반 매칭 및 스마트 머지

### TDD 사이클

#### 6.1 RED: 테스트 작성
**tests/test_obsidian_writer.py**
```python
import pytest
from pathlib import Path
from datetime import date
from src.obsidian_writer import ObsidianWriter

class TestObsidianWriter:
    def test_create_new_note(self, temp_vault):
        """새 노트를 생성할 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'email': 'hong@example.com'
        }

        interactions = [
            {'date': date(2025, 1, 15), 'content': '점심 미팅'},
            {'date': date(2025, 1, 10), 'content': '전화 통화'}
        ]

        stats = {
            'last_contact': date(2025, 1, 15),
            'contact_count': 2,
            'last_6month_contacts': 2
        }

        writer.write_note(contact, interactions, stats)

        # 파일 생성 확인
        note_path = temp_vault / "홍길동.md"
        assert note_path.exists()

        # 내용 확인
        content = note_path.read_text()
        assert 'contact_id: ABC-123' in content
        assert '홍길동' in content
        assert '점심 미팅' in content

    def test_update_existing_note(self, temp_vault):
        """기존 노트를 업데이트할 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        # 기존 노트 작성 (수동 섹션 포함)
        existing_note = temp_vault / "홍길동.md"
        existing_note.write_text("""---
contact_id: ABC-123
name: 홍길동
---

# 홍길동

## 활동 기록
### 2025-01-10
전화 통화

## 내 메모
신뢰할 수 있는 친구
""")

        # 업데이트
        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678'
        }

        interactions = [
            {'date': date(2025, 1, 15), 'content': '점심 미팅'},  # 새로운 것
            {'date': date(2025, 1, 10), 'content': '전화 통화'}
        ]

        stats = {'last_contact': date(2025, 1, 15), 'contact_count': 2}

        writer.write_note(contact, interactions, stats)

        # 수동 섹션 보존 확인
        content = existing_note.read_text()
        assert '신뢰할 수 있는 친구' in content
        assert '점심 미팅' in content

    def test_find_note_by_contact_id(self, temp_vault):
        """contact_id로 노트를 찾을 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        # 파일명과 다른 이름으로 저장
        note = temp_vault / "홍길동(ABC회사).md"
        note.write_text("""---
contact_id: ABC-123
name: 홍길동
---
""")

        # contact_id로 찾기
        found = writer.find_note_by_contact_id('ABC-123')
        assert found == note

    def test_preserve_manual_sections(self, temp_vault):
        """수동 작성 섹션을 보존해야 함"""
        writer = ObsidianWriter(temp_vault)

        existing = temp_vault / "홍길동.md"
        existing.write_text("""---
contact_id: ABC-123
---

# 홍길동

## 활동 기록
### 2025-01-10
전화 통화

## 내 메모
중요한 메모

## 특이사항
- 자녀 2명
""")

        contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
        interactions = [{'date': date(2025, 1, 15), 'content': '새 미팅'}]
        stats = {'last_contact': date(2025, 1, 15), 'contact_count': 1}

        writer.write_note(contact, interactions, stats)

        content = existing.read_text()
        assert '중요한 메모' in content
        assert '자녀 2명' in content
```

#### 6.2 GREEN & REFACTOR: 구현
**src/obsidian_writer.py**
```python
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date

class ObsidianWriter:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.auto_sync_marker = "*⚠️ 자동 동기화 섹션*"
        self.manual_marker = "*✏️ 자유롭게 작성*"

    def write_note(self, contact: Dict, interactions: List[Dict], stats: Dict):
        """노트 작성 또는 업데이트"""
        contact_id = contact['contact_id']

        # 기존 노트 찾기
        existing_note = self.find_note_by_contact_id(contact_id)

        if existing_note:
            self._update_note(existing_note, contact, interactions, stats)
        else:
            self._create_note(contact, interactions, stats)

    def _create_note(self, contact: Dict, interactions: List[Dict], stats: Dict):
        """새 노트 생성"""
        filename = f"{contact['name']}.md"
        note_path = self.vault_path / filename

        content = self._generate_content(contact, interactions, stats)
        note_path.write_text(content, encoding='utf-8')

    def _update_note(self, note_path: Path, contact: Dict, interactions: List[Dict], stats: Dict):
        """기존 노트 업데이트 (수동 섹션 보존)"""
        existing_content = note_path.read_text(encoding='utf-8')

        # 수동 섹션 추출
        manual_sections = self._extract_manual_sections(existing_content)

        # 새 내용 생성
        new_content = self._generate_content(contact, interactions, stats, manual_sections)

        note_path.write_text(new_content, encoding='utf-8')

    def _generate_content(self, contact: Dict, interactions: List[Dict],
                          stats: Dict, manual_sections: str = "") -> str:
        """노트 내용 생성"""
        # YAML frontmatter
        frontmatter = {
            'type': 'person',
            'contact_id': contact['contact_id'],
            'name': contact['name'],
            'phone': contact.get('phone'),
            'email': contact.get('email'),
            'last_contact': str(stats.get('last_contact', '')),
            'contact_count': stats.get('contact_count', 0),
            'last_6month_contacts': stats.get('last_6month_contacts', 0),
            'tags': ['people']
        }

        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        # 활동 기록
        activity_section = "## 활동 기록\n"
        activity_section += f"{self.auto_sync_marker}\n\n"

        for interaction in interactions:
            interaction_date = interaction['date']
            content = interaction['content']
            activity_section += f"### {interaction_date}\n{content}\n\n"

        # 전체 조합
        full_content = f"""---
{yaml_str}---

# {contact['name']}

## 기본 정보
- **연락처**: {contact.get('phone', '')}
- **이메일**: {contact.get('email', '')}
- **총 연락 횟수**: {stats.get('contact_count', 0)}회

{activity_section}

{manual_sections}
"""
        return full_content

    def _extract_manual_sections(self, content: str) -> str:
        """수동 작성 섹션 추출"""
        # 간단 구현: "## 내 메모" 이후 모든 내용
        if "## 내 메모" in content:
            parts = content.split("## 내 메모", 1)
            return "## 내 메모" + parts[1]
        return ""

    def find_note_by_contact_id(self, contact_id: str) -> Optional[Path]:
        """contact_id로 노트 찾기"""
        for note_path in self.vault_path.glob("*.md"):
            content = note_path.read_text(encoding='utf-8')

            # YAML frontmatter에서 contact_id 추출
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter and frontmatter.get('contact_id') == contact_id:
                        return note_path

        return None
```

---

## Task 7: [TDD] 통계 계산 로직 개발

### 목표
- 총 연락 횟수 계산
- 최근 6개월 연락 횟수
- 마지막 연락일

### TDD 사이클

#### 7.1 RED: 테스트 작성
**tests/test_stats_calculator.py**
```python
import pytest
from datetime import date, timedelta
from src.stats_calculator import StatsCalculator

class TestStatsCalculator:
    def test_calculate_contact_count(self, temp_db):
        """총 연락 횟수를 계산해야 함"""
        from src.db_manager import DatabaseManager

        db = DatabaseManager(temp_db)
        db.create_tables()
        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        # 3개 interaction
        db.insert_interaction({'contact_id': 'ABC-123', 'date': date(2025, 1, 15), 'content': 'A'})
        db.insert_interaction({'contact_id': 'ABC-123', 'date': date(2025, 1, 10), 'content': 'B'})
        db.insert_interaction({'contact_id': 'ABC-123', 'date': date(2024, 12, 1), 'content': 'C'})

        calc = StatsCalculator(db)
        stats = calc.calculate_stats('ABC-123')

        assert stats['contact_count'] == 3

    def test_calculate_last_contact(self, temp_db):
        """마지막 연락일을 계산해야 함"""
        from src.db_manager import DatabaseManager

        db = DatabaseManager(temp_db)
        db.create_tables()
        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        db.insert_interaction({'contact_id': 'ABC-123', 'date': date(2025, 1, 15), 'content': 'A'})
        db.insert_interaction({'contact_id': 'ABC-123', 'date': date(2025, 1, 10), 'content': 'B'})

        calc = StatsCalculator(db)
        stats = calc.calculate_stats('ABC-123')

        assert stats['last_contact'] == date(2025, 1, 15)

    def test_calculate_last_6month_contacts(self, temp_db):
        """최근 6개월 연락 횟수를 계산해야 함"""
        from src.db_manager import DatabaseManager

        db = DatabaseManager(temp_db)
        db.create_tables()
        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        today = date.today()

        # 최근 6개월 내: 2개
        db.insert_interaction({'contact_id': 'ABC-123', 'date': today - timedelta(days=30), 'content': 'A'})
        db.insert_interaction({'contact_id': 'ABC-123', 'date': today - timedelta(days=60), 'content': 'B'})

        # 6개월 이전: 1개
        db.insert_interaction({'contact_id': 'ABC-123', 'date': today - timedelta(days=200), 'content': 'C'})

        calc = StatsCalculator(db)
        stats = calc.calculate_stats('ABC-123')

        assert stats['last_6month_contacts'] == 2
        assert stats['contact_count'] == 3
```

#### 7.2 GREEN & REFACTOR: 구현
**src/stats_calculator.py**
```python
from datetime import date, timedelta
from typing import Dict
from src.db_manager import DatabaseManager

class StatsCalculator:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def calculate_stats(self, contact_id: str) -> Dict:
        """연락처의 통계 계산"""
        interactions = self.db.get_interactions(contact_id)

        if not interactions:
            return {
                'contact_count': 0,
                'last_contact': None,
                'last_6month_contacts': 0
            }

        # 총 연락 횟수
        contact_count = len(interactions)

        # 마지막 연락일
        last_contact = max(i['date'] for i in interactions)

        # 최근 6개월 연락 횟수
        six_months_ago = date.today() - timedelta(days=180)
        last_6month_contacts = sum(
            1 for i in interactions
            if isinstance(i['date'], date) and i['date'] >= six_months_ago
        )

        return {
            'contact_count': contact_count,
            'last_contact': last_contact,
            'last_6month_contacts': last_6month_contacts
        }
```

---

## Task 8: 메인 동기화 스크립트 통합 및 E2E 테스트

### 목표
- 모든 컴포넌트 통합
- End-to-End 테스트 작성
- 에러 처리 및 로깅

### E2E 테스트

**tests/test_integration.py**
```python
import pytest
from pathlib import Path
from datetime import date
from src.db_manager import DatabaseManager
from src.memo_parser import MemoParser
from src.obsidian_writer import ObsidianWriter
from src.stats_calculator import StatsCalculator

class TestIntegration:
    def test_full_sync_flow(self, temp_vault, temp_db):
        """전체 동기화 플로우 테스트"""
        # 1. 메모 파싱
        parser = MemoParser()
        memo = """250115 점심 미팅
250110 전화 통화"""
        interactions = parser.parse(memo)

        # 2. DB 저장
        db = DatabaseManager(temp_db)
        db.create_tables()

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678'
        }
        db.insert_contact(contact)

        for interaction in interactions:
            interaction['contact_id'] = 'ABC-123'
            db.insert_interaction(interaction)

        # 3. 통계 계산
        calc = StatsCalculator(db)
        stats = calc.calculate_stats('ABC-123')

        # 4. Obsidian 노트 작성
        writer = ObsidianWriter(temp_vault)
        writer.write_note(contact, interactions, stats)

        # 5. 검증
        note_path = temp_vault / "홍길동.md"
        assert note_path.exists()

        content = note_path.read_text()
        assert 'ABC-123' in content
        assert '점심 미팅' in content
        assert 'contact_count: 2' in content
```

### 메인 스크립트

**sync.py**
```python
#!/usr/bin/env python3
"""
Contacts-Obsidian 동기화 메인 스크립트
"""
import logging
from pathlib import Path
from src.config import VAULT_PATH, PEOPLE_FOLDER, DB_PATH
from src.contacts_reader import ContactsReader
from src.memo_parser import MemoParser
from src.db_manager import DatabaseManager
from src.obsidian_writer import ObsidianWriter
from src.stats_calculator import StatsCalculator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """메인 동기화 로직"""
    try:
        logger.info("동기화 시작")

        # 1. Contacts 읽기
        logger.info("Contacts 데이터 읽는 중...")
        reader = ContactsReader()
        contacts = reader.read_all_contacts()
        logger.info(f"{len(contacts)}개 연락처 발견")

        # 2. DB 초기화
        db = DatabaseManager(DB_PATH)
        db.create_tables()

        # 3. 파서 및 writer 초기화
        parser = MemoParser()
        writer = ObsidianWriter(PEOPLE_FOLDER)
        calc = StatsCalculator(db)

        # 4. 각 연락처 처리
        for contact in contacts:
            try:
                contact_id = contact['contact_id']
                logger.info(f"처리 중: {contact['name']} ({contact_id})")

                # Contact 저장
                db.insert_contact(contact)

                # 메모 파싱
                memo = contact.get('notes', '')
                interactions = parser.parse(memo)

                # Interaction 저장
                for interaction in interactions:
                    interaction['contact_id'] = contact_id
                    db.insert_interaction(interaction)

                # 통계 계산
                stats = calc.calculate_stats(contact_id)

                # Obsidian 노트 작성
                writer.write_note(contact, interactions, stats)

            except Exception as e:
                logger.error(f"{contact['name']} 처리 실패: {e}")
                continue

        logger.info("동기화 완료")

    except Exception as e:
        logger.error(f"동기화 실패: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    main()
```

---

## 추가 개선사항

### 1. 코드 품질
- `black`으로 포맷팅
- `flake8`으로 린팅
- `mypy`로 타입 체크

### 2. CI/CD
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src
      - run: black --check src tests
      - run: flake8 src tests
```

### 3. 문서화
- README.md: 설치 및 사용법
- API 문서 (Sphinx)
- 예제 및 FAQ

---

## 타임라인 (TDD 기반)

| Week | Task | 설명 |
|------|------|------|
| 1 | Task 1-2 | 환경 설정 및 테스트 인프라 |
| 2 | Task 3-4 | Contacts 읽기 + 메모 파싱 (TDD) |
| 3 | Task 5 | SQLite DB 관리 (TDD) |
| 4 | Task 6 | Obsidian 노트 생성 (TDD) |
| 5 | Task 7-8 | 통계 계산 + E2E 통합 |

---

**작성일**: 2025-11-10
**방법론**: TDD (Test-Driven Development)
**상태**: 작업 계획 완료
