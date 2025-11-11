# 알려진 이슈 (Known Issues)

## 1. macOS Contacts 접근 권한 문제

### 문제
- Python 스크립트가 macOS Contacts 앱에 접근할 때 권한이 거부됨
- 권한 팝업이 제대로 나타나지 않음
- TCC (Transparency, Consent, and Control) 시스템의 제약

### 증상
```
Error Domain=CNErrorDomain Code=100 "Access Denied"
UserInfo={NSLocalizedDescription=Access Denied,
NSLocalizedFailureReason=This application has not been granted permission to access Contacts.}
```

### 원인
macOS는 보안상의 이유로 **앱 번들** 형태로 실행되는 프로그램만 Contacts 접근 권한 팝업을 표시합니다. Python 스크립트는 일반적으로 앱 번들이 아니므로 권한 팝업이 나타나지 않습니다.

### 해결 방법

#### 방법 1: 개발 환경 (임시)
터미널 앱에 **Full Disk Access** 권한 부여
1. 시스템 설정 > 개인 정보 보호 및 보안 > Full Disk Access
2. 터미널 앱 추가 및 활성화
3. 터미널 재시작

**주의**: 이 방법은 개발/테스트 용도로만 사용

#### 방법 2: 프로덕션 환경
Python 스크립트를 macOS **앱 번들**로 패키징
- `py2app` 또는 `PyInstaller` 사용
- Info.plist에 `NSContactsUsageDescription` 추가
- 코드 서명 및 공증 (Notarization)

예제:
```xml
<!-- Info.plist -->
<key>NSContactsUsageDescription</key>
<string>인맥 관리를 위해 연락처 접근이 필요합니다.</string>
```

#### 방법 3: LaunchAgent 사용
- LaunchAgent로 백그라운드 실행
- Python 실행 파일에 직접 권한 부여 필요

### 테스트 전략
**현재 (개발 단계)**:
- ✅ 단위 테스트로 모든 기능 검증
- ✅ Mock 데이터로 로직 테스트
- ⚠️ 실제 Contacts 데이터는 권한 문제로 접근 불가

**향후 (배포 단계)**:
- 앱 번들로 패키징 후 E2E 테스트
- 실제 iPhone/iCloud 연락처로 통합 테스트

### 관련 파일
- `test_contacts_permission.py` - 권한 확인 스크립트
- `src/contacts_reader.py` - Contacts 읽기 구현

### 상태
- [x] 문제 확인
- [x] 원인 파악
- [ ] 프로덕션 해결 방법 구현 (앱 번들 패키징)
- [ ] 실제 데이터로 E2E 테스트

### 참고 자료
- [Apple TCC Documentation](https://developer.apple.com/documentation/bundleresources/information_property_list/nscontactsusagedescription)
- [py2app Documentation](https://py2app.readthedocs.io/)

---

## 2. (향후 이슈는 여기에 추가)

