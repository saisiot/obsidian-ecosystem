import { ActionPanel, Action, Form, showToast, Toast, useNavigation, getPreferenceValues } from "@raycast/api";
import React, { useState } from "react";
import {
  validateTitle,
  validateContent,
  validateTags,
  processTags,
  saveNote,
  sanitizeFilename,
  getDateString,
} from "./utils";

interface Preferences {
  savePath: string;
}

// Preferences에서 저장 경로 가져오기
const preferences = getPreferenceValues<Preferences>();
const SAVE_PATH = preferences.savePath.replace(/^~/, process.env.HOME || "");

interface FormValues {
  title: string;
  content: string;
  tags: string;
}

export default function Command() {
  const { pop } = useNavigation();
  const [titleError, setTitleError] = useState<string | undefined>();
  const [contentError, setContentError] = useState<string | undefined>();
  const [tagsError, setTagsError] = useState<string | undefined>();

  // 폼 제출 핸들러
  async function handleSubmit(values: FormValues) {
    // 모든 에러 초기화
    setTitleError(undefined);
    setContentError(undefined);
    setTagsError(undefined);

    // 유효성 검사
    const titleValidation = validateTitle(values.title);
    const contentValidation = validateContent(values.content);
    const tagsValidation = validateTags(values.tags);

    let hasError = false;

    if (!titleValidation.valid) {
      setTitleError(titleValidation.error);
      hasError = true;
    }

    if (!contentValidation.valid) {
      setContentError(contentValidation.error);
      hasError = true;
    }

    if (!tagsValidation.valid) {
      setTagsError(tagsValidation.error);
      hasError = true;
    }

    if (hasError) {
      await showToast({
        style: Toast.Style.Failure,
        title: "입력 오류",
        message: "필수 항목을 확인해주세요",
      });
      return;
    }

    // 태그 처리
    const tagsResult = processTags(values.tags);
    if (!tagsResult.valid) {
      setTagsError(tagsResult.error);
      await showToast({
        style: Toast.Style.Failure,
        title: "태그 오류",
        message: tagsResult.error,
      });
      return;
    }

    try {
      // 파일 저장
      saveNote(values.title, values.content, tagsResult.tags, SAVE_PATH);

      // 파일명 생성 (Toast 메시지용)
      const dateString = getDateString();
      const sanitizedTitle = sanitizeFilename(values.title);
      const filename = `${dateString}_${sanitizedTitle}.md`;

      // 성공 메시지
      await showToast({
        style: Toast.Style.Success,
        title: "✅ 메모가 저장되었습니다",
        message: filename,
      });

      // 폼 닫기
      pop();
    } catch (error) {
      // 에러 처리
      const errorMessage = error instanceof Error ? error.message : "알 수 없는 오류";

      // 권한 에러 감지
      if (errorMessage.includes("EACCES") || errorMessage.includes("permission")) {
        await showToast({
          style: Toast.Style.Failure,
          title: "저장 권한이 없습니다",
          message: "시스템 설정에서 Raycast에 Full Disk Access 권한을 부여해주세요",
        });
      } else if (errorMessage.includes("ENOSPC")) {
        await showToast({
          style: Toast.Style.Failure,
          title: "저장 공간이 부족합니다",
          message: "디스크 공간을 확보한 후 다시 시도해주세요",
        });
      } else {
        await showToast({
          style: Toast.Style.Failure,
          title: "파일 저장 중 오류가 발생했습니다",
          message: errorMessage,
        });
      }
    }
  }

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm title="확인" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.TextField
        id="title"
        title="제목"
        placeholder="메모 제목을 입력하세요"
        error={titleError}
        onChange={() => setTitleError(undefined)}
      />
      <Form.TextArea
        id="content"
        title="본문"
        placeholder="메모 내용을 입력하세요"
        error={contentError}
        onChange={() => setContentError(undefined)}
      />
      <Form.TextField
        id="tags"
        title="태그"
        placeholder="쉼표로 구분하여 입력 (예: 개발, 아이디어, 급함)"
        error={tagsError}
        onChange={() => setTagsError(undefined)}
      />
      <Form.Description title="저장 경로" text={SAVE_PATH} />
    </Form>
  );
}
