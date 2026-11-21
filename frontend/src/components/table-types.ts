/** 数据表列定义：对齐方式决定数值列是否右对齐（等宽数字） */
export interface DataTableColumn {
  key: string
  label: string
  align?: 'left' | 'right'
  width?: string
}
