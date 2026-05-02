import api from './client'
import type { User } from '../types/domain'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export function register(username: string, password: string) {
  return api.post<User>('/auth/register', { username, password })
}

export function login(username: string, password: string) {
  return api.post<LoginResponse>('/auth/login', { username, password })
}

export function fetchMe() {
  return api.get<User>('/auth/me')
}
