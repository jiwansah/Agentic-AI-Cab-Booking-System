"use client";

import {
  ArrowUp,
  Loader2,
  Mic,
} from "lucide-react";
import {
  FormEvent,
  KeyboardEvent,
  useState,
} from "react";

interface ChatInputProps {
  disabled?: boolean;
  onSend: (message: string) => Promise<void> | void;
}

export default function ChatInput({
  disabled = false,
  onSend,
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  async function handleSubmit(
    event?: FormEvent
  ) {
    event?.preventDefault();

    const value = message.trim();

    if (!value || disabled) {
      return;
    }

    setMessage("");

    await onSend(value);
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      void handleSubmit();
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-slate-200 bg-white p-3 md:p-4"
    >
      <div className="mx-auto flex max-w-4xl items-end gap-2 rounded-2xl border border-slate-300 bg-white p-2 shadow-sm">
        <textarea
          value={message}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder="Type a message..."
          className="
            max-h-32 min-h-[42px] flex-1
            resize-none
            border-0 bg-transparent
            px-3 py-2
            text-sm text-slate-900
            outline-none
            placeholder:text-slate-400
          "
        />

        {/* Microphone placeholder */}
        <button
          type="button"
          disabled
          title="Voice input coming soon"
          className="hidden rounded-xl p-2.5 text-slate-400 md:block"
        >
          <Mic size={19} />
        </button>

        <button
          type="submit"
          disabled={
            disabled || !message.trim()
          }
          className="
            flex h-10 w-10 shrink-0
            items-center justify-center
            rounded-xl
            bg-slate-900
            text-white
            transition
            hover:bg-slate-800
            disabled:cursor-not-allowed
            disabled:opacity-40
          "
        >
          {disabled ? (
            <Loader2
              size={18}
              className="animate-spin"
            />
          ) : (
            <ArrowUp size={19} />
          )}
        </button>
      </div>

      <div className="mx-auto mt-2 hidden max-w-4xl text-center text-[11px] text-slate-400 md:block">
        Press Enter to send · Shift + Enter for a new line
      </div>
    </form>
  );
}