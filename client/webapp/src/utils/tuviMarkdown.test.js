import { describe, it, expect } from 'vitest'
import { renderMarkdown, escapeHtml } from './tuviMarkdown.js'

describe('tuviMarkdown.renderMarkdown — XSS safety (review 2026-06-21)', () => {
  it('escape thẻ HTML/script thô từ output LLM (không để tiêm script)', () => {
    const html = renderMarkdown('Xin chào <script>alert(1)</script> <img src=x onerror=alert(2)>')
    expect(html).not.toContain('<script>')
    expect(html).not.toContain('<img')
    expect(html).toContain('&lt;script&gt;')
  })

  it('vẫn render markdown cơ bản (## heading, **đậm**) thành thẻ an toàn', () => {
    const html = renderMarkdown('## Tiêu đề\n**đậm**')
    expect(html).toContain('<h4>Tiêu đề</h4>')
    expect(html).toContain('<strong>đậm</strong>')
  })

  it('null-safe (không ném khi text rỗng/null)', () => {
    expect(renderMarkdown(null)).toBe('')
    expect(renderMarkdown(undefined)).toBe('')
  })
})

describe('tuviMarkdown.escapeHtml', () => {
  it('escape &, <, >', () => {
    expect(escapeHtml('<a> & </a>')).toBe('&lt;a&gt; &amp; &lt;/a&gt;')
  })
})
