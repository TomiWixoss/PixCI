'use client'

import { useState, FormEvent, useRef, useEffect } from 'react'
import { PixelStar } from './svgs/PixelStar'

interface FloatingInputProps {
  onSubmit: (prompt: string) => void
  isProcessing: boolean
}

export function FloatingInput({ onSubmit, isProcessing }: FloatingInputProps) {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => { inputRef.current?.focus() }, [])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (value.trim() && !isProcessing) {
      onSubmit(value.trim())
      setValue('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="art-canvas flex items-center w-full bg-white p-2 rounded-full">
      <div className="flex-shrink-0 pl-4 pr-2">
        <PixelStar className={`w-8 h-8 ${isProcessing ? 'text-[var(--text-color)] animate-spin' : 'text-[var(--accent-purple)]'}`} />
      </div>
      
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={isProcessing}
        placeholder={isProcessing ? "Hệ thống đang xử lý..." : "Chuyển màu, thêm chi tiết, thay đổi nền..."}
        className="flex-1 bg-transparent border-none outline-none text-base sm:text-lg font-bold placeholder:text-[var(--text-color)]/30 disabled:opacity-50 text-[var(--text-color)] px-4"
      />
      
      <button
        type="submit"
        disabled={!value.trim() || isProcessing}
        className={`
          h-12 px-8 font-bold text-sm uppercase tracking-widest rounded-full border-4 border-[var(--text-color)] transition-transform
          ${(!value.trim() || isProcessing) 
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
            : 'bg-[var(--accent-yellow)] text-[var(--text-color)] hover:-translate-y-1 active:translate-y-1 shadow-[0_4px_0_var(--text-color)]'}
        `}
      >
        Hô Biến!
      </button>
    </form>
  )
}
