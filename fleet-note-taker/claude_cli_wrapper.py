import subprocess
import json
import os
import shutil
from PIL import Image

class ClaudeCliWrapper:
    """Claude Code CLI를 subprocess로 호출하여 이미지 분석"""

    def __init__(self, claude_cli_path=None):
        """
        Args:
            claude_cli_path: claude CLI 실행 파일 경로 (None이면 자동 탐지)
        """
        if claude_cli_path is None:
            # claude 명령어 경로 자동 탐지
            self.claude_cli_path = shutil.which('claude')
            if self.claude_cli_path is None:
                raise RuntimeError(
                    "claude CLI를 찾을 수 없습니다. "
                    "Claude Code가 설치되어 있는지 확인해주세요."
                )
        else:
            self.claude_cli_path = claude_cli_path

        print(f"Claude CLI 경로: {self.claude_cli_path}")

    def analyze_image(self, image_path, max_retries=3):
        """
        이미지를 Claude CLI로 분석

        Args:
            image_path: 분석할 이미지 파일 경로
            max_retries: 최대 재시도 횟수

        Returns:
            dict: 분석 결과 {'title': ..., 'notes': ..., 'date': ..., 'tags': [...]}
            None: 분석 실패
        """
        # 이미지 파일 존재 확인
        if not os.path.exists(image_path):
            print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            return None

        # 이미지 유효성 확인
        try:
            img = Image.open(image_path)
            img.verify()
        except Exception as e:
            print(f"이미지 파일이 손상되었습니다: {e}")
            return None

        # 프롬프트 생성
        prompt = self._create_prompt(image_path)

        # 재시도 로직
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"  - 재시도 {attempt}/{max_retries}...")

                result = self._call_claude_cli(prompt, image_path)

                if result and self._validate_result(result):
                    return result
                elif attempt < max_retries - 1:
                    print(f"  - AI 응답 품질 부족, 재시도 예정...")
                    continue
                else:
                    print(f"  - 최대 재시도 횟수 도달, 현재 결과 반환")
                    return result

            except Exception as e:
                print(f"  - Claude CLI 호출 오류: {e}")
                if attempt < max_retries - 1:
                    continue
                return None

        return None

    def _call_claude_cli(self, prompt, image_path):
        """
        Claude CLI를 subprocess로 호출

        Args:
            prompt: 분석 프롬프트
            image_path: 이미지 파일 경로

        Returns:
            dict: 파싱된 응답
        """
        # 절대 경로로 변환
        abs_image_path = os.path.abspath(image_path)

        # Claude CLI에게 Read 도구로 이미지를 읽고 분석하도록 요청
        full_prompt = f"Read 도구를 사용해서 '{abs_image_path}' 이미지 파일을 읽고 다음 지시사항을 따라주세요:\n\n{prompt}"

        try:
            # claude -p 명령어 실행
            # -p: print 모드 (비대화형 출력)
            # --dangerously-skip-permissions: 권한 확인 스킵
            result = subprocess.run(
                [
                    'claude',
                    '-p',
                    '--dangerously-skip-permissions',
                    full_prompt
                ],
                capture_output=True,
                text=True,
                timeout=60  # 60초 타임아웃
            )

            if result.returncode != 0:
                print(f"  - Claude CLI 실행 실패 (exit code: {result.returncode})")
                print(f"  - stderr: {result.stderr}")
                return None

            # 응답 파싱
            response_text = result.stdout.strip()

            if not response_text:
                print("  - Claude CLI 응답이 비어있습니다.")
                return None

            # 응답 파싱
            return self._parse_response(response_text)

        except subprocess.TimeoutExpired:
            print("  - Claude CLI 실행 타임아웃 (60초)")
            return None
        except Exception as e:
            print(f"  - subprocess 실행 오류: {e}")
            return None

    def _create_prompt(self, image_path):
        """이미지 분석 프롬프트 생성"""
        return """
이 손글씨 메모 이미지를 분석해주세요. 다음 형식으로 응답해주세요:

제목: [첫 번째 줄 내용을 그대로 사용]

내용: [두 번째 줄부터 모든 내용을 정리 (원본 텍스트 최대한 유지)]

날짜: [메모에서 날짜 정보 추출 (예: 250815, 250818 등). 날짜를 파악할 수 없으면 오늘 날짜를 사용하세요]

태그: [이미지 맨 아래에 수기로 작성된 #태그들을 우선 추출하세요. 태그가 없다면 노트 내용을 바탕으로 한글 태그 5개를 생성하세요. 태그는 # 기호 없이 단어만 쉼표로 구분하여 작성하세요 (예: 육아, 자녀교육, 관계)]

태그 생성 가이드 (수기 태그가 없는 경우만):
- 자기계발 관련: 학습, 성장, 습관, 목표, 동기부여 등
- 방법론 관련: 전략, 기법, 도구, 프로세스, 시스템 등
- 주제별: 업무, 개인, 공부, 회의, 아이디어 등
- 우선순위: 긴급, 중요, 보통 등

한글로 자연스럽게 작성하고, 메모의 핵심 내용을 놓치지 마세요.
"""

    def _parse_response(self, response_text):
        """Claude 응답 파싱"""
        try:
            lines = response_text.strip().split('\n')
            title = '메모'
            notes = ''
            date = ''
            tags = ['메모']

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # ** 마크다운 볼드 제거
                line = line.replace('**', '')

                if line.startswith('제목:'):
                    title = line.replace('제목:', '').strip()
                elif line.startswith('내용:'):
                    # 내용은 다음 줄부터 날짜 전까지 모두 포함
                    notes_lines = []
                    i += 1
                    while i < len(lines):
                        current_line = lines[i].strip().replace('**', '')
                        # 날짜나 태그가 나오면 중단
                        if current_line.startswith('날짜:') or current_line.startswith('태그:'):
                            i -= 1  # 한 줄 뒤로
                            break
                        if current_line and current_line != '---':  # 빈 줄이나 구분선이 아닌 경우만
                            notes_lines.append(current_line)
                        i += 1
                    notes = '\n'.join(notes_lines)
                    continue
                elif line.startswith('날짜:'):
                    date = line.replace('날짜:', '').strip()
                elif line.startswith('태그:'):
                    tags_text = line.replace('태그:', '').strip()
                    tags_text = tags_text.strip('[]')
                    tags = [tag.strip().lstrip('#') for tag in tags_text.split(',') if tag.strip()]

                i += 1

            # 기본값 처리
            if not title or title == '[첫 번째 줄 내용을 그대로 사용]':
                title = '메모'

            if not notes or notes == '[두 번째 줄부터 모든 내용을 정리 (원본 텍스트 최대한 유지)]':
                notes = '내용 분석 중...'

            if not tags or tags == ['[노트 내용을 바탕으로 한글 태그 5개]']:
                tags = ['메모', '자기계발', '방법론']

            return {
                'title': title,
                'notes': notes,
                'date': date,
                'tags': tags
            }

        except Exception as e:
            print(f"  - 응답 파싱 오류: {e}")
            return {
                'title': '메모',
                'notes': '파싱 오류로 인한 기본 내용',
                'tags': ['메모']
            }

    def _validate_result(self, result):
        """결과 유효성 검증"""
        if not result:
            return False

        # 필수 필드 확인
        if 'notes' not in result or 'title' not in result:
            return False

        # 내용 품질 확인
        notes = result.get('notes', '')
        if '내용 분석 중' in notes or '파싱 오류' in notes:
            return False

        return True
