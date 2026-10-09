import katex from 'katex'

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

/**
 * Render text containing LaTeX/KaTeX math formulas into HTML.
 * Supports:
 * - Block math: $$ ... $$ or \[ ... \]
 * - Inline math: $ ... $ or \( ... \)
 *
 * @param {string} content
 * @param {boolean} [allowHtml=false]
 */
export function renderFormula(content, allowHtml = false) {
  if (!content || typeof content !== 'string') return ''

  // If content already contains HTML markup (e.g. content_html from database), do not escape HTML tags
  const hasHtml = allowHtml || /<\/?[a-z][\s\S]*>/i.test(content)

  const placeholders = []

  // 1. Process block math: $$ ... $$ or \[ ... \]
  let text = content.replace(/\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]/g, (match, p1, p2) => {
    const tex = (p1 || p2 || '').trim()
    try {
      const rendered = katex.renderToString(tex, {
        displayMode: true,
        throwOnError: false,
      })
      const token = `__KATEX_BLOCK_${placeholders.length}__`
      placeholders.push({ token, rendered })
      return token
    } catch {
      return match
    }
  })

  // 2. Process inline math: $ ... $ or \( ... \)
  text = text.replace(/(?<!\\)\$([^\$\n]+?)(?<!\\)\$|\\\(([\s\S]*?)\\\)/g, (match, p1, p2) => {
    const tex = (p1 || p2 || '').trim()
    try {
      const rendered = katex.renderToString(tex, {
        displayMode: false,
        throwOnError: false,
      })
      const token = `__KATEX_INLINE_${placeholders.length}__`
      placeholders.push({ token, rendered })
      return token
    } catch {
      return match
    }
  })

  // 3. Only escape HTML & convert newlines if content is plain text (not already HTML markup)
  if (!hasHtml) {
    text = escapeHtml(text)
    text = text.replace(/\n/g, '<br>')
  }

  // 4. Restore rendered KaTeX HTML using function replacer to avoid special $ patterns
  placeholders.forEach(({ token, rendered }) => {
    text = text.replace(token, () => rendered)
  })

  return text
}
