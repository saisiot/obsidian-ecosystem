"""
AppleScript를 통한 Contacts 읽기
권한 문제를 우회하는 대체 방법
"""
import subprocess
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ContactsReaderAppleScript:
    """AppleScript를 사용하여 Contacts 앱에서 연락처 읽기"""

    def read_all_contacts(self) -> List[Dict[str, Optional[str]]]:
        """
        모든 연락처 읽기 (AppleScript 사용)

        Returns:
            연락처 딕셔너리 리스트
            각 연락처는 다음 키를 포함:
            - contact_id: 고유 ID (AppleScript에서는 id 사용)
            - name: 이름
            - phone: 전화번호 (첫 번째)
            - email: 이메일 (첫 번째)
            - notes: 메모
        """
        logger.info("AppleScript를 통해 연락처 읽기 시작...")

        # AppleScript: 모든 연락처 정보를 JSON으로 반환
        applescript = '''
        use framework "Foundation"
        use scripting additions

        set contactsList to {}

        tell application "Contacts"
            set allPeople to every person

            repeat with aPerson in allPeople
                try
                    set personId to id of aPerson
                    set personName to name of aPerson

                    -- 전화번호 (첫 번째)
                    set personPhone to ""
                    try
                        set phoneNumbers to phones of aPerson
                        if (count of phoneNumbers) > 0 then
                            set personPhone to value of item 1 of phoneNumbers
                        end if
                    end try

                    -- 이메일 (첫 번째)
                    set personEmail to ""
                    try
                        set emailAddresses to emails of aPerson
                        if (count of emailAddresses) > 0 then
                            set personEmail to value of item 1 of emailAddresses
                        end if
                    end try

                    -- 메모
                    set personNotes to ""
                    try
                        set personNotes to note of aPerson
                    end try

                    -- JSON 형식으로 추가
                    set contactInfo to {personId:personId, personName:personName, personPhone:personPhone, personEmail:personEmail, personNotes:personNotes}
                    set end of contactsList to contactInfo
                end try
            end repeat
        end tell

        -- JSON 변환
        set jsonString to ""
        set jsonString to jsonString & "["
        set firstItem to true

        repeat with aContact in contactsList
            if not firstItem then
                set jsonString to jsonString & ","
            end if
            set firstItem to false

            set jsonString to jsonString & "{"
            set jsonString to jsonString & "\\"contact_id\\":\\"" & (personId of aContact) & "\\","
            set jsonString to jsonString & "\\"name\\":\\"" & my escapeJSON(personName of aContact) & "\\","
            set jsonString to jsonString & "\\"phone\\":\\"" & my escapeJSON(personPhone of aContact) & "\\","
            set jsonString to jsonString & "\\"email\\":\\"" & my escapeJSON(personEmail of aContact) & "\\","
            set jsonString to jsonString & "\\"notes\\":\\"" & my escapeJSON(personNotes of aContact) & "\\""
            set jsonString to jsonString & "}"
        end repeat

        set jsonString to jsonString & "]"
        return jsonString

        on escapeJSON(txt)
            if txt is missing value or txt is "" then
                return ""
            end if
            set txt to txt as text
            -- 간단한 이스케이프 (백슬래시, 따옴표, 개행)
            set AppleScript's text item delimiters to "\\\\"
            set txt to text items of txt
            set AppleScript's text item delimiters to "\\\\\\\\"
            set txt to txt as text

            set AppleScript's text item delimiters to "\\""
            set txt to text items of txt
            set AppleScript's text item delimiters to "\\\\\\""
            set txt to txt as text

            set AppleScript's text item delimiters to return
            set txt to text items of txt
            set AppleScript's text item delimiters to "\\\\n"
            set txt to txt as text

            set AppleScript's text item delimiters to ""
            return txt
        end escapeJSON
        '''

        try:
            # AppleScript 실행
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=60  # 연락처가 많으면 시간이 걸릴 수 있음
            )

            if result.returncode != 0:
                logger.error(f"AppleScript 실행 실패: {result.stderr}")
                return []

            # JSON 파싱
            json_output = result.stdout.strip()

            if not json_output or json_output == "[]":
                logger.warning("연락처가 없습니다.")
                return []

            contacts = json.loads(json_output)

            # 빈 값 처리
            for contact in contacts:
                for key in ['phone', 'email', 'notes']:
                    if contact.get(key) == "":
                        contact[key] = None

            logger.info(f"{len(contacts)}개의 연락처를 읽었습니다 (AppleScript)")
            return contacts

        except subprocess.TimeoutExpired:
            logger.error("AppleScript 실행 시간 초과")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.debug(f"출력: {result.stdout[:500]}")
            return []
        except Exception as e:
            logger.error(f"연락처 읽기 실패: {e}")
            return []
