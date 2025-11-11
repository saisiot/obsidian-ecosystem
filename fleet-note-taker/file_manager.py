import os
import shutil
from config import Config

class FileManager:
    def __init__(self):
        pass
    
    def get_pending_images(self):
        """처리 대기 중인 이미지 파일들 반환"""
        if not os.path.exists(Config.ORIGINAL_NOTES_DIR):
            return []

        image_files = []
        for filename in os.listdir(Config.ORIGINAL_NOTES_DIR):
            if self._is_supported_image(filename):
                filepath = os.path.join(Config.ORIGINAL_NOTES_DIR, filename)
                image_files.append(filepath)

        return sorted(image_files)  # 파일명 순으로 정렬

    def get_pending_markdown(self):
        """처리 대기 중인 마크다운 파일들 반환"""
        if not os.path.exists(Config.ORIGINAL_NOTES_DIR):
            return []

        md_files = []
        for filename in os.listdir(Config.ORIGINAL_NOTES_DIR):
            if self._is_supported_markdown(filename):
                filepath = os.path.join(Config.ORIGINAL_NOTES_DIR, filename)
                md_files.append(filepath)

        return sorted(md_files)  # 파일명 순으로 정렬

    def get_all_pending_files(self):
        """처리 대기 중인 모든 파일들 반환 (이미지 + 마크다운)"""
        return {
            'images': self.get_pending_images(),
            'markdown': self.get_pending_markdown()
        }
    
    def move_to_linked(self, image_path):
        """처리 완료된 이미지를 linked_notes로 이동"""
        try:
            filename = os.path.basename(image_path)
            destination = os.path.join(Config.LINKED_NOTES_DIR, filename)
            
            # 중복 파일명 처리
            destination = self._ensure_unique_destination(destination)
            
            # 파일 이동
            shutil.move(image_path, destination)
            
            print(f"이미지 이동 완료: {filename} -> linked_notes/")
            return os.path.basename(destination)
            
        except Exception as e:
            print(f"파일 이동 중 오류 발생: {e}")
            return None
    
    def delete_markdown_file(self, md_path):
        """
        마크다운 파일 삭제 (원본 유지 안 함)

        Args:
            md_path: 삭제할 마크다운 파일 경로

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if os.path.exists(md_path):
                os.remove(md_path)
                filename = os.path.basename(md_path)
                print(f"🗑️  원본 마크다운 삭제: {filename}")
                return True
            else:
                print(f"⚠️  파일을 찾을 수 없습니다: {md_path}")
                return False
        except Exception as e:
            print(f"❌ 파일 삭제 중 오류 발생: {e}")
            return False

    def _is_supported_image(self, filename):
        """지원되는 이미지 형식인지 확인"""
        extension = filename.lower().split('.')[-1]
        return extension in Config.SUPPORTED_IMAGE_FORMATS

    def _is_supported_markdown(self, filename):
        """지원되는 마크다운 형식인지 확인"""
        extension = filename.lower().split('.')[-1]
        return extension in Config.SUPPORTED_MARKDOWN_FORMATS
    
    def _ensure_unique_destination(self, destination):
        """중복 파일명 처리 (목적지)"""
        if not os.path.exists(destination):
            return destination
        
        directory = os.path.dirname(destination)
        filename = os.path.basename(destination)
        name, extension = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(destination):
            new_filename = f"{name}_{counter:02d}{extension}"
            destination = os.path.join(directory, new_filename)
            counter += 1
        
        return destination
    
    def get_stats(self):
        """처리 통계 반환"""
        pending_count = len(self.get_pending_images())
        
        linked_count = 0
        if os.path.exists(Config.LINKED_NOTES_DIR):
            linked_count = len([f for f in os.listdir(Config.LINKED_NOTES_DIR) 
                               if self._is_supported_image(f)])
        
        return {
            'pending': pending_count,
            'processed': linked_count
        }