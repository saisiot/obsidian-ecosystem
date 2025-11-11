#!/usr/bin/env python3
"""
Contacts 앱 권한 확인 및 요청
"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_contacts_permission():
    """Contacts 접근 권한 확인 및 요청"""
    try:
        from Contacts import CNContactStore
        from Foundation import NSError

        store = CNContactStore.alloc().init()

        print("=" * 60)
        print("Contacts 앱 권한 확인")
        print("=" * 60)

        # 권한 상태 확인
        from Contacts import CNAuthorizationStatusNotDetermined, CNAuthorizationStatusRestricted, CNAuthorizationStatusDenied, CNAuthorizationStatusAuthorized

        auth_status = CNContactStore.authorizationStatusForEntityType_(0)  # 0 = CNEntityTypeContacts

        status_names = {
            0: "NotDetermined (아직 결정 안됨)",
            1: "Restricted (제한됨)",
            2: "Denied (거부됨)",
            3: "Authorized (승인됨)"
        }

        print(f"\n현재 권한 상태: {status_names.get(auth_status, '알 수 없음')} ({auth_status})")

        if auth_status == 3:  # Authorized
            print("✅ Contacts 접근 권한이 이미 허용되었습니다!")
            return True

        if auth_status == 2:  # Denied
            print("❌ Contacts 접근 권한이 거부되었습니다.")
            print("\n해결 방법:")
            print("1. 시스템 설정 > 개인 정보 보호 및 보안 > 연락처")
            print("2. Python 또는 터미널 앱의 권한 활성화")
            return False

        if auth_status == 1:  # Restricted
            print("⚠️  Contacts 접근이 제한되었습니다 (관리자 정책)")
            return False

        # 권한 요청 (NotDetermined)
        print("\n🔔 Contacts 접근 권한을 요청합니다...")
        print("(팝업이 나타나면 '확인'을 눌러주세요)")

        # 동기 방식으로 권한 요청
        error = None
        granted = [False]  # 리스트로 감싸서 클로저에서 수정 가능하게

        def completion_handler(granted_val, err):
            granted[0] = granted_val
            if err:
                print(f"❌ 에러 발생: {err}")

        store.requestAccessForEntityType_completionHandler_(0, completion_handler)

        # 잠시 대기 (권한 팝업이 나타날 시간)
        import time
        time.sleep(2)

        if granted[0]:
            print("✅ 권한이 승인되었습니다!")
            return True
        else:
            print("❌ 권한이 거부되었습니다.")
            return False

    except ImportError as e:
        print(f"❌ PyObjC Contacts 프레임워크를 불러올 수 없습니다: {e}")
        print("\n해결 방법:")
        print("pip install pyobjc-framework-Contacts")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_read_contacts():
    """실제로 연락처 읽기 시도"""
    from src.contacts_reader import ContactsReader

    print("\n" + "=" * 60)
    print("연락처 읽기 시도")
    print("=" * 60)

    reader = ContactsReader()
    contacts = reader.read_all_contacts()

    print(f"\n📊 결과: {len(contacts)}개의 연락처")

    if len(contacts) > 0:
        print("\n처음 3개 연락처:")
        for i, contact in enumerate(contacts[:3], 1):
            print(f"\n[{i}] {contact['name']}")
            print(f"    ID: {contact['contact_id'][:20]}...")
            if contact['phone']:
                print(f"    전화: {contact['phone']}")
            if contact['email']:
                print(f"    이메일: {contact['email']}")
            if contact['notes']:
                preview = contact['notes'][:30] + "..." if len(contact['notes']) > 30 else contact['notes']
                print(f"    메모: {preview}")
    else:
        print("\n⚠️  연락처가 없습니다.")
        print("\n확인 사항:")
        print("1. macOS Contacts 앱을 열어서 연락처가 있는지 확인")
        print("2. iCloud 동기화가 켜져 있는지 확인")
        print("3. 테스트용 연락처를 추가해보세요")

    return contacts

if __name__ == '__main__':
    # 권한 확인
    has_permission = check_contacts_permission()

    if has_permission:
        # 연락처 읽기
        contacts = test_read_contacts()
    else:
        print("\n" + "=" * 60)
        print("⚠️  권한을 먼저 허용해야 연락처를 읽을 수 있습니다.")
        print("=" * 60)
