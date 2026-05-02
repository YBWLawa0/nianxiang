import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

/** 将 Markdown 转为可安全用于 v-html 的 HTML（XSS 过滤） */
export function renderSafeMarkdown(source: string): string {
  const raw = source ?? ''
  if (!raw.trim()) return ''
  const html = marked.parse(raw, { async: false }) as string
  return DOMPurify.sanitize(html)
}
