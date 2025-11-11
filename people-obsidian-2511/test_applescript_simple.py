#!/usr/bin/env python3
"""
간단한 AppleScript 테스트
"""
import subprocess

# 처음 3명의 연락처만 가져오기
applescript = '''
tell application "Contacts"
    set output to ""
    set peopleList to people 1 thru 3

    repeat with aPerson in peopleList
        set output to output & "ID: " & (id of aPerson) & "\\n"
        set output to output & "Name: " & (name of aPerson) & "\\n"

        try
            set phoneNum to value of phone 1 of aPerson
            set output to output & "Phone: " & phoneNum & "\\n"
        on error
            set output to output & "Phone: (none)\\n"
        end try

        try
            set emailAddr to value of email 1 of aPerson
            set output to output & "Email: " & emailAddr & "\\n"
        on error
            set output to output & "Email: (none)\\n"
        end try

        try
            set personNote to note of aPerson
            if personNote is not missing value then
                set output to output & "Note: " & personNote & "\\n"
            else
                set output to output & "Note: (none)\\n"
            end if
        on error
            set output to output & "Note: (none)\\n"
        end try

        set output to output & "---\\n"
    end repeat

    return output
end tell
'''

result = subprocess.run(
    ['osascript', '-e', applescript],
    capture_output=True,
    text=True,
    timeout=30
)

print("=== AppleScript 테스트 결과 ===\n")
print(result.stdout)

if result.returncode != 0:
    print(f"\n❌ 에러: {result.stderr}")
