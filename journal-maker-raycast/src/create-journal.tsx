import { ActionPanel, Action, Form, showToast, Toast, useNavigation, getPreferenceValues } from "@raycast/api";
import React, { useState } from "react";
import { parseJournalInput, saveJournal } from "./utils";

interface Preferences {
  journalPath: string;
}

// Preferences에서 저장 경로 가져오기
const preferences = getPreferenceValues<Preferences>();
const SAVE_PATH = preferences.journalPath.replace(/^~/, process.env.HOME || "");

interface FormValues {
  journalInput: string;
}

export default function Command() {
  const { pop } = useNavigation();
  const [inputError, setInputError] = useState<string | undefined>();

  // 폼 제출 핸들러
  async function handleSubmit(values: FormValues) {
    // 에러 초기화
    setInputError(undefined);

    // 입력 검증 (빈 입력만 확인)
    if (!values.journalInput || values.journalInput.trim().length === 0) {
      setInputError("입력 내용이 비어있습니다");
      await showToast({
        style: Toast.Style.Failure,
        title: "입력 오류",
        message: "일기 내용을 입력해주세요",
      });
      return;
    }

    try {
      // 입력 파싱
      const { filename, content } = parseJournalInput(values.journalInput);

      // 파일 저장
      saveJournal(filename, content, SAVE_PATH);

      // 성공 메시지
      await showToast({
        style: Toast.Style.Success,
        title: "✅ 일기가 저장되었습니다",
        message: filename,
      });

      // 토스트 메시지가 보이도록 잠시 대기 후 폼 닫기
      setTimeout(() => {
        pop();
      }, 1500);
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
      <Form.TextArea
        id="journalInput"
        title="일기 입력"
        placeholder={"첫 줄: YYYYMMDD 제목\n나머지 줄: 일기 내용"}
        error={inputError}
        onChange={() => setInputError(undefined)}
      />
      <Form.Description title="저장 경로" text={SAVE_PATH} />
      <Form.Description
        title="입력 형식"
        text="첫 줄에 'YYYYMMDD 제목'을 입력하고, 나머지 줄에 일기 내용을 입력하세요."
      />
    </Form>
  );
}
