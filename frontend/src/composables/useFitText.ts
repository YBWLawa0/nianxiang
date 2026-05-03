import {
  type Ref,
  onMounted,
  onBeforeUnmount,
  watch,
  nextTick,
} from 'vue'

/**
 * 在单行内优先通过缩小字号适应宽度；到达 minPx 仍溢出时再允许换行。
 */
export function useFitText(
  elRef: Ref<HTMLElement | null>,
  options?: {
    minPx?: number
    deps?: () => unknown[]
  }
) {
  const minPx = options?.minPx ?? 13

  async function fit() {
    const el = elRef.value
    if (!el) return
    el.style.fontSize = ''
    el.style.whiteSpace = 'nowrap'
    await nextTick()
    await new Promise<void>((r) =>
      requestAnimationFrame(() => requestAnimationFrame(() => r()))
    )
    const maxPx = parseFloat(getComputedStyle(el).fontSize)
    let size = maxPx
    while (size > minPx && el.scrollWidth > el.clientWidth + 1) {
      size -= 0.25
      el.style.fontSize = `${size}px`
    }
    if (el.scrollWidth > el.clientWidth + 1) {
      el.style.whiteSpace = 'normal'
      el.style.fontSize = `${minPx}px`
    }
  }

  let ro: ResizeObserver | null = null

  onMounted(() => {
    void fit()
    ro = new ResizeObserver(() => {
      void fit()
    })
    const el = elRef.value
    if (el) {
      ro.observe(el)
      if (el.parentElement) ro.observe(el.parentElement)
    }
  })

  if (options?.deps) {
    watch(options.deps, () => void fit(), { flush: 'post' })
  }

  onBeforeUnmount(() => {
    ro?.disconnect()
    ro = null
  })
}
