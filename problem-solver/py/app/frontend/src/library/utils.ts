import {clsx, type ClassValue} from "clsx"
import {twMerge} from "tailwind-merge"
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from "axios";

type TokenResponse = {
  access_token: string;
  expires_in?: number;
  refresh_expires_in?: number;
  refresh_token?: string;
  token_type?: string;
  id_token?: string;
};

function getTokens(): TokenResponse | null {
  try {
    return JSON.parse(sessionStorage.getItem('kc_tokens') || 'null') as TokenResponse | null;
  } catch {
    return null;
  }
}

function getAccessToken(): string | null {
  const tokens = getTokens();
  return tokens?.access_token || null;
}

function isTokenExpiringSoon(tokens: TokenResponse | null): boolean {
  if (!tokens?.access_token) return true;
  
  try {
    const parts = tokens.access_token.split('.');
    if (parts.length < 2) return true;
    
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    const exp = payload.exp;
    
    if (!exp) return true;
    
    const now = Math.floor(Date.now() / 1000);
    return (exp - now) < 60;
  } catch {
    return true;
  }
}

function setTokens(tokens: TokenResponse): void {
  sessionStorage.setItem('kc_tokens', JSON.stringify(tokens));
}

const KEYCLOAK_BASE = (import.meta as any).env?.VITE_KEYCLOAK_BASE || 'https://localhost:8443';
const CLIENT_ID = (import.meta as any).env?.VITE_KEYCLOAK_CLIENT_ID || 'spa-client';
const TOKEN_ENDPOINT = `${KEYCLOAK_BASE}/realms/ostis-ann/protocol/openid-connect/token`;

function toFormUrlEncoded(obj: Record<string, string>): string {
  return Object.entries(obj)
    .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
    .join('&');
}

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
  config: InternalAxiosRequestConfig;
}> = [];

async function refreshAccessToken(): Promise<TokenResponse | null> {
  const tokens = getTokens();
  if (!tokens?.refresh_token) {
    return null;
  }

  try {
    const body = toFormUrlEncoded({
      grant_type: 'refresh_token',
      client_id: CLIENT_ID,
      refresh_token: tokens.refresh_token
    });

    const res = await fetch(TOKEN_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });

    if (!res.ok) {
      const txt = await res.text();
      console.error(`Token refresh failed ${res.status}: ${txt}`);
      return null;
    }

    const newTokens = await res.json() as TokenResponse;
    const merged: TokenResponse = {
      ...tokens,
      ...newTokens,
      refresh_token: newTokens.refresh_token || tokens.refresh_token
    };
    
    setTokens(merged);
    return merged;
  } catch (error) {
    console.error('Token refresh error:', error);
    return null;
  }
}


const GATEWAY_BASE_URL =
  (import.meta as any).env?.VITE_GATEWAY_BASE ||
  "https://gateway.local.test";

const API: AxiosInstance = axios.create({
    baseURL: GATEWAY_BASE_URL,
    headers: {"Content-Type": "application/json"},
});

API.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  let tokens = getTokens();
  
  if (tokens && isTokenExpiringSoon(tokens) && !isRefreshing) {
    isRefreshing = true;
    try {
      const newTokens = await refreshAccessToken();
      if (newTokens) {
        tokens = newTokens;
      }
    } catch (error) {
      console.warn('Failed to refresh token proactively:', error);
    } finally {
      isRefreshing = false;
    }
  }
  
  const token = tokens?.access_token || getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalRequest });
        });
      }

      isRefreshing = true;

      try {
        const newTokens = await refreshAccessToken();
        
        if (newTokens?.access_token) {
          const newToken = newTokens.access_token;

          failedQueue.forEach(({ resolve, config }) => {
            if (config.headers) {
              config.headers.Authorization = `Bearer ${newToken}`;
            }
            resolve(API(config));
          });
          failedQueue = [];

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          return API(originalRequest);
        } else {
          failedQueue.forEach(({ reject }) => {
            reject(error);
          });
          failedQueue = [];
          
          sessionStorage.removeItem('kc_tokens');
          window.location.href = '/';
          return Promise.reject(error);
        }
      } catch (refreshError) {

        failedQueue.forEach(({ reject }) => {
          reject(refreshError);
        });
        failedQueue = [];
        
        sessionStorage.removeItem('kc_tokens');
        window.location.href = '/';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type AgentStatus = "question" | "complete" | "processing" | "error";

export type TaskCategory = "informational" | "build_model" | "unclear";

export type ChatMode = "auto" | "consultant" | "designer";

export interface FormField {
  name: string;
  label: string;
  description?: string | null;
  placeholder?: string | null;
  value?: string | null;
  required: boolean;
}

interface ChatPayload {
  query: string;
  session_id?: string;
  user_response?: string;
  form_data?: Record<string, string>;
  chat_mode?: ChatMode;
}

export interface ChatResponse {
  status: AgentStatus;
  message: string;
  session_id: string;
  category?: TaskCategory;
  collected_data?: Record<string, string>;
  form_fields?: FormField[] | null;
  recommended_model?: string | null;
  confidence?: number | null;
  reasoning?: string | null;
  alternative_models?: string[] | null;
  best_link?: string | null;
  other_links?: string[];
}

interface FileUploadResponse {
  message: string;
  file_id: number;
  filename: string;
}

interface FileDeleteResponse {
  success: boolean;
  message: string;
}

export interface DocumentsInfo {
  id: number;
  filename: string;
  upload_timestamp: string;
}

interface DocumentDeleteRequest {
  file_id: number;
}

export interface DialogInfo {
  session_id: string;
  title?: string | null;
  category?: TaskCategory | null;
  chat_mode?: string | null;
  last_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DialogMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  category?: TaskCategory | null;
  meta?: Record<string, unknown> | null;
}

export const api = {
  async chat(payload: ChatPayload): Promise<ChatResponse> {
    const { data } = await API.post<ChatResponse>("/api/v1/chat", payload);
    return data;
  },

  async uploadDoc(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await API.post<FileUploadResponse>(
      "/api/v1/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data;
  },

  async deleteDoc(fileId: number): Promise<FileDeleteResponse> {
    const payload: DocumentDeleteRequest = { file_id: fileId };
    const { data } = await API.delete<FileDeleteResponse>("/api/v1/documents/delete", {
      data: payload,
      headers: { "Content-Type": "application/json" },
    });
    return data;
  },

  async getFileList(): Promise<DocumentsInfo[]> {
    const { data } = await API.get<DocumentsInfo[]>("/api/v1/documents/list");
    return data;
  },

  async listDialogs(): Promise<DialogInfo[]> {
    const { data } = await API.get<DialogInfo[]>("/api/v1/dialogs");
    return data;
  },

  async createDialog(title?: string, chatMode?: ChatMode): Promise<DialogInfo> {
    const { data } = await API.post<DialogInfo>("/api/v1/dialogs", { title, chat_mode: chatMode });
    return data;
  },

  async getDialogMessages(sessionId: string): Promise<DialogMessage[]> {
    const { data } = await API.get<DialogMessage[]>(`/api/v1/dialogs/${sessionId}/messages`);
    return data;
  },

  async deleteDialog(sessionId: string): Promise<{ success: boolean; message: string }> {
    const { data } = await API.delete<{ success: boolean; message: string }>(`/api/v1/dialogs/${sessionId}`);
    return data;
  },
};