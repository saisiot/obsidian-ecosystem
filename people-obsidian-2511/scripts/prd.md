# PRD: Contacts-Obsidian 인맥 관리 동기화 시스템

## 1. 프로젝트 개요

### 목적
macOS Contacts 앱에 입력된 인맥 정보를 Obsidian vault와 SQLite 데이터베이스에 동시에 동기화하여, 모바일에서의 편리한 입력과 Obsidian 기반 PKM 시스템의 장점, 그리고 SQLite의 강력한 분석 기능을 모두 활용

### 배경
- 현재: Contacts 앱의 메모란에 'YYMMDD 내용' 형식으로 기록
- 문제: Obsidian vault와 분리되어 있어 통합 관리 및 검색 불가
- 해결: 하이브리드 동기화로 정성적 PKM과 정량적 분석 모두 가능

### 아키텍처
```
iPhone Contacts 입력
    ↓
Mac 동기화 스크립트 (자동/수동)
    ↓
├─→ Obsidian 노트 (사람 중심, 전체 기록)
│   - 읽기/쓰기 편한 Markdown
│   - 벡터DB로 의미 검색
│   - 다른 노트와 링크
│   - 수동 인사이트 추가
│
└─→ SQLite DB (raw data, 분석용)
    - 개별 interaction 기록
    - 복잡한 집계 쿼리
    - 시계열 분석
    - 통계 생성
    - 외부 도구 연동
```

## 2. 핵심 요구사항

### 2.1 데이터 소스
- **입력 채널**: macOS Contacts 앱 (주로 iPhone에서 입력)
- **활용 필드**:
  - 이름 (First Name, Last Name 조합)
  - 전화번호
  - 이메일
  - 메모 (Notes 필드 - 시간순 기록 포함)

### 2.2 데이터 출력

#### Obsidian 노트
- **저장 위치**: `~/Desktop/SecondBrain/07 people/`
- **파일명 규칙**: `{이름}.md` (예: `홍길동.md`)
  - 사용자가 자유롭게 변경 가능 (예: `홍길동(ABC회사).md`)
- **고유 식별자**: `contact_id` (Contacts 앱의 UUID)
  - macOS Contacts가 부여하는 영구적인 고유 식별자
  - 이름, 전화번호, 이메일이 변경되어도 동일하게 유지
  - 파일명과 무관하게 Contacts와 매칭
  - YAML frontmatter에 저장
- **파일 구조**: 
  - 메타데이터 (YAML frontmatter)
  - 기본 정보 섹션
  - 전체 활동 기록 (시간순 정렬)
  - 자유로운 추가 섹션 (특이사항, 관계 등)

#### SQLite 데이터베이스
- **저장 위치**: `~/Desktop/SecondBrain/07 people/.contacts.db`
- **테이블 구조**:
  - `contacts`: 사람 기본 정보
  - `interactions`: 개별 대화/만남 기록 (raw data)
- **용도**:
  - 정량적 분석 (연락 빈도, 패턴)
  - 복잡한 SQL 쿼리
  - 통계 계산
  - 외부 도구 연동
- **참고**: 숨김 파일(`.contacts.db`)로 저장하여 Obsidian 파일 목록에서 제외

### 2.3 동기화 로직
- **트리거**: 주기적 실행 (하루 1회, 또는 수동 실행)
- **권장 실행 시간**: 새벽 2시 (Mac이 켜져있을 때)
- **동작 방식**:
  1. Contacts 앱에서 모든 연락처 데이터 읽기
  2. 각 연락처의 UUID를 `contact_id`로 사용
  3. 메모 필드 파싱 (YYMMDD 형식 인식)
  4. **SQLite 저장**:
     - `contacts` 테이블에 기본 정보 저장/업데이트
     - `interactions` 테이블에 개별 대화 기록 저장
     - 통계 계산 (contact_count, last_6month_contacts 등)
  5. **Obsidian 노트 생성/업데이트**:
     - `07 people` 폴더에서 동일한 `contact_id` (UUID)를 가진 노트 검색
     - 매칭되는 노트가 있으면 업데이트, 없으면 신규 생성
     - 파일명과 무관하게 `contact_id`로만 매칭
     - 전체 활동 기록을 시간순으로 포함
     - SQLite에서 계산한 통계를 YAML에 포함
  6. 기존 벡터DB는 주기적 업데이트로 자동 반영

## 3. 기능 명세

### 3.1 필수 기능 (MVP)
1. **Contacts 데이터 읽기**
   - macOS에서 iCloud 동기화된 Contacts 데이터 접근
   - 한글/영문 이름 모두 정확히 추출
   - 전체 연락처 목록 조회
   - 이름, 전화번호, 이메일, 메모 필드 추출

2. **메모 파싱**
   - 'YYMMDD 내용' 형식 인식 (정규식)
   - 자연어 날짜 표현 처리 ("오늘", "어제")
   - 날짜 없는 메모는 Contacts 수정 시각 사용
   - 시간순 정렬 유지

3. **SQLite 데이터베이스 관리**
   - `contacts` 테이블: 기본 정보 저장/업데이트
   - `interactions` 테이블: 개별 대화 기록 저장
   - 통계 계산 (contact_count, last_6month_contacts 등)
   - 중복 방지 (contact_id + date 기준)

4. **Obsidian 노트 생성/업데이트**
   - Markdown 파일 생성
   - YAML frontmatter 포함 (SQLite 통계 포함)
   - 전체 활동 기록 포함 (시간순 정렬)
   - 기존 파일 존재 시 스마트 업데이트
   - 수동 작성 섹션 보존

5. **자동화 설정**
   - LaunchAgent로 주기적 실행 (하루 1회, 새벽 2시 권장)
   - 수동 실행 스크립트 제공

### 3.2 부가 기능 (향후 고려)
1. **Dataview 쿼리 템플릿**
   - 연락이 뜸한 사람 조회
   - 최근 활발한 관계 조회
   - 카테고리별 정리

2. **SQLite 분석 스크립트**
   - 월별 연락 빈도 분석
   - 관계 강도 점수 계산
   - 연락 주기 예측

3. **Obsidian SQL Query 플러그인 연동**
   - Obsidian 노트 안에서 SQLite 쿼리 실행
   - 동적 테이블 생성

4. **알림 기능**
   - 오래 연락 안 한 사람 알림
   - 중요 이벤트 리마인더

5. **대시보드/시각화**
   - Python으로 관계 네트워크 시각화
   - 시계열 그래프

## 4. 데이터 구조

### 4.1 Obsidian 노트 템플릿
```markdown
---
type: person
contact_id: ABC-123-DEF-456-789
name: 홍길동
phone: 010-1234-5678
email: hong@example.com
last_contact: 2025-01-15
contact_count: 12
last_6month_contacts: 5
first_met: 2023-03-10
relationship_strength: 8
category: work
tags: [people, work]
---

# 홍길동

## 기본 정보
- **연락처**: 010-1234-5678
- **이메일**: hong@example.com
- **처음 만남**: 2023-03-10
- **총 연락 횟수**: 12회
- **최근 6개월**: 5회

## 활동 기록
*⚠️ 자동 동기화 섹션 - 이 섹션은 매일 자동으로 업데이트됨*

### 2025-01-15
점심 미팅. 새 프로젝트 논의. AI 도입 방안에 대해 이야기 나눔.

### 2025-01-10
전화 통화. 다음 주 일정 조율.

### 2024-12-20
연말 인사. 내년에도 잘 부탁한다고.

### 2024-11-10
[[서울 AI 컨퍼런스]]에서 만남. 명함 교환.

... (전체 기록 계속)

## 내 메모
*✏️ 자유롭게 작성 - 동기화 시 보존됨*
- 이 사람은 정말 신뢰할 수 있는 친구
- 투자 관련 조언 구할 때 좋음
- 가족 이야기 편하게 나눌 수 있음

## 관계 히스토리
*✏️ 자유롭게 작성 - 동기화 시 보존됨*
- 2020년 세미나에서 처음 만남
- 2021년부터 정기적으로 점심
- [[AI 스터디]]를 같이 하고 있음

## 특이사항
*✏️ 자유롭게 작성 - 동기화 시 보존됨*
- 농심 다니는 철밥통
- 투자에 관심 많음 (MSTY 등)
- 자녀 2명 (첫째, 둘째)
```

**섹션 구분**:
- **자동 동기화**: YAML frontmatter, 기본 정보, 활동 기록
- **수동 작성 보존**: 내 메모, 관계 히스토리, 특이사항 등

### 4.2 메타데이터 필드 정의
- `type`: person (고정값)
- `contact_id`: Contacts 앱의 UUID (예: `ABC-123-DEF-456-789`)
  - macOS Contacts가 부여하는 영구적인 고유 식별자
  - 이름, 전화번호, 이메일 변경과 무관하게 동일한 사람 추적
  - 파일명과 무관하게 동기화 추적
- `name`: 전체 이름
- `phone`: 전화번호
- `email`: 이메일
- `last_contact`: 마지막 연락일 (SQLite에서 계산)
- `contact_count`: 총 연락 횟수 (SQLite에서 계산)
- `last_6month_contacts`: 최근 6개월 연락 횟수 (SQLite에서 계산)
- `first_met`: 첫 만남 날짜 (가장 오래된 interaction)
- `relationship_strength`: 관계 강도 점수 1-10 (선택적, 수동 입력 가능)
- `category`: work, friend, family 등
- `created`: 노트 최초 생성일
- `updated`: 마지막 업데이트일
- `tags`: [people] + 추가 태그

### 4.3 SQLite 스키마

#### contacts 테이블
```sql
CREATE TABLE contacts (
    contact_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    first_met DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### interactions 테이블
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id TEXT NOT NULL,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
    UNIQUE(contact_id, date)  -- 같은 사람의 같은 날짜는 하나만 (덮어쓰기)
);

-- 인덱스
CREATE INDEX idx_interactions_contact ON interactions(contact_id);
CREATE INDEX idx_interactions_date ON interactions(date);
CREATE INDEX idx_interactions_contact_date ON interactions(contact_id, date);
```

**UNIQUE 제약 및 덮어쓰기 전략**:
- `UNIQUE(contact_id, date)`: 같은 사람의 같은 날짜는 하나의 레코드만 유지
- **동작 방식**:
  - 같은 날짜 새로운 내용: 기존 레코드 삭제 후 새로 INSERT (덮어쓰기)
  - Contacts에서 내용 수정: 최신 내용으로 업데이트 (수정 이력 미보존)
  - 이유: 실제 사용 시 같은 날짜 수정은 "업데이트"이지 "새로운 만남"이 아님
- **장점**:
  - 중복 레코드 방지
  - Obsidian 노트가 깔끔하게 유지
  - 구현 간단
- **제약사항**:
  - 같은 날 여러 번 만난 경우 마지막 것만 저장됨
  - 실제로는 드물고, 필요시 다른 날짜로 분리하거나 내용에 "점심/저녁" 명시

### 4.4 데이터 흐름 예시

**Contacts 메모**:
```
250115 점심 미팅. 새 프로젝트 논의
250110 전화 통화
241220 연말 인사
```

**Contacts UUID**: `ABC-123-DEF-456-789`

**↓ 파싱 후**

**SQLite**:
```sql
-- contacts 테이블
| contact_id | name | phone | email |
|------------|------|-------|-------|
| ABC-123-DEF-456-789 | 홍길동 | 010-1234-5678 | hong@example.com |

-- interactions 테이블
| id | contact_id | date | content |
|----|------------|------|---------|
| 1 | ABC-123-DEF-456-789 | 2025-01-15 | 점심 미팅. 새 프로젝트 논의 |
| 2 | ABC-123-DEF-456-789 | 2025-01-10 | 전화 통화 |
| 3 | ABC-123-DEF-456-789 | 2024-12-20 | 연말 인사 |
```

**Obsidian 노트**: 위 4.1 템플릿처럼 전체 기록 포함

## 5. 쿼리 및 분석

### 5.1 Dataview 쿼리 (Obsidian 내)

#### 연락이 뜸한 사람들 (90일 이상)
```dataview
TABLE 
  phone as "전화번호",
  last_contact as "마지막 연락",
  contact_count as "총 횟수"
FROM "07 people"
WHERE last_contact < date(today) - dur(90 days)
SORT last_contact ASC
```

#### 최근 6개월 활발한 관계
```dataview
TABLE 
  last_contact as "마지막 연락",
  last_6month_contacts as "최근 6개월",
  relationship_strength as "관계 강도"
FROM "07 people"
WHERE last_6month_contacts >= 3
SORT last_6month_contacts DESC
```

#### 카테고리별 정리
```dataview
TABLE phone, last_contact, contact_count
FROM "07 people"
WHERE category = "work"
SORT name ASC
```

### 5.2 SQLite 쿼리 (분석용)

#### 월별 연락 빈도 추이
```sql
SELECT 
    strftime('%Y-%m', date) as month,
    COUNT(*) as contact_count
FROM interactions
WHERE contact_id = '홍길동-01012345678'
GROUP BY month
ORDER BY month DESC;
```

#### 가장 활발했던 관계 TOP 10
```sql
SELECT 
    c.name,
    COUNT(*) as contacts_last_year,
    MAX(i.date) as last_contact
FROM interactions i
JOIN contacts c ON i.contact_id = c.contact_id
WHERE i.date >= date('now', '-1 year')
GROUP BY c.contact_id
ORDER BY contacts_last_year DESC
LIMIT 10;
```

#### 평균 연락 주기 분석
```sql
SELECT 
    c.name,
    c.phone,
    MAX(i.date) as last_contact,
    COUNT(*) as total_contacts,
    AVG(
        julianday(i.date) - 
        julianday(LAG(i.date) OVER (PARTITION BY c.contact_id ORDER BY i.date))
    ) as avg_interval_days
FROM contacts c
LEFT JOIN interactions i ON c.contact_id = i.contact_id
GROUP BY c.contact_id
HAVING last_contact < date('now', '-90 days')
ORDER BY total_contacts DESC;
```

#### 특정 키워드로 대화 검색
```sql
SELECT 
    c.name,
    i.date,
    i.content
FROM interactions i
JOIN contacts c ON i.contact_id = c.contact_id
WHERE i.content LIKE '%AI%' OR i.content LIKE '%프로젝트%'
ORDER BY i.date DESC;
```

### 5.3 Obsidian SQL Query 플러그인 활용

Obsidian 노트 안에서 직접 SQLite 쿼리 실행 가능:

````markdown
# 연락 히스토리 분석

```sql
SELECT 
  name,
  COUNT(*) as total,
  MAX(date) as last
FROM interactions i
JOIN contacts c ON i.contact_id = c.contact_id
GROUP BY c.contact_id
ORDER BY total DESC
LIMIT 10
```
````

## 6. 기술적 고려사항

### 5.0 contact_id 기반 매칭 전략 (UUID 사용)
- **핵심 아이디어**: Contacts 앱의 영구적인 UUID를 고유 식별자로 사용
- **장점**:
  1. **완벽한 안정성**: 이름, 전화번호, 이메일이 변경되어도 동일한 사람 추적
  2. **동명이인 완벽 구분**: macOS가 부여하는 고유 식별자
  3. **파일명 자유도**: 사용자가 파일명을 `홍길동(ABC회사).md`처럼 의미있게 변경 가능
  4. **충돌 방지**: UUID는 절대 중복되지 않음
  5. **시스템 신뢰성**: Apple이 관리하는 식별자로 가장 안정적
- **구현**:
  - Contacts Framework에서 제공하는 `identifier` 속성 사용
  - 예: `ABC-123-DEF-456-789`
  - 매 동기화마다 폴더 내 모든 `.md` 파일의 YAML에서 `contact_id` (UUID) 수집
  - Contacts UUID와 매칭

### 5.1 메모 날짜 파싱 전략
- **1차 (정규식)**: `YYMMDD` 패턴 체크 (예: `250115`)
- **2차 (간단한 자연어)**: "오늘", "어제", "today", "yesterday" 매핑
- **3차 (날짜 없음)**: Contacts의 메모 수정 시각 사용
- **4차 (Optional)**: 복잡한 자연어 표현은 Gemini Flash API 활용 가능

**파싱 예시**:
```
250115 점심 미팅    → 2025-01-15
오늘 전화 통화      → 오늘 날짜
프로젝트 관련       → Contacts 수정 시각
```

**줄바꿈 처리**:
```
입력:
251110 생일날만남
같이 카페에가서 커피 한잔하고 선물받음

251101 전화로 연락함. 요즘 많이 바쁜듯.

파싱 로직:
1. YYMMDD로 시작하는 줄 → 새 interaction 시작
2. 날짜 없는 줄 → 이전 interaction에 줄바꿈(\n)으로 추가
3. 빈 줄 → 무시

결과:
- date: 2025-11-10, content: "생일날만남\n같이 카페에가서 커피 한잔하고 선물받음"
- date: 2025-11-01, content: "전화로 연락함. 요즘 많이 바쁜듯."
```

### 5.2 SQLite 설계 원칙
- **정규화**: contacts와 interactions 분리로 중복 최소화
- **인덱스**: 자주 쿼리하는 필드에 인덱스 생성
- **UNIQUE 제약**: `UNIQUE(contact_id, date)` - 같은 날짜는 하나만 유지
- **덮어쓰기 전략**: 
  ```python
  # 같은 날짜 기존 데이터 삭제 후 새로 INSERT
  DELETE FROM interactions WHERE contact_id = ? AND date = ?;
  INSERT INTO interactions (contact_id, date, content) VALUES (?, ?, ?);
  ```
- **트랜잭션**: 동기화 시 원자성 보장
- **백업**: 단일 파일이라 백업 간단

### 5.3 한글 이름 처리
- **이슈**: iPhone에서 입력한 한글 이름이 macOS Contacts에서 정확히 표시되는지 확인 필요
- **해결**:
  - iCloud 동기화 활용 (iPhone → iCloud → Mac)
  - macOS Contacts 앱에서 직접 확인 후 개발 시작
  - UTF-8 인코딩 강제 적용
  - 테스트: 실제 iPhone에서 한글 이름 입력 후 Mac에서 확인

### 5.2 Contacts 데이터 접근 방법
- **권장**: Python + PyObjC (Contacts Framework)
  - macOS의 네이티브 Contacts 프레임워크 직접 접근
  - 한글 처리 안정적
  - 성능 우수
  - 권한 설정 필요 (최초 1회)

- **대안**: AppleScript
  - 간단하지만 성능 이슈 가능
  - 대량 연락처 시 느릴 수 있음

### 5.3 파일 업데이트 전략
- **contact_id 기반 매칭**:
  1. Contacts에서 연락처 읽기 → `contact_id` 생성
  2. `07 people` 폴더의 모든 `.md` 파일 스캔
  3. 각 파일의 YAML frontmatter에서 `contact_id` 추출
  4. 매칭되는 `contact_id` 찾으면 해당 파일 업데이트
  5. 없으면 새 파일 생성 (파일명: `{이름}.md`)

- **스마트 머지 방식**:
  - YAML frontmatter: Contacts 데이터로 전체 업데이트
  - 기본 정보 섹션: Contacts 데이터로 전체 업데이트
  - 활동 기록 섹션: 
    - Contacts 메모에서 파싱한 내용 추가
    - 기존 수동 작성 내용 보존
    - 중복 방지 로직 적용
  - 기타 섹션: 수동 작성 내용 완전 보존

### 5.4 충돌 해결
- Obsidian에서 수동으로 추가한 섹션은 절대 삭제하지 않음
- "## 활동 기록" 섹션만 업데이트
- 날짜 기반 중복 체크로 동일 날짜 기록 중복 방지

## 7. 실행 계획

### Phase 1: 환경 확인 및 프로토타입 (2-3일)
- [ ] iPhone에서 한글 이름 입력 → Mac Contacts 동기화 테스트
- [ ] Python 환경 설정 (PyObjC, sqlite3)
- [ ] Contacts Framework 접근 테스트
- [ ] 샘플 연락처로 단일 노트 생성 테스트

### Phase 2: 기본 동기화 개발 (1주)
- [ ] Contacts 데이터 읽기 스크립트 개발
- [ ] 이름, 전화번호, 이메일 추출 로직
- [ ] Contacts UUID 추출 및 `contact_id`로 사용
- [ ] 메모 파싱 (정규식 + 자연어 날짜)
- [ ] SQLite 데이터베이스 생성 및 스키마 설정
- [ ] interactions 저장 로직
- [ ] 통계 계산 로직 (contact_count 등)

### Phase 3: Obsidian 노트 생성 (1주)
- [ ] `07 people` 폴더 스캔 및 YAML 파싱
- [ ] UUID 기반 매칭 로직
- [ ] Obsidian 노트 생성 (YAML + 전체 활동 기록)
- [ ] 스마트 머지 로직 (수동 섹션 보존)
- [ ] 수동 실행 스크립트 완성

### Phase 4: Dataview 쿼리 템플릿 (2-3일)
- [ ] 연락이 뜸한 사람 쿼리
- [ ] 최근 활발한 관계 쿼리
- [ ] 카테고리별 정리 쿼리
- [ ] 대시보드 노트 템플릿 작성

### Phase 5: 자동화 및 안정화 (2-3일)
- [ ] LaunchAgent 설정 (하루 1회, 새벽 2시)
- [ ] 로깅 시스템 구축
- [ ] 에러 처리 및 예외 상황 대응
- [ ] SQLite 백업 메커니즘

### Phase 6: 테스트 및 배포 (2-3일)
- [ ] 실제 연락처로 전체 동기화 테스트
- [ ] 한글/영문 이름 혼합 테스트
- [ ] SQLite 쿼리 성능 테스트
- [ ] Dataview 쿼리 동작 확인
- [ ] 사용자 가이드 작성

### Phase 7: 고급 분석 (선택적)
- [ ] SQLite 분석 스크립트 개발
- [ ] Python 시각화 도구
- [ ] Obsidian SQL Query 플러그인 연동

## 8. 성공 지표
- iPhone에서 입력한 한글 이름이 Mac에서 정확히 동기화됨
- Contacts의 모든 연락처가 Obsidian에 정확히 반영됨
- SQLite에 모든 interaction이 정확히 저장됨
- 기존 수동 작성 내용(특이사항 등)이 손실되지 않음
- 안정적인 주기적 동기화 작동 (에러율 < 1%)
- Dataview 쿼리로 다양한 관점의 인맥 정보 조회 가능
- SQLite 쿼리로 정량적 분석 가능
- 벡터DB 자동 업데이트로 인맥 정보 즉시 검색 가능

## 8. 위험 요소 및 대응

### 위험 1: iPhone 한글 이름 동기화 문제
- **확률**: 중간
- **영향**: 높음 (핵심 기능 불가)
- **대응**: 
  - Phase 1에서 사전 확인
  - 문제 발견 시 iCloud 설정 조정 또는 대안 검토
  - 최악의 경우 영문 transliteration 활용

### 위험 2: 데이터 손실
- **확률**: 낮음
- **영향**: 높음
- **대응**: 
  - 첫 실행 시 전체 백업
  - 스마트 머지 로직으로 기존 내용 보존
  - 수동 확인 단계 포함

### 위험 3: 인코딩 이슈
- **확률**: 낮음
- **영향**: 중간
- **대응**: 
  - UTF-8 강제 적용
  - 특수문자 처리 로직

### 위험 4: 연락처 정보 변경
- **확률**: 중간
- **영향**: 없음 (UUID 사용으로 해결)
- **대응**: 
  - UUID는 절대 변경되지 않으므로 전화번호, 이메일, 이름이 바뀌어도 추적 가능
  - 정보 변경 시 SQLite와 Obsidian에서 자동 업데이트

### 위험 5: 같은 날짜 내용 수정 시 중복
- **확률**: 높음
- **영향**: 낮음 (덮어쓰기 전략으로 해결)
- **대응**:
  - 같은 날짜는 최신 내용으로 덮어쓰기
  - 수정 이력은 보존하지 않음 (실제로 필요하지 않음)
  - 같은 날 여러 번 만난 경우는 드물고, 필요시 내용에 "점심/저녁" 등으로 구분

## 9. 추가 검토사항

### 9.1 Contacts 삭제된 연락처 처리
- **권장**: Obsidian 노트는 유지
- **이유**: 과거 기록 보존 가치
- **표시**: frontmatter에 `archived: true` 추가 (향후 기능)

### 9.2 기존 '07 people' 폴더 노트
- **확인**: 기존 수동 작성 노트 존재 여부
- **전략**: 
  - 동일 이름 파일 있으면 스마트 머지
  - 기존 내용 최대한 보존
  - 필요시 수동 통합 가이드 제공

### 9.3 파일명 규칙
- **기본**: `{이름}.md` (신규 생성 시)
- **사용자 수정**: 자유롭게 변경 가능 (예: `홍길동(ABC회사).md`, `John(친구).md`)
- **동명이인**: 파일명 중복 가능 (UUID로 구분)
- **시스템 매칭**: 파일명과 무관하게 UUID로만 추적
- **연락처 정보 변경**: 전화번호나 이름이 바뀌어도 UUID로 동일 인물 추적

## 11. 개발 환경

### 필요 도구
- Python 3.8+
- PyObjC (Contacts Framework 접근)
- sqlite3 (Python 내장)
- macOS Catalina 이상 (Contacts 권한 시스템)

### Python 패키지
```
pyobjc-framework-Contacts
python-dateutil  # 날짜 파싱
pyyaml           # YAML 처리
```

### 디렉토리 구조
```
contacts-obsidian-sync/
├── sync.py                 # 메인 동기화 스크립트
├── contacts_reader.py      # Contacts 데이터 읽기
├── memo_parser.py          # 메모 파싱 로직 (날짜 인식)
├── db_manager.py           # SQLite 관리
├── obsidian_writer.py      # Obsidian 노트 생성/업데이트
├── stats_calculator.py     # 통계 계산
├── config.py               # 설정 (경로, 주기 등)
├── requirements.txt        # Python 패키지
├── schema.sql              # SQLite 스키마
├── dataview_queries/       # Dataview 쿼리 템플릿
│   ├── recent_contacts.md
│   ├── need_followup.md
│   └── dashboard.md
└── README.md               # 사용자 가이드
```

### SQLite 데이터베이스
- **경로**: `~/Desktop/SecondBrain/07 people/.contacts.db`
- **숨김 파일**: `.`으로 시작하여 Obsidian 파일 목록에 나타나지 않음
- **백업**: 자동 백업 스크립트 포함
- **마이그레이션**: 스키마 버전 관리

## 12. 다음 단계

1. **즉시**: iPhone에서 테스트 연락처 생성 (한글 이름) → Mac 동기화 확인
2. **승인 후**: Phase 1 환경 설정 및 프로토타입 개발 시작
3. **1-2주차**: Contacts 읽기 + SQLite 저장 + Obsidian 노트 생성
4. **3주차**: Dataview 쿼리 템플릿 + 자동화
5. **4주차**: 실제 데이터로 테스트 및 배포
6. **지속적**: 고급 분석 기능 추가 (선택적)

---

**작성일**: 2025-01-10  
**버전**: 2.2  
**상태**: PRD 최종 완성 - 하이브리드 아키텍처 (Obsidian + SQLite + Dataview)  
**주요 변경사항**:
- **v2.2**: 같은 날짜 덮어쓰기 전략 채택 (중복 방지)
- **v2.1**: contact_id를 Contacts UUID로 변경 (전화번호/이메일 변경 대응)
- **v2.0**: SQLite 데이터베이스 추가 (raw data 저장 및 분석)
- 전체 활동 기록을 Obsidian 노트에 포함
- 줄바꿈 파싱 로직 추가
- 수동 편집 섹션 명확화 (내 메모, 관계 히스토리, 특이사항)
- 동기화 주기: 하루 1회 (새벽 2시)
- Dataview 쿼리 템플릿 추가
- 역할 분리: Obsidian (정성적 PKM) + SQLite (정량적 분석)