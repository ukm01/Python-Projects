import {
  type FormEvent,
  type KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  AlertCircle,
  Bot,
  FileText,
  Loader2,
  MessageSquareText,
  Send,
  Sparkles,
  Trash2,
  UserRound,
} from "lucide-react";

import type { ChatCitation } from "@/api/types";
import { Button } from "@/components/ui/button";
import { useChat } from "@/hooks/api";
import { cn } from "@/lib/utils";


const suggestedQuestions = [
  "What is the probation period?",
  "What does the warranty cover?",
  "How does the leave policy work?",
];

export function ChatBotSection() {
  const {
    messages,
    sendQuestion,
    clearConversation,
    isLoading,
    error,
    clearError,
  } = useChat();
  const [question, setQuestion] = useState("");
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }, [isLoading, messages]);

  async function submitQuestion(value: string) {
    const submittedQuestion = value.trim();
    if (!submittedQuestion || isLoading) {
      return;
    }

    setQuestion("");
    clearError();
    const sent = await sendQuestion(submittedQuestion);
    if (!sent) {
      setQuestion(submittedQuestion);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitQuestion(question);
  }

  function handleQuestionKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitQuestion(question);
    }
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-5 py-6 md:px-8">
      <section className="grid min-h-[calc(100vh-8.5rem)] grid-rows-[auto_1fr_auto] overflow-hidden rounded-xl border bg-white shadow-sm">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <MessageSquareText className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">Knowledge Assistant</h1>
              <p className="text-xs text-muted-foreground">
                Answers use only the company documents available to you.
              </p>
            </div>
          </div>

          {messages.length > 0 ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="gap-2 text-muted-foreground"
              onClick={clearConversation}
              disabled={isLoading}
            >
              <Trash2 className="h-4 w-4" />
              Clear chat
            </Button>
          ) : null}
        </header>

        <div
          className="max-h-[calc(100vh-18rem)] min-h-[360px] overflow-y-auto px-4 py-6 md:px-8"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <EmptyChat onSelectQuestion={(value) => void submitQuestion(value)} />
          ) : (
            <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
              {messages.map((message) =>
                message.role === "user" ? (
                  <UserMessage key={message.id} content={message.content} />
                ) : (
                  <AssistantMessage
                    key={message.id}
                    content={message.content}
                    status={message.response.status}
                    citations={message.response.citations}
                  />
                ),
              )}

              {isLoading ? <LoadingMessage /> : null}

              {error ? (
                <div
                  role="alert"
                  className="flex items-start gap-2 rounded-lg border border-destructive/25 bg-destructive/10 px-4 py-3 text-sm text-destructive"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              ) : null}
              <div ref={endOfMessagesRef} />
            </div>
          )}
        </div>

        <form className="border-t bg-background/55 p-4" onSubmit={handleSubmit}>
          <div className="mx-auto flex w-full max-w-4xl items-end gap-3">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleQuestionKeyDown}
              placeholder="Ask about products, policies, warranties, and more..."
              aria-label="Company knowledge question"
              rows={2}
              maxLength={2000}
              disabled={isLoading}
              className="min-h-12 flex-1 resize-none rounded-lg border border-input bg-white px-3 py-3 text-sm shadow-sm outline-none transition-colors placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
            />
            <Button
              type="submit"
              size="icon"
              className="h-12 w-12 shrink-0"
              aria-label="Send question"
              disabled={!question.trim() || isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </div>
          <p className="mx-auto mt-2 w-full max-w-4xl text-xs text-muted-foreground">
            Press Enter to send. Use Shift + Enter for a new line.
          </p>
        </form>
      </section>
    </div>
  );
}

function EmptyChat({
  onSelectQuestion,
}: {
  onSelectQuestion: (question: string) => void;
}) {
  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
        <Sparkles className="h-6 w-6" />
      </div>
      <h2 className="mt-5 text-xl font-semibold">Ask about company information</h2>
      <p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">
        I’ll search the documents you’re permitted to access and show the
        sources used for the answer.
      </p>
      <div className="mt-6 grid w-full gap-3 sm:grid-cols-3">
        {suggestedQuestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onSelectQuestion(suggestion)}
            className="rounded-lg border bg-white px-4 py-3 text-left text-sm font-medium transition-colors hover:border-primary/40 hover:bg-primary/5"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}

function UserMessage({ content }: { content: string }) {
  return (
    <article className="ml-auto flex max-w-[85%] items-start gap-3">
      <div className="rounded-2xl rounded-tr-sm bg-primary px-4 py-3 text-sm leading-6 text-primary-foreground shadow-sm">
        {content}
      </div>
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
        <UserRound className="h-4 w-4" />
      </div>
    </article>
  );
}

function AssistantMessage({
  content,
  status,
  citations,
}: {
  content: string;
  status: "answered" | "insufficient_context";
  citations: ChatCitation[];
}) {
  return (
    <article className="flex max-w-[92%] items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Bot className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div
          className={cn(
            "rounded-2xl rounded-tl-sm border px-4 py-3 text-sm leading-6 shadow-sm",
            status === "insufficient_context"
              ? "border-amber-200 bg-amber-50 text-amber-950"
              : "bg-white",
          )}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
        {citations.length > 0 ? <CitationList citations={citations} /> : null}
      </div>
    </article>
  );
}

function CitationList({ citations }: { citations: ChatCitation[] }) {
  return (
    <div className="mt-3">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Sources
      </p>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation) => (
          <div
            key={`${citation.source_id}-${citation.chunk_id}`}
            className="flex max-w-full items-center gap-2 rounded-md border bg-muted/55 px-3 py-2 text-xs"
            title={citation.original_filename}
          >
            <FileText className="h-3.5 w-3.5 shrink-0 text-primary" />
            <span className="truncate font-medium">{citation.document_name}</span>
            <span className="shrink-0 text-muted-foreground">
              {citation.page_number === null
                ? citation.source_id
                : `Page ${citation.page_number}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LoadingMessage() {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Bot className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border bg-white px-4 py-3 text-sm text-muted-foreground shadow-sm">
        <Loader2 className="h-4 w-4 animate-spin text-primary" />
        Searching your documents and preparing an answer…
      </div>
    </div>
  );
}
