/**
 * Re-render math and chemistry formulas using MathJax
 */
export function typesetMath(element = null) {
  if (window.MathJax && window.MathJax.typesetPromise) {
    const target = element ? [element] : undefined
    window.MathJax.typesetPromise(target).catch((err) => {
      console.warn('MathJax typesetting error:', err)
    })
  }
}
