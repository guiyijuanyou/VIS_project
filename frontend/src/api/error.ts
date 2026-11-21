/** 后端错误响应体（待人员二 B03 的 docs/api/contract.md 确认，见 request_contract_notes） */
export interface ApiErrorBody {
  code: string
  message: string
  detail?: string
}
