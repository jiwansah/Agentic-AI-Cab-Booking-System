"use client";


import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/api";

interface ChatMessagesProps {
  messages: ChatMessage[];
  thinking?: boolean;
}

export default function ChatMessages({
  messages,
  thinking = false,
}: ChatMessagesProps) {

    const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, thinking]);


  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((message, index) => {
          if (!message.content?.trim()) {
            return null;
          }

          const isUser = message.role === "user";

          return (
            <div
              key={`${index}-${message.role}`}
              className={`flex ${
                isUser ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                  isUser
                    ? "rounded-br-md bg-blue-600 text-white"
                    : "rounded-bl-md bg-slate-100 text-slate-800"
                }`}
              >
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
              </div>
            </div>
          );
        })}

        {thinking && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-md bg-slate-100 px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">
                  RidePilot is thinking
                </span>

                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Auto-scroll target */}
        <div ref={bottomRef} />

      </div>
    </div>
  );
}