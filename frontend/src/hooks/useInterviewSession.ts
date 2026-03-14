import { useCallback, useEffect, useMemo, useState } from "react";
import type { KeyboardEvent } from "react";
import type { Problem } from "../types/problem";
import {
  completeInterviewSession,
  getInterviewSession,
  postInterviewMessage,
  runSubmission,
  startInterviewSession,
} from "../services/api";
import type {
  InterviewCompletionResponse,
  InterviewEvaluationResponse,
  InterviewSessionDetailResponse,
} from "../types/interview";
import type { ChatMessage } from "../utils/interview";
import {
  buildNitpicks,
  extractAiAdditionalImprovements,
  sortMessagesByTime,
  summarizeRubric,
  toChatHistory,
} from "../utils/interview";

type InterviewPanelTab = "chat" | "feedback";

export interface UseInterviewSessionResult {
  languageOptions: string[];
  selectedLanguage: string;
  code: string;
  draftMessage: string;
  messages: ChatMessage[];
  sessionStatus: "ACTIVE" | "COMPLETED" | "ABANDONED";
  canSubmit: boolean;
  activeTab: InterviewPanelTab;
  evaluations: InterviewEvaluationResponse[];
  completionResult: InterviewCompletionResponse | null;
  isSending: boolean;
  isSubmittingCode: boolean;
  isLoadingFeedback: boolean;
  error: string | null;
  rubricRows: ReturnType<typeof summarizeRubric>;
  nitpicks: string[];
  finalScore: number | null;
  didPass: boolean | null;
  hasSession: boolean;
  setDraftMessage: (value: string) => void;
  setActiveTab: (tab: InterviewPanelTab) => void;
  handleLanguageChange: (lang: string) => void;
  updateCode: (value: string | undefined) => void;
  handleSend: () => Promise<void>;
  handleSubmitCode: () => Promise<void>;
  handleDraftKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
}

export function useInterviewSession(problem: Problem): UseInterviewSessionResult {
  const starterCode = problem?.starter_code ?? {};
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  const [selectedLanguage, setSelectedLanguage] = useState<string>(
    languageOptions[0] ?? "javascript"
  );
  const [code, setCode] = useState<string>(starterCode[selectedLanguage] ?? "");
  const [draftMessage, setDraftMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] =
    useState<"ACTIVE" | "COMPLETED" | "ABANDONED">("ACTIVE");
  const [canSubmit, setCanSubmit] = useState(false);
  const [activeTab, setActiveTab] = useState<InterviewPanelTab>("chat");
  const [evaluations, setEvaluations] = useState<InterviewEvaluationResponse[]>([]);
  const [completionResult, setCompletionResult] =
    useState<InterviewCompletionResponse | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isSubmittingCode, setIsSubmittingCode] = useState(false);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      setError(null);
      setCanSubmit(false);
      setCompletionResult(null);
      setEvaluations([]);
      setActiveTab("chat");
      try {
        const started = await startInterviewSession({ problem_id: problem.id });
        const detail = await getInterviewSession(started.id);
        applySession(detail);
      } catch (sessionError) {
        const message =
          sessionError instanceof Error
            ? sessionError.message
            : "Failed to start interview session.";
        setError(message);
      }
    };

    void initializeSession();
  }, [problem.id]);

  useEffect(() => {
    setSelectedLanguage(languageOptions[0] ?? "javascript");
  }, [languageOptions]);

  useEffect(() => {
    setCode(starterCode[selectedLanguage] ?? "");
  }, [starterCode, selectedLanguage]);

  useEffect(() => {
    if (
      sessionStatus !== "COMPLETED" ||
      !sessionId ||
      completionResult ||
      isLoadingFeedback
    ) {
      return;
    }
    const hydrateFeedback = async () => {
      setIsLoadingFeedback(true);
      try {
        const result = await completeInterviewSession(sessionId);
        setCompletionResult(result);
        const detail = await getInterviewSession(sessionId);
        setEvaluations(detail.evaluations ?? []);
      } catch {
        // keep chat functional if completion fails
      } finally {
        setIsLoadingFeedback(false);
      }
    };
    void hydrateFeedback();
  }, [sessionStatus, completionResult, isLoadingFeedback, sessionId]);

  const handleLanguageChange = useCallback(
    (nextLanguage: string) => {
      setSelectedLanguage(nextLanguage);
      setCode(starterCode[nextLanguage] ?? "");
    },
    [starterCode]
  );

  const updateCode = useCallback((value: string | undefined) => {
    setCode(value ?? "");
  }, []);

  const applySession = useCallback(
    (detail: InterviewSessionDetailResponse) => {
      setSessionId(detail.id);
      setSessionStatus(detail.status);
      setEvaluations(detail.evaluations ?? []);
      const nextCanSubmit = canSubmit || Boolean(detail.can_code);
      setCanSubmit(nextCanSubmit);
      if (detail.status === "COMPLETED") {
        setActiveTab("feedback");
      }
      setMessages(
        sortMessagesByTime(
          detail.messages
            .filter(
              (message) => message.role === "assistant" || message.role === "user"
            )
            .map((message) => ({
              id: message.id,
              role: message.role === "assistant" ? "ai" : "you",
              content: message.content,
              createdAt: new Date(message.created_at).getTime(),
            }))
        )
      );
    },
    [canSubmit]
  );

  const handleSend = useCallback(async () => {
    if (!sessionId) {
      return;
    }
    const content = draftMessage.trim();
    if (!content) {
      return;
    }

    const optimisticMessageId = `optimistic-${Date.now()}`;
    const nextMessages = [
      ...messages,
      {
        id: optimisticMessageId,
        role: "you" as const,
        content,
        createdAt: Date.now(),
      },
    ];
    setMessages(nextMessages);
    setDraftMessage("");
    setIsSending(true);
    setError(null);
    try {
      const detail = await postInterviewMessage(sessionId, {
        content,
        role: "user",
        has_submission: false,
        current_code: code,
        chat_history: toChatHistory(nextMessages),
      });
      applySession(detail);
    } catch (sendError) {
      setMessages((prev) =>
        prev.filter((message) => message.id !== optimisticMessageId)
      );
      setDraftMessage(content);
      const message =
        sendError instanceof Error ? sendError.message : "Failed to send message.";
      setError(message);
    } finally {
      setIsSending(false);
    }
  }, [applySession, code, draftMessage, messages, sessionId]);

  const handleSubmitCode = useCallback(async () => {
    if (!sessionId) {
      return;
    }

    setIsSubmittingCode(true);
    setError(null);

    try {
      const submission = await runSubmission({
        problem_id: problem.id,
        code_submitted: code,
        language: selectedLanguage,
      });

      const submissionSummary =
        submission.result === "pass"
          ? `I submitted my ${selectedLanguage} solution and all tests passed.`
          : `I submitted my ${selectedLanguage} solution and it failed. Error: ${
              submission.error ?? "Unknown failure"
            }`;

      const nextMessages = [
        ...messages,
        {
          id: `submission-${Date.now()}`,
          role: "you" as const,
          content: submissionSummary,
          createdAt: Date.now(),
        },
      ];
      const detail = await postInterviewMessage(sessionId, {
        content: submissionSummary,
        role: "user",
        has_submission: true,
        current_code: code,
        chat_history: toChatHistory(nextMessages),
      });
      applySession(detail);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Failed to submit code.";
      setError(message);
    } finally {
      setIsSubmittingCode(false);
    }
  }, [applySession, code, messages, problem.id, selectedLanguage, sessionId]);

  const handleDraftKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        void handleSend();
      }
    },
    [handleSend]
  );

  const rubricRows = useMemo(() => summarizeRubric(evaluations), [evaluations]);
  const aiAdditionalImprovements = useMemo(
    () => extractAiAdditionalImprovements(evaluations),
    [evaluations]
  );
  const nitpicks = useMemo(
    () =>
      aiAdditionalImprovements.length > 0
        ? aiAdditionalImprovements
        : buildNitpicks(rubricRows, completionResult),
    [aiAdditionalImprovements, rubricRows, completionResult]
  );
  const finalScore = completionResult?.final_score ?? null;
  const didPass = finalScore !== null ? finalScore >= 30 : null;
  const hasSession = Boolean(sessionId);

  return {
    languageOptions,
    selectedLanguage,
    code,
    draftMessage,
    messages,
    sessionStatus,
    canSubmit,
    activeTab,
    evaluations,
    completionResult,
    isSending,
    isSubmittingCode,
    isLoadingFeedback,
    error,
    rubricRows,
    nitpicks,
    finalScore,
    didPass,
    hasSession,
    setDraftMessage,
    setActiveTab,
    handleLanguageChange,
    updateCode,
    handleSend,
    handleSubmitCode,
    handleDraftKeyDown,
  };
}
