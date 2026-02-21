import type {
  LoginPayload,
  SignupPayload,
  TokenResponse,
  User,
} from "../../types/user";
import { API_BASE_URL, parseJson } from "./api";

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJson<TokenResponse>(response);
}

export async function register(payload: SignupPayload): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJson<User>(response);
}
