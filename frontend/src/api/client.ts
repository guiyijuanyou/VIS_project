import { handleMockRequest } from '@/mock/handlers'
import type { ApiErrorBody } from './error'

/**
 * 统一请求层（人员三 C02 的核心交付：单一请求层 + mock/real 切换）。
 *
 * 规则：
 * 1. 所有页面只能通过 endpoints.ts 访问数据，禁止组件内直接 fetch。
 * 2. mock 与 real 由 VITE_API_MODE 决定；real 失败时**直接报错**，
 *    绝不自动回落到模拟数据（分工文件：真实接口失败不得自动展示模拟结果）。
 * 3. 请求可取消：视图条件变化时取消上一次请求，防止旧响应覆盖新条件。
 */

export type ApiMode = 'mock' | 'real'

const rawMode = import.meta.env.VITE_API_MODE ?? 'mock'
export const API_MODE: ApiMode = rawMode === 'real' ? 'real' : 'mock'
export const API_BASE = (import.meta.env.VITE_API_BASE ?? '/api/v1').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number
  readonly code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export type QueryParams = Record<string, string | number | boolean | null | undefined | string[]>

function buildSearchParams(params?: QueryParams): string {
  const search = new URLSearchParams()
  if (!params) return ''
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === '') continue
    if (Array.isArray(value)) {
      // 同字段多值：重复键，保持顺序，前端不拼接分隔符（待与 B 确认，见 request_contract_notes）
      for (const item of value) if (item !== '') search.append(key, item)
    } else {
      search.append(key, String(value))
    }
  }
  const text = search.toString()
  return text ? `?${text}` : ''
}

export async function apiGet<T>(path: string, params?: QueryParams, signal?: AbortSignal): Promise<T> {
  if (!path.startsWith('/')) throw new ApiError(0, 'BAD_PATH', `接口路径必须以 / 开头：${path}`)

  if (API_MODE === 'mock') {
    return await handleMockRequest<T>(path, params, signal)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}${buildSearchParams(params)}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new ApiError(0, 'NETWORK_ERROR', `无法连接后端 ${API_BASE}：请确认服务已启动或改用 mock 模式`)
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null
    try {
      body = (await response.json()) as ApiErrorBody
    } catch {
      body = null
    }
    throw new ApiError(
      response.status,
      body?.code ?? `HTTP_${response.status}`,
      body?.message ?? `接口 ${path} 返回 ${response.status}`,
    )
  }

  return (await response.json()) as T
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}
