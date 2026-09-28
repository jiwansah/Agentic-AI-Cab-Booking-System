"use client";

import {
  Menu,
  MoreVertical,
  Bot,
  User,
  LogOut,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  clearAuthSession,
  getAuthSession,
  getConversationMessages,
  getConversations,
  sendChatMessage,
  type ChatMessage,
  type Conversation,
} from "@/lib/api";

import ChatSidebar from "./ChatSidebar";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import {
  getMyProfile,
  type UserProfile,
} from "@/lib/api";

export default function ChatWindow() {
  const [conversations, setConversations] =
    useState<Conversation[]>([]);

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [selectedConversationId, setSelectedConversationId,] = useState<string | null>(null);

  const [thinking, setThinking] = useState(false);
  const [
    loadingConversations,
    setLoadingConversations,
  ] = useState(true);

  const [
    loadingMessages,
    setLoadingMessages,
  ] = useState(false);

  const [
    sendingMessage,
    setSendingMessage,
  ] = useState(false);

  const [mobileSidebarOpen, setMobileSidebarOpen] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [
    userMenuOpen,
    setUserMenuOpen,
  ] = useState(false);

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);

  const [authSession, setAuthSession] = useState<ReturnType<typeof getAuthSession>>(null);
  const [mounted, setMounted] = useState(false);


  useEffect(() => {
        const session = getAuthSession();

        setAuthSession(session);
        setMounted(true);
   }, []);


  /**
   * Load conversation list.
   */
  const loadConversations =
    useCallback(async () => {
      try {
        setLoadingConversations(true);
        setError(null);

        const data = await getConversations();

        setConversations(data);
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load chat history."
        );
      } finally {
        setLoadingConversations(false);
      }
    }, []);


    useEffect(() => {
        if (!mounted || !authSession) {
            return;
        }

        void loadConversations();
        }, [
        mounted,
        authSession,
        loadConversations,
        ]);


  /**
   * Load selected conversation.
   */

const handleSelectConversation = async (
  conversationId: string
) => {
  setSelectedConversationId(conversationId);
  setMobileSidebarOpen(false);

  try {
    const result =
      await getConversationMessages(conversationId);

    setMessages(
      result.messages.filter(
        (message) =>
          message.content &&
          message.content.trim().length > 0
      )
    );
  } catch (error) {
    console.error(
      "Failed to load conversation:",
      error
    );
  }
};

  /**
   * Start a new conversation.
   */
  function handleNewChat() {
    setSelectedConversationId(null);
    setMessages([]);
    setError(null);
    setMobileSidebarOpen(false);
  }

  /**
   * Send new chat message.
   */

  const handleSendMessage = async (message: string) => {
  if (!message.trim() || sendingMessage) {
    return;
  }

  const userMessage: ChatMessage = {
    role: "user",
    content: message,
  };

  // Immediately show user's message
  setMessages((prev) => [...prev, userMessage]);

  // Immediately show "thinking"
  setThinking(true);
  setSendingMessage(true);

  try {
    const response = await sendChatMessage(
      message,
      selectedConversationId ?? ""
    );

    // New conversation created by backend
    if (response.conversation_id) {
      setSelectedConversationId(
        response.conversation_id
      );
    }

    const assistantContent =
      response.content ??
      response.message ??
      response.response ??
      response.reply ??
      "";

    // Remove thinking indicator and show response
    if (assistantContent.trim()) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: assistantContent,
        },
      ]);
    }

    await loadConversations();

  } catch (error) {
    console.error("Chat request failed:", error);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content:
          "Sorry, I couldn't process your request. Please try again.",
      },
    ]);
  } finally {
    setThinking(false);
    setSendingMessage(false);
  }
};



  const handleProfileClick = async () => {
    setProfileOpen(true);
    setProfileLoading(true);
    setProfileError(null);

    try {
      const data = await getMyProfile();
      setProfile(data);
    } catch (error) {
      console.error("Failed to load profile:", error);

      setProfileError(
        error instanceof Error
          ? error.message
          : "Unable to load profile."
      );
    } finally {
      setProfileLoading(false);
    }
  };

  function handleLogout() {
    clearAuthSession();

    window.location.href = "/";
  }

if (!mounted) {
  return (
    <div className="flex h-dvh items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="text-3xl">🚕</div>

        <p className="mt-3 text-sm text-slate-500">
          Loading RidePilot...
        </p>
      </div>
    </div>
  );
}

if (!authSession) {
  return (
    <div className="flex h-dvh items-center justify-center bg-slate-50 p-6">
      <div className="text-center">
        <h1 className="text-xl font-semibold text-slate-900">
          Authentication required
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Please login to use RidePilot.
        </p>

        <button
          onClick={() => {
            window.location.href = "/";
          }}
          className="mt-5 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white"
        >
          Go to Login
        </button>
      </div>
    </div>
  );
}

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-white">
      {/* =====================================================
          TOP HEADER
          ===================================================== */}
      <header className="relative flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 md:px-6">
        <div className="flex items-center gap-3">
          {/* Mobile menu */}
          <button
            onClick={() =>
              setMobileSidebarOpen(true)
            }
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
          >
            <Menu size={21} />
          </button>

          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="text-2xl">
              🚕
            </div>

            <div className="font-bold tracking-tight text-slate-900">
              RidePilot
            </div>
          </div>
        </div>

        {/* Desktop header actions */}
        <div className="flex items-center gap-2">


          {/* Profile */}
          <div className="relative">

          <button type="button" onClick={handleProfileClick}>
            Profile
          </button>
          {profileOpen && (
            <div className="absolute right-0 top-full z-50 mt-2 w-72 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
              {/* Header */}
              <div className="mb-3 flex items-center justify-between border-b border-slate-100 pb-3">
                <h2 className="text-base font-semibold text-slate-900">
                  Profile
                </h2>

                <button
                  type="button"
                  onClick={() => setProfileOpen(false)}
                  className="rounded-md px-2 py-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                >
                  ✕
                </button>
              </div>

              {/* Loading */}
              {profileLoading && (
                <div className="py-4 text-center text-sm text-slate-500">
                  Loading profile...
                </div>
              )}

              {/* Error */}
              {profileError && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                  {profileError}
                </div>
              )}

              {/* Profile details */}
              {profile && !profileLoading && (
                <div className="space-y-3 text-sm">

                  <div className="flex items-center">
                    <span className="w-32 shrink-0 font-medium text-slate-500">
                      Account Type
                    </span>
                    <span className="text-slate-900">
                      {profile.account_type}
                    </span>
                  </div>

                  <div className="flex items-center">
                    <span className="w-32 shrink-0 font-medium text-slate-500">
                      Phone
                    </span>
                    <span className="text-slate-900">
                      {profile.phone || "Not provided"}
                    </span>
                  </div>

                  <div className="flex items-center">
                    <span className="w-32 shrink-0 font-medium text-slate-500">
                      Email
                    </span>
                    <span className="break-all text-slate-900">
                      {profile.email || "Not provided"}
                    </span>
                  </div>

                  <div className="flex items-start">
                    <span className="w-32 shrink-0 font-medium text-slate-500">
                      User ID
                    </span>
                    <span className="break-all text-xs text-slate-700">
                      {profile.user_id}
                    </span>
                  </div>

                  <div className="flex items-center">
                    <span className="w-32 shrink-0 font-medium text-slate-500">
                      Session Expires
                    </span>
                    <span className="text-slate-900">
                      {new Date(profile.expires_at).toLocaleString("en-IN")}
                    </span>
                  </div>

                </div>
              )}
            </div>
          )}
          </div>




          {/* User menu */}
          <div className="relative">
            <button
              onClick={() =>
                setUserMenuOpen(
                  (current) => !current
                )
              }
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
            >
              <MoreVertical size={20} />
            </button>

            {userMenuOpen && (
              <div className="absolute right-0 top-11 z-50 w-52 rounded-xl border border-slate-200 bg-white p-2 shadow-xl">
                <div className="border-b border-slate-100 px-3 py-2">
                  <div className="text-xs text-slate-400">
                    Account
                  </div>

                  <div className="mt-1 truncate text-sm font-medium text-slate-800">
                    {authSession.account_type}
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="mt-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut size={16} />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* =====================================================
          MAIN AREA
          ===================================================== */}
      <div className="flex min-h-0 flex-1">
        <ChatSidebar
          conversations={conversations}
          selectedConversationId={
            selectedConversationId
          }
          loading={loadingConversations}
          mobileOpen={mobileSidebarOpen}
          onNewChat={handleNewChat}
          onSelectConversation={
            handleSelectConversation
          }
          onCloseMobile={() =>
            setMobileSidebarOpen(false)
          }
        />

        {/* ===================================================
            CHAT AREA
            =================================================== */}
        <main className="flex min-w-0 flex-1 flex-col bg-slate-50">
          {/* Chat title */}
          <div className="border-b border-slate-200 bg-white px-4 py-5 md:px-8">
            <div className="mx-auto flex max-w-4xl items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-white">
                <Bot size={20} />
              </div>

              <div>
                <h1 className="font-semibold text-slate-900">
                  RidePilot AI
                </h1>

                <p className="text-xs text-slate-500">
                  Your AI Cab Assistant
                </p>
              </div>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="px-4 pt-4 md:px-8">
              <div className="mx-auto max-w-4xl rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 md:px-8">
            <div className="mx-auto max-w-4xl">
              {messages.length === 0 &&
              !loadingMessages ? (
                <EmptyChat />
              ) : (
                <ChatMessages
                  messages={messages}
                  thinking={thinking}
                />
              )}
            </div>
          </div>

          {/* Input */}
          <ChatInput
            disabled={
              sendingMessage ||
              loadingMessages
            }
            onSend={handleSendMessage}
          />
        </main>
      </div>
    </div>



    
  );
}


/**
 * Empty chat screen.
 */
function EmptyChat() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center text-center">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-slate-900 text-3xl shadow-sm">
        🤖
      </div>

      <h2 className="text-2xl font-bold text-slate-900">
        RidePilot AI
      </h2>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        Where would you like to go?
        <br />
        Tell me your pickup location,
        destination and passenger count.
      </p>

      <div className="mt-6 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm text-slate-500 shadow-sm">
        Example:{" "}
        <span className="font-medium text-slate-700">
          I need a cab from Durgapur
          to Asansol for 2 people
        </span>
      </div>
    </div>
  );
}


