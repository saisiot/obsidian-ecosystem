import * as fs from "fs";
import * as path from "path";

/**
 * 현재 날짜를 YYMMDD 형식으로 반환
 */
export function getDateString(): string {
  const now = new Date();
  const year = now.getFullYear().toString().slice(-2);
  const month = (now.getMonth() + 1).toString().padStart(2, "0");
  const day = now.getDate().toString().padStart(2, "0");
  return `${year}${month}${day}`;
}

/**
 * 파일명으로 사용할 수 없는 특수문자 제거 및 공백을 언더바로 변환
 */
export function sanitizeFilename(filename: string): string {
  // 특수문자 제거: / \ : * ? " < > |
  let sanitized = filename.replace(/[/\\:*?"<>|]/g, "");
  // 공백을 언더바로 변환
  sanitized = sanitized.replace(/\s+/g, "_");
  // 파일명 길이 제한 (100자)
  if (sanitized.length > 100) {
    sanitized = sanitized.slice(0, 100);
  }
  return sanitized;
}

/**
 * 태그 문자열을 검증하고 해시태그 형식으로 변환
 */
export function processTags(tagsInput: string): { valid: boolean; tags: string; error?: string } {
  // 쉼표로 분리
  const tagArray = tagsInput
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);

  // 빈 태그만 있는 경우
  if (tagArray.length === 0) {
    return { valid: false, tags: "", error: "유효한 태그를 입력해주세요" };
  }

  // 해시태그 형식으로 변환
  const hashTags = tagArray.map((tag) => `#${tag}`).join(" ");
  return { valid: true, tags: hashTags };
}

/**
 * 메모를 Markdown 파일로 저장
 */
export function saveNote(title: string, content: string, tags: string, savePath: string): void {
  // 디렉토리가 없으면 생성
  if (!fs.existsSync(savePath)) {
    fs.mkdirSync(savePath, { recursive: true });
  }

  // 파일명 생성
  const dateString = getDateString();
  const sanitizedTitle = sanitizeFilename(title);
  const filename = `${dateString}_${sanitizedTitle}.md`;
  const fullPath = path.join(savePath, filename);

  // Markdown 내용 생성
  const markdown = `# ${title}

${content}

${tags}
`;

  // 파일 저장
  fs.writeFileSync(fullPath, markdown, "utf-8");
}

/**
 * 파일명 유효성 검사
 */
export function validateTitle(title: string): { valid: boolean; error?: string } {
  if (title.trim().length === 0) {
    return { valid: false, error: "제목을 입력해주세요" };
  }

  const sanitized = sanitizeFilename(title);
  if (sanitized.length > 100) {
    return { valid: false, error: "제목은 100자 이내로 입력해주세요" };
  }

  return { valid: true };
}

/**
 * 본문 유효성 검사
 */
export function validateContent(content: string): { valid: boolean; error?: string } {
  if (content.trim().length === 0) {
    return { valid: false, error: "본문을 입력해주세요" };
  }
  return { valid: true };
}

/**
 * 태그 유효성 검사
 */
export function validateTags(tags: string): { valid: boolean; error?: string } {
  if (tags.trim().length === 0) {
    return { valid: false, error: "최소 1개 이상의 태그를 입력해주세요" };
  }

  const result = processTags(tags);
  if (!result.valid) {
    return { valid: false, error: result.error };
  }

  return { valid: true };
}
