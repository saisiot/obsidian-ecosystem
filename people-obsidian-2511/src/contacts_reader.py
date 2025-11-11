"""
macOS Contacts 데이터 읽기
TDD REFACTOR 단계: 실제 Contacts Framework 구현
"""
from typing import List, Dict, Optional
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


class ContactsReader:
    """macOS Contacts 앱에서 연락처 데이터를 읽는 클래스"""

    def __init__(self):
        """ContactsReader 초기화"""
        # PyObjC가 설치되어 있으면 사용
        try:
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

            self.store = CNContactStore.alloc().init()
            self.keys_to_fetch = [
                CNContactIdentifierKey,
                CNContactGivenNameKey,
                CNContactFamilyNameKey,
                CNContactPhoneNumbersKey,
                CNContactEmailAddressesKey,
                CNContactNoteKey
            ]
            self.has_contacts_framework = True
            logger.info("Contacts Framework 초기화 완료")

        except ImportError as e:
            logger.warning(f"PyObjC Contacts 프레임워크를 불러올 수 없습니다: {e}")
            self.store = None
            self.keys_to_fetch = []
            self.has_contacts_framework = False

    def read_all_contacts(self) -> List[Dict[str, Optional[str]]]:
        """
        모든 연락처를 읽어 딕셔너리 리스트로 반환

        Returns:
            List[Dict]: 연락처 정보 리스트
                - contact_id: UUID (필수)
                - name: 전체 이름 (필수)
                - phone: 전화번호 (선택)
                - email: 이메일 (선택)
                - notes: 메모 (선택)
        """
        if not self.has_contacts_framework or not self.store:
            logger.warning("Contacts Framework가 없어 빈 리스트 반환")
            return []

        try:
            from Contacts import CNContactFetchRequest

            contacts = []
            fetch_request = CNContactFetchRequest.alloc().initWithKeysToFetch_(
                self.keys_to_fetch
            )

            error = None

            def handler(cn_contact, stop):
                """연락처 하나씩 처리하는 핸들러"""
                try:
                    contact_data = self._extract_contact_data(cn_contact)
                    contacts.append(contact_data)
                except Exception as e:
                    logger.error(f"연락처 추출 실패: {e}")
                return True

            # Contacts 앱에서 모든 연락처 가져오기
            success = self.store.enumerateContactsWithFetchRequest_error_usingBlock_(
                fetch_request, error, handler
            )

            if not success:
                logger.error(f"연락처 읽기 실패: {error}")
                return []

            logger.info(f"{len(contacts)}개의 연락처를 읽었습니다")
            return contacts

        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return []

    def _extract_contact_data(self, cn_contact) -> Dict[str, Optional[str]]:
        """
        CNContact 객체에서 필요한 데이터 추출

        Args:
            cn_contact: CNContact 객체

        Returns:
            Dict: 연락처 정보 딕셔너리
        """
        # 이름 조합 (Last Name + First Name)
        first_name = cn_contact.givenName() or ''
        last_name = cn_contact.familyName() or ''

        # 한글 이름: 성+이름 (예: 홍길동)
        # 영문 이름: First Last (예: John Doe)
        if last_name:
            # 성이 있으면 한글로 간주 (성+이름)
            full_name = f"{last_name}{first_name}".strip()
        else:
            # 성이 없으면 영문으로 간주 (이름만)
            full_name = first_name

        # 전화번호 (첫 번째 것만)
        phone = None
        if cn_contact.phoneNumbers():
            phone_number = cn_contact.phoneNumbers()[0].value()
            phone = phone_number.stringValue()

        # 이메일 (첫 번째 것만)
        email = None
        if cn_contact.emailAddresses():
            email = str(cn_contact.emailAddresses()[0].value())

        # 메모
        notes = cn_contact.note() or ''

        return {
            'contact_id': cn_contact.identifier(),
            'name': full_name,
            'phone': phone,
            'email': email,
            'notes': notes
        }
