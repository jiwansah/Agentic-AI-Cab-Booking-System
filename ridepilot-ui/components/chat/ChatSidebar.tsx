"use client";

import {
  MessageSquarePlus,
  History,
  Loader2,
  X,
} from "lucide-react";

import type { Conversation } from "@/lib/api";

interface ChatSidebarProps {
  conversations: Conversation[];
  selectedConversationId: string | null;
  loading: boolean;
  mobileOpen: boolean;

  onNewChat: () => void;
  onSelectConversation: (
    conversationId: string
  ) => void;
  onCloseMobile: () => void;
}

function formatConversationDate(
  value: string
): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getConversationTitle(
  conversation: Conversation
): string {
  if (conversation.title?.trim()) {
    return conversation.title.trim();
  }

  return formatConversationDate(
    conversation.created_at
  );
}

export default function ChatSidebar({
  conversations,
  selectedConversationId,
  loading,
  mobileOpen,
  onNewChat,
  onSelectConversation,
  onCloseMobile,
}: ChatSidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50
          flex w-[280px] flex-col
          border-r border-slate-200
          bg-white
          transition-transform duration-200
          md:relative md:z-auto md:flex
          md:w-[280px]
          md:translate-x-0
          ${mobileOpen
            ? "translate-x-0"
            : "-translate-x-full md:translate-x-0"}
        `}
      >
        {/* Mobile header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4 md:hidden">
          <div className="font-semibold text-slate-900">
            Chat History
          </div>

          <button
            onClick={onCloseMobile}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
          >
            <X size={20} />
          </button>
        </div>

        {/* New Chat */}
        <div className="p-4">
          <button
            onClick={onNewChat}
            className="
              flex w-full items-center justify-center
              gap-2 rounded-xl
              bg-slate-900
              px-4 py-3
              text-sm font-semibold text-white
              transition
              hover:bg-slate-800
            "
          >
            <MessageSquarePlus size={18} />
            New Chat
          </button>
        </div>

        {/* Navigation */}
        <div className="px-4 pb-3">
          <div className="flex items-center gap-2 px-2 text-sm font-semibold text-slate-700">
            <History size={17} />
            Chat History
          </div>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto px-3 pb-4">
          {loading ? (
            <div className="flex items-center justify-center py-10 text-slate-500">
              <Loader2
                size={20}
                className="mr-2 animate-spin"
              />
              Loading...
            </div>
          ) : conversations.length === 0 ? (
            <div className="px-3 py-8 text-center text-sm text-slate-500">
              No previous conversations
            </div>
          ) : (
            <div className="space-y-1">
              {conversations.map((conversation) => {
                const selected =
                  conversation.conversation_id ===
                  selectedConversationId;

                return (
                  <button
                    key={conversation.conversation_id}
                    onClick={() =>
                      onSelectConversation(
                        conversation.conversation_id
                      )
                    }
                    className={`
                      w-full rounded-xl px-3 py-3
                      text-left transition
                      ${
                        selected
                          ? "bg-slate-100 text-slate-900"
                          : "text-slate-600 hover:bg-slate-50"
                      }
                    `}
                  >
                    <div className="flex items-start gap-3">
                      <MessageSquarePlus
                        size={17}
                        className="mt-0.5 shrink-0"
                      />

                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium">
                          {getConversationTitle(
                            conversation
                          )}
                        </div>

                        {conversation.trip_state
                          ?.pickup &&
                          conversation.trip_state
                            ?.destination && (
                            <div className="mt-1 truncate text-xs text-slate-400">
                              {
                                conversation.trip_state
                                  .pickup
                              }{" "}
                              →{" "}
                              {
                                conversation.trip_state
                                  .destination
                              }
                            </div>
                          )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}