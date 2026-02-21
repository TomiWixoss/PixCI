'use client'

import { Toaster } from 'react-hot-toast'

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        icon: null,
        style: {
          background: 'var(--panel-bg)',
          color: 'var(--text-color)',
          border: '4px solid var(--text-color)',
          borderRadius: '0',
          boxShadow: '4px 4px 0px 0px var(--accent-purple)',
          fontWeight: 'bold',
          fontSize: '14px',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        },
        success: {
          duration: 3000,
          style: {
            boxShadow: '4px 4px 0px 0px var(--accent-yellow)',
            borderColor: 'var(--text-color)',
          },
        },
        error: {
          duration: 5000,
          style: {
            boxShadow: '4px 4px 0px 0px var(--accent-pink)',
            borderColor: 'var(--accent-pink)',
          },
        },
      }}
    />
  )
}
