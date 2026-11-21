import { onScopeDispose, ref, shallowRef } from 'vue'
import { isAbortError } from '@/api/client'

/** C06：取消或忽略过期请求，防止旧响应覆盖新条件 */
export type QueryStatus = 'idle' | 'loading' | 'success' | 'error'

export function useAsyncQuery<T>(loader: (signal: AbortSignal) => Promise<T>) {
  const status = ref<QueryStatus>('idle')
  const data = shallowRef<T | null>(null)
  const error = ref('')
  let controller: AbortController | null = null
  let ticket = 0

  async function run(): Promise<void> {
    controller?.abort()
    const current = new AbortController()
    controller = current
    ticket += 1
    const mine = ticket
    status.value = 'loading'
    error.value = ''
    try {
      const result = await loader(current.signal)
      if (mine !== ticket) return
      data.value = result
      status.value = 'success'
    } catch (caught) {
      if (isAbortError(caught) || mine !== ticket) return
      data.value = null
      error.value = caught instanceof Error ? caught.message : String(caught)
      status.value = 'error'
    }
  }

  onScopeDispose(() => controller?.abort())

  return { status, data, error, run }
}
