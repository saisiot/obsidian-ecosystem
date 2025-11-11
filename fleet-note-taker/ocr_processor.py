import re
from config import Config
from claude_cli_wrapper import ClaudeCliWrapper

class OCRProcessor:
    """Claude Code CLI를 사용한 이미지 분석 프로세서"""

    def __init__(self):
        """Claude CLI Wrapper 초기화"""
        self.claude_wrapper = ClaudeCliWrapper(claude_cli_path=Config.CLAUDE_CLI_PATH)

    def extract_text_and_analyze(self, image_path, max_retries=3):
        """
        이미지에서 텍스트 추출 및 분석

        Args:
            image_path: 분석할 이미지 경로
            max_retries: 최대 재시도 횟수

        Returns:
            dict: 분석 결과 {'title': ..., 'notes': ..., 'date': ..., 'tags': [...]}
            None: 분석 실패
        """
        result = self.claude_wrapper.analyze_image(image_path, max_retries=max_retries)

        if not result:
            return None

        # 제목 정제 (파일명으로 사용 가능하도록)
        if 'title' in result:
            result['title'] = self._clean_title(result['title'])

        return result

    def _clean_title(self, title):
        """제목 정제 (파일명에 사용 불가능한 문자 제거)"""
        # 연속된 공백을 언더스코어로 변경
        title = re.sub(r'\s+', '_', title)

        # 길이 제한
        if len(title) > Config.MAX_TITLE_LENGTH:
            title = title[:Config.MAX_TITLE_LENGTH]

        # macOS/Obsidian 호환성을 위한 문자 정제
        title = self._clean_for_macos_obsidian(title)

        return title.strip('_')  # 앞뒤 언더스코어 제거

    def _clean_for_macos_obsidian(self, title):
        """macOS와 Obsidian 호환성을 위한 문자 정제"""
        # macOS에서 문제가 되는 문자들 제거
        # - 쉼표, 세미콜론, 콜론, 느낌표, 물음표
        # - 대괄호, 중괄호, 괄호
        # - 앰퍼샌드, 백슬래시, 슬래시
        # - 따옴표 (작은따옴표, 큰따옴표)
        title = re.sub(r'[,;:!?\[\]{}()&\\/\'"]', '', title)

        # 연속된 언더스코어를 하나로 정리
        title = re.sub(r'_+', '_', title)

        # 앞뒤 공백 및 특수문자 제거
        title = title.strip(' _-')

        return title
