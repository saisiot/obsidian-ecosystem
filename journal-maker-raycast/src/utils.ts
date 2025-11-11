import * as fs from "fs";
import * as path from "path";

/**
 * 일기 입력을 파싱하여 파일명과 본문을 추출
 * @param input 전체 입력 텍스트
 * @returns { filename: string, content: string }
 */
export function parseJournalInput(input: string): { filename: string; content: string } {
  const lines = input.split("\n");

  if (lines.length === 0) {
    throw new Error("입력이 비어있습니다");
  }

  // 첫 줄을 파일명으로 사용 (YYYYMMDD 제목)
  const filename = lines[0].trim() + ".md";

  // 나머지 줄을 본문으로 사용
  const content = lines.slice(1).join("\n");

  return { filename, content };
}

/**
 * 일기를 Markdown 파일로 저장
 * @param filename 파일명 (YYYYMMDD 제목.md)
 * @param content 본문 내용
 * @param savePath 저장 경로
 */
export function saveJournal(filename: string, content: string, savePath: string): void {
  // 디렉토리가 없으면 생성
  if (!fs.existsSync(savePath)) {
    fs.mkdirSync(savePath, { recursive: true });
  }

  // 전체 파일 경로
  const fullPath = path.join(savePath, filename);

  // 파일 저장
  fs.writeFileSync(fullPath, content, "utf-8");
}
