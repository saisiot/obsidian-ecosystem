#!/usr/bin/env python3
"""
AppleScript를 통해 연락처 확인
"""
import subprocess
import json

# AppleScript로 연락처 개수 확인
applescript = '''
tell application "Contacts"
    return count of people
end tell
'''

try:
    result = subprocess.run(
        ['osascript', '-e', applescript],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0:
        count = result.stdout.strip()
        print(f"✅ AppleScript로 확인한 연락처 개수: {count}개")

        if int(count) == 0:
            print("\n⚠️  Contacts 앱에 연락처가 없습니다.")
            print("확인 사항:")
            print("1. Contacts 앱을 열어서 연락처가 있는지 확인하세요")
            print("2. iCloud 동기화가 켜져 있는지 확인하세요")
        else:
            print(f"\n📱 {count}개의 연락처가 있습니다!")
            print("AppleScript를 통해 읽어올 수 있습니다.")
    else:
        print(f"❌ 에러: {result.stderr}")
        print("\n가능한 원인:")
        print("1. Contacts 앱이 실행되지 않음")
        print("2. AppleScript 권한 필요")

except subprocess.TimeoutExpired:
    print("❌ 시간 초과")
except Exception as e:
    print(f"❌ 오류: {e}")
