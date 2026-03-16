import { createContext, useCallback, useContext, useMemo, useState } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const remove = useCallback((id) => {
    setToasts((prev) => (prev || []).filter((t) => t.id !== id))
  }, [])

  const push = useCallback((toast) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
    const next = {
      id,
      title: toast?.title || '',
      description: toast?.description || '',
      variant: toast?.variant || 'default', // default | success | error | warning
      durationMs: typeof toast?.durationMs === 'number' ? toast.durationMs : 3500,
    }
    setToasts((prev) => [...(prev || []), next])
    if (next.durationMs > 0) {
      window.setTimeout(() => remove(id), next.durationMs)
    }
    return id
  }, [remove])

  const api = useMemo(() => {
    return {
      toast: push,
      success: (title, description) => push({ variant: 'success', title, description }),
      error: (title, description) => push({ variant: 'error', title, description }),
      warning: (title, description) => push({ variant: 'warning', title, description }),
      info: (title, description) => push({ variant: 'default', title, description }),
      remove,
    }
  }, [push, remove])

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed bottom-4 right-4 z-[60] flex w-[92vw] max-w-sm flex-col gap-2">
        {(toasts || []).map((t) => {
          const tone =
            t.variant === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-950'
              : t.variant === 'error'
                ? 'border-rose-200 bg-rose-50 text-rose-950'
                : t.variant === 'warning'
                  ? 'border-amber-200 bg-amber-50 text-amber-950'
                  : 'border-slate-200 bg-white text-slate-950'

          return (
            <div
              key={t.id}
              className={`rounded-xl border p-3 shadow-lg shadow-slate-200/60 backdrop-blur ${tone}`}
              role="status"
              aria-live="polite"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  {t.title ? <div className="text-sm font-semibold truncate">{t.title}</div> : null}
                  {t.description ? <div className="mt-0.5 text-sm opacity-90">{t.description}</div> : null}
                </div>
                <button
                  type="button"
                  onClick={() => remove(t.id)}
                  className="shrink-0 rounded-md px-2 py-1 text-xs font-medium hover:bg-black/5"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
