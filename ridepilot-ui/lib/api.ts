const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://192.168.29.7:8000';

export type AccountType = "registered" | "guest";

export interface AuthResponse {
  user_id: string;
  session_id: string;
  access_token: string;
  token_type?: string;
  expires_at?: string;
  account_type: "registered" | "guest";

  device_credential?: string;
  recovery_code?: string;
}

export type LoginRequest = { identifier: string; password: string };
export type RegisterRequest = { phone: string; email?: string; password: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "*/*",
      ...(init?.body ? {"Content-Type":"application/json"} : {}),
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") message = body.detail;
      else if (Array.isArray(body?.detail))
        message = body.detail.map((x:{msg?:string})=>x.msg).filter(Boolean).join(", ");
    } catch {}
    throw new Error(message);
  }
  return response.json();
}

// POST /auth/login
// {"identifier":"strings","password":"stringst"}
export function login(payload: LoginRequest) {
  return request<AuthResponse>("/auth/login", {
    method:"POST", body:JSON.stringify(payload)
  });
}

// POST /auth/guest — no request body
export function continueAsGuest() {
  return request<AuthResponse>("/auth/guest", {method:"POST"});
}

// POST /auth/register
// {"phone":"strings_2","email":"user_2@example.com","password":"stringst"}
export function register(payload: RegisterRequest) {
  return request<AuthResponse>("/auth/register", {
    method:"POST", body:JSON.stringify(payload)
  });
}




export interface Conversation {
  title: string | null;
  created_at: string;
  user_id: string;
  conversation_id: string;
  trip_state?: {
    pickup?: string | null;
    destination?: string | null;
    passengers?: number | null;
    pickup_date?: string | null;
    pickup_time?: string | null;
    preferred_provider?: string | null;
    max_fare?: number | null;
    clarification_needed?: string[];
  };
  updated_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | string;
  content: string | null;
  tool_calls?: unknown[];
  reasoning?: string;
}

export interface ConversationMessagesResponse {
  conversation_id: string;
  messages: ChatMessage[];
}


export function getAuthSession(): AuthResponse | null {
  if (typeof window === "undefined") {
    return null;
  }

  const stored = sessionStorage.getItem("ridepilot_auth");

  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as AuthResponse;
  } catch {
    return null;
  }
}

export function saveAuthSession(session: AuthResponse) {
  sessionStorage.setItem(
    "ridepilot_auth",
    JSON.stringify(session)
  );
}

export function clearAuthSession() {
  sessionStorage.removeItem("ridepilot_auth");
}


/**
 * Common authenticated headers.
 */
function getAuthHeaders(): HeadersInit {
  const session = getAuthSession();

  if (!session?.access_token) {
    throw new Error("Authentication session not found.");
  }

  return {
    Accept: "*/*",
    Authorization: `Bearer ${session.access_token}`,
  };
}


/**
 * Get user's conversation history.
 */
export async function getConversations(): Promise<Conversation[]> {
  const response = await fetch(
    `${API_BASE_URL}/conversations`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const detail = await getApiError(response);
    throw new Error(detail);
  }

  return response.json();
}


/**
 * Get messages for a conversation.
 */
export async function getConversationMessages(
  conversationId: string
): Promise<ConversationMessagesResponse> {
  const response = await fetch(
    `${API_BASE_URL}/conversations/${conversationId}/chatmessages`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const detail = await getApiError(response);
    throw new Error(detail);
  }

  return response.json();
}


export interface CabBookingChatRequest {
  message: string;
  conversation_id: string;
}

export interface CabBookingChatResponse {
  conversation_id: string;
  message?: string;
  content?: string;
  response?: string;
  reply?: string;
  [key: string]: unknown;
}

export async function sendChatMessage(
  message: string,
  conversationId: string = ""
): Promise<CabBookingChatResponse> {
  const session = getAuthSession();

  if (!session?.access_token) {
    throw new Error("Authentication session not found.");
  }

  const response = await fetch(`${API_BASE_URL}/cab_booking_chat`, {
    method: "POST",
    headers: {
      Accept: "*/*",
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });

  if (!response.ok) {
    throw new Error(await getApiError(response));
  }

  return response.json();
}


/**
 * Convert FastAPI errors into a useful message.
 */
async function getApiError(
  response: Response
): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item: any) => item?.msg || String(item))
        .join(", ");
    }

    return "Request failed.";
  } catch {
    return `Request failed with status ${response.status}.`;
  }
}


export interface UserProfile {
  phone: string | null;
  email: string | null;
  user_id: string;
  account_type: "registered" | "guest";
  session_id: string;
  expires_at: string;
}

export async function getMyProfile(): Promise<UserProfile> {
  const session = getAuthSession();

  if (!session?.access_token) {
    throw new Error("Authentication session not found.");
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Accept: "*/*",
      Authorization: `Bearer ${session.access_token}`,
    },
  });

  if (!response.ok) {
    throw new Error(await getApiError(response));
  }

  return response.json();
}

